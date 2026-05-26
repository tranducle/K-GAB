import json
import os
import time
import argparse
import requests
import yaml
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Load-balanced OpenRouter API keys from the model registry
OPENROUTER_KEYS = [
    "sk-REDACTED-v1-REDACTED",
    "sk-REDACTED-v1-REDACTED",
    "sk-REDACTED-v1-REDACTED"
]

def get_judge_configs(models_arg, urls_arg, keys_arg):
    models = [m.strip() for m in models_arg.split(",")]
    urls = [u.strip() for u in urls_arg.split(",")] if urls_arg else ["https://openrouter.ai/api/v1/chat/completions"] * len(models)
    
    if len(urls) == 1 and len(models) > 1:
        urls = urls * len(models)
        
    keys = []
    if keys_arg:
        key_groups = keys_arg.split(";") # semi-colon separated for different models, comma for load balancing
        for kg in key_groups:
            keys.append([k.strip() for k in kg.split(",")])
    else:
        keys = [OPENROUTER_KEYS] * len(models)
        
    if len(keys) == 1 and len(models) > 1:
        keys = keys * len(models)
        
    configs = []
    for i in range(len(models)):
        configs.append({
            "model_id": models[i],
            "base_url": urls[i],
            "api_keys": keys[i]
        })
    return configs

def call_llm_judge(model_id, base_url, api_keys, system_prompt, user_prompt, max_retries=5):
    headers = {
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/K-GAB",
        "X-Title": "K-GAB Benchmark"
    }
    
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0, # Zero temperature for deterministic judging
    }
    
    # Exponential backoff retry logic for 429 and other transient errors
    for attempt in range(max_retries):
        api_key = random.choice(api_keys)
        headers["Authorization"] = f"Bearer {api_key}"
        
        try:
            res = requests.post(base_url, headers=headers, json=payload, timeout=90)
            if res.status_code == 429:
                time.sleep((attempt + 1) * 3)
                continue
            if res.status_code != 200:
                return {"error": f"HTTP {res.status_code}: {res.text}"}
            
            data = res.json()
            return {"text": data['choices'][0]['message']['content']}
        except Exception as e:
            time.sleep((attempt + 1) * 2)
            
    return {"error": "Failed after max retries"}

def score_worker(task_args):
    record = task_args['record']
    target_spec = task_args['target_spec']
    system_prompt = task_args['system_prompt']
    dry_run = task_args['dry_run']
    judge_configs = task_args['judge_configs']
    
    run_id = record.get('run_id')
    
    if 'error' in record and record['error']:
        # If generation failed, score is automatically 0
        score = {"formula_acc": 0, "distractor_plaus": 0, "format_ok": 0, "justification": "Generation failed: " + str(record['error'])}
        record['score'] = score
        return record
        
    response_text = record.get('response', '')
    
    user_prompt = f"""Target Topic: {target_spec['topic']}
Grade: {target_spec['grade']}
Formula Expected: {target_spec.get('physical_law_formula', 'N/A')}

Generated Question:
{response_text}"""
    
    if dry_run:
        score = {"formula_acc": 1.0, "distractor_plaus": 1.0, "format_ok": 1.0, "justification": "Mock score"}
        time.sleep(0.05)
    else:
        results = []
        for config in judge_configs:
            res = call_llm_judge(
                model_id=config["model_id"],
                base_url=config["base_url"],
                api_keys=config["api_keys"],
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            if "error" in res:
                results.append({"formula_acc": 0, "distractor_plaus": 0, "format_ok": 0, "justification": f"Judge error: {res['error']}"})
            else:
                try:
                    txt = res['text'].replace("```json", "").replace("```", "").strip()
                    s = json.loads(txt)
                    results.append({
                        "formula_acc": float(s.get("formula_acc", 0)),
                        "distractor_plaus": float(s.get("distractor_plaus", 0)),
                        "format_ok": float(s.get("format_ok", 0)),
                        "justification": s.get("justification", "")
                    })
                except Exception as e:
                    results.append({"formula_acc": 0, "distractor_plaus": 0, "format_ok": 0, "justification": f"Parse error from judge: {str(e)} | Raw: {res['text']}"})
        
        if not results:
             score = {"formula_acc": 0, "distractor_plaus": 0, "format_ok": 0, "justification": "No models configured."}
        else:
             # Ensemble averaging
             score = {
                 "formula_acc": sum(r["formula_acc"] for r in results) / len(results),
                 "distractor_plaus": sum(r["distractor_plaus"] for r in results) / len(results),
                 "format_ok": sum(r["format_ok"] for r in results) / len(results),
                 "justification": " | ".join(r["justification"] for r in results)
             }
    
    record['score'] = score
    return record

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-workers", type=int, default=20, help="Number of parallel scoring threads")
    parser.add_argument("--judge-models", type=str, default="inferstack/gpt-5.4,alibaba/qwen-3.6-plus", help="Comma-separated list of judge model IDs")
    parser.add_argument("--base-urls", type=str, default="", help="Comma-separated list of base URLs for models")
    parser.add_argument("--api-keys", type=str, default="", help="Semi-colon separated list of keys per model. Comma separated within groups.")
    args = parser.parse_args()
    
    judge_configs = get_judge_configs(args.judge_models, args.base_urls, args.api_keys)
    print(f"Using {len(judge_configs)} models for ensemble scoring:")
    for c in judge_configs:
        print(f"  - {c['model_id']} at {c['base_url']}")

    # Load targets
    run_manifest = yaml.safe_load(open("experiments/multillm_cleanroom/run_manifest.yaml", "r"))
    targets = {}
    with open(run_manifest['target_specs_path'], 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                t = json.loads(line)
                targets[t['target_id']] = t

    raw_outputs_file = "results/raw_outputs.jsonl"
    scored_outputs_file = "results/scored_outputs.jsonl"
    
    existing_scores = set()
    if os.path.exists(scored_outputs_file):
        with open(scored_outputs_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        existing_scores.add(record['run_id'])
                    except:
                        pass
                        
    print(f"Found {len(existing_scores)} existing scores.")
    
    system_prompt = """You are an expert Vietnamese physics teacher and academic evaluator acting as an LLM-as-a-Judge.
Your task is to evaluate physics multiple-choice questions generated by other AI models.
References validating this approach: Zheng et al., 2023 (Judging LLM-as-a-Judge); Wang et al., 2023 (PandaLM).

Evaluate the provided question on three binary dimensions (1 = Pass, 0 = Fail):
1. Formula Accuracy (formula_acc): Does the question correctly apply the underlying physics formula?
2. Distractor Plausibility (distractor_plaus): Are the distractors physically plausible and based on common student misconceptions?
3. Formatting (format_ok): Is it properly structured as a JSON with question, options, answer, explanation?

Output ONLY a JSON dictionary with keys "formula_acc", "distractor_plaus", "format_ok" and a "justification" string. Do not include markdown formatting blocks."""

    tasks_to_run = []
    
    if not os.path.exists(raw_outputs_file):
        print(f"Raw outputs file {raw_outputs_file} not found. Ensure experiment has run.")
        return

    with open(raw_outputs_file, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            if not line.strip(): continue
            record = json.loads(line)
            run_id = record.get('run_id')
            
            if not run_id or run_id in existing_scores:
                continue
                
            tasks_to_run.append({
                "record": record,
                "target_spec": targets[record['target_id']],
                "system_prompt": system_prompt,
                "dry_run": args.dry_run,
                "judge_configs": judge_configs
            })
            
    print(f"Remaining items to score: {len(tasks_to_run)}")
    
    if len(tasks_to_run) == 0:
        print("Nothing left to score.")
        return

    completed = len(existing_scores)
    total_calls = completed + len(tasks_to_run)
    
    lock = threading.Lock()
    
    with open(scored_outputs_file, 'a', encoding='utf-8') as f_out:
        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            future_to_run_id = {executor.submit(score_worker, t): t['record']['run_id'] for t in tasks_to_run}
            
            for future in as_completed(future_to_run_id):
                record = future.result()
                
                with lock:
                    f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    f_out.flush()
                    completed += 1
                    if completed % 50 == 0:
                        print(f"Scored {completed}/{total_calls} items.")
                        
    print(f"Scoring complete. Output saved to {scored_outputs_file}")

if __name__ == "__main__":
    main()
