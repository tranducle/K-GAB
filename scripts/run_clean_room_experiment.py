import yaml
import json
import os
import time
import argparse
import requests
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def load_jsonl(path):
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def load_prompt_template(path):
    if not os.path.exists(path):
        return "Generate a physics question about {topic} for grade {grade}."
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def call_llm_api(model_id, base_url, api_keys, system_prompt, user_prompt, settings, max_retries=5):
    headers = {
        "Content-Type": "application/json"
    }
    
    if "openrouter.ai" in base_url:
        headers["HTTP-Referer"] = "https://github.com/K-GAB"
        headers["X-Title"] = "K-GAB Benchmark"
    
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": settings.get("temperature", 0.2),
        "top_p": settings.get("top_p", 0.95),
        "max_tokens": settings.get("max_tokens", 2048)
    }
    
    start_time = time.time()
    
    for attempt in range(max_retries):
        api_key = random.choice(api_keys)
        headers["Authorization"] = f"Bearer {api_key}"
        
        try:
            response = requests.post(base_url, headers=headers, json=payload, timeout=90)
            
            if response.status_code == 429:
                # Rate limit, backoff and retry
                time.sleep((attempt + 1) * 4)
                continue
                
            if response.status_code != 200:
                latency = (time.time() - start_time) * 1000
                return {"error": f"HTTP {response.status_code}: {response.text}", "latency_ms": latency, "cost": 0.0}
                
            data = response.json()
            
            if 'choices' not in data or len(data['choices']) == 0:
                latency = (time.time() - start_time) * 1000
                return {"error": "Invalid API response structure", "latency_ms": latency, "cost": 0.0, "raw": data}
                
            text = data['choices'][0]['message']['content']
            latency = (time.time() - start_time) * 1000
            
            return {
                "text": text,
                "latency_ms": latency,
                "cost": 0.0,
                "raw_response": data
            }
        except Exception as e:
            if attempt == max_retries - 1:
                latency = (time.time() - start_time) * 1000
                return {"error": str(e), "latency_ms": latency, "cost": 0.0}
            time.sleep((attempt + 1) * 3)
            
    latency = (time.time() - start_time) * 1000
    return {"error": "Max retries exceeded (likely 429 rate limits)", "latency_ms": latency, "cost": 0.0}

def mock_llm_call(model_id, system_prompt, user_prompt, settings):
    time.sleep(random.uniform(0.1, 0.5)) # Mock processing time
    return {
        "text": f"[Mock generated response from {model_id} for prompt length {len(user_prompt)}]",
        "cost": 0.0,
        "latency_ms": 150,
        "raw_response": {}
    }

def worker_task(task_args):
    # Unpack
    run_id = task_args['run_id']
    target = task_args['target']
    model_key = task_args['model_key']
    model_id = task_args['model_id']
    base_url = task_args['base_url']
    api_keys = task_args['api_keys']
    settings = task_args['settings']
    cond_id = task_args['cond_id']
    repeat = task_args['repeat']
    system_prompt = task_args['system_prompt']
    user_prompt = task_args['user_prompt']
    dry_run = task_args['dry_run']
    
    try:
        if dry_run:
            result = mock_llm_call(model_id, system_prompt, user_prompt, settings)
        else:
            result = call_llm_api(model_id, base_url, api_keys, system_prompt, user_prompt, settings)
            
        record = {
            "run_id": run_id,
            "target_id": target["target_id"],
            "model_key": model_key,
            "model_id": model_id,
            "condition": cond_id,
            "repeat": repeat,
            "response": result.get("text", ""),
            "error": result.get("error", None),
            "cost": result.get("cost", 0.0),
            "latency_ms": result.get("latency_ms", 0.0),
            "timestamp": time.time()
        }
    except Exception as e:
        record = {
            "run_id": run_id,
            "error": str(e),
            "timestamp": time.time()
        }
        
    return record

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Run without calling actual APIs")
    parser.add_argument("--max-workers", type=int, default=15, help="Number of parallel threads")
    args = parser.parse_args()

    print("Loading manifests...")
    run_manifest = load_yaml("experiments/multillm_cleanroom/run_manifest.yaml")
    model_registry = load_yaml("experiments/multillm_cleanroom/model_registry.yaml")
    condition_manifest = load_yaml("experiments/multillm_cleanroom/condition_manifest.yaml")
    target_specs = load_jsonl(run_manifest['target_specs_path'])
    
    models_to_run = run_manifest['models']
    
    output_dir = run_manifest.get('output_dir', 'results')
    os.makedirs(output_dir, exist_ok=True)
    raw_outputs_file = os.path.join(output_dir, "raw_outputs.jsonl")
    
    conditions_to_run = run_manifest['conditions']
    repeats = run_manifest.get('repeats_per_cell', 1)
    
    print(f"Loaded {len(target_specs)} target specs.")
    print(f"Models: {models_to_run}")
    print(f"Conditions: {conditions_to_run}")
    
    total_calls = len(target_specs) * len(models_to_run) * len(conditions_to_run) * repeats
    print(f"Total planned API calls: {total_calls}")
    
    existing_runs = set()
    if os.path.exists(raw_outputs_file):
        with open(raw_outputs_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        existing_runs.add(record['run_id'])
                    except json.JSONDecodeError:
                        pass
    
    print(f"Found {len(existing_runs)} already completed runs. Resuming...")
    completed = len(existing_runs)
    
    # Build list of tasks
    tasks_to_run = []
    
    for target in target_specs:
        for model_key in models_to_run:
            model_info = model_registry['models'][model_key]
            model_id = model_info['model_id']
            base_url = model_info['base_url']
            api_keys = model_info['api_keys']
            settings = model_info.get('decoding_settings', {})
            
            for cond_key in conditions_to_run:
                cond_info = condition_manifest['conditions'][cond_key]
                template_path = cond_info.get('prompt_template', '')
                template = load_prompt_template(template_path)
                
                for repeat in range(repeats):
                    run_id = f"20260526_{target['target_id']}_{model_key}_{cond_info['id']}_{repeat}"
                    
                    if run_id in existing_runs:
                        continue
                        
                    system_prompt = "You are a Vietnamese high-school physics teacher."
                    user_prompt = template.format(
                        topic=target['topic'],
                        grade=target['grade'],
                        formula=target.get('physical_law_formula', ''),
                        tier=target.get('cognitive_tier', '')
                    )
                    
                    task_args = {
                        "run_id": run_id,
                        "target": target,
                        "model_key": model_key,
                        "model_id": model_id,
                        "base_url": base_url,
                        "api_keys": api_keys,
                        "settings": settings,
                        "cond_id": cond_info['id'],
                        "repeat": repeat,
                        "system_prompt": system_prompt,
                        "user_prompt": user_prompt,
                        "dry_run": args.dry_run
                    }
                    tasks_to_run.append(task_args)

    print(f"Remaining tasks to execute: {len(tasks_to_run)} on {args.max_workers} threads")
    
    lock = threading.Lock()
    
    with open(raw_outputs_file, "a", encoding="utf-8") as f_out:
        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            # Submit all tasks
            future_to_run_id = {executor.submit(worker_task, t): t['run_id'] for t in tasks_to_run}
            
            for future in as_completed(future_to_run_id):
                record = future.result()
                
                with lock:
                    f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    f_out.flush()
                    completed += 1
                    if completed % 10 == 0:
                        print(f"Progress: {completed}/{total_calls}")

    print(f"Execution complete. Results saved to {raw_outputs_file}")

if __name__ == "__main__":
    main()
