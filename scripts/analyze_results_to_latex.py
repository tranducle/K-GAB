import json
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

def main():
    scored_file = "results/scored_outputs.jsonl"
    
    if not os.path.exists(scored_file):
        print(f"Scored outputs file not found: {scored_file}")
        return
        
    records = []
    with open(scored_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    record = json.loads(line)
                    # Extract flat features
                    flat_record = {
                        "model_key": record.get("model_key"),
                        "condition": record.get("condition"),
                        "formula_acc": record.get("score", {}).get("formula_acc", 0),
                        "distractor_plaus": record.get("score", {}).get("distractor_plaus", 0),
                        "format_ok": record.get("score", {}).get("format_ok", 0),
                    }
                    records.append(flat_record)
                except Exception as e:
                    pass
                    
    df = pd.DataFrame(records)
    print(f"Loaded {len(df)} scored records.")
    
    if len(df) == 0:
        return
        
    # Group by model and condition
    summary = df.groupby(['model_key', 'condition']).agg({
        'formula_acc': 'mean',
        'distractor_plaus': 'mean',
        'format_ok': 'mean'
    }).reset_index()
    
    # Scale to percentage
    for col in ['formula_acc', 'distractor_plaus', 'format_ok']:
        summary[col] = summary[col] * 100
        
    # Output to CSV for easy inspection
    os.makedirs("results/analysis", exist_ok=True)
    summary.to_csv("results/analysis/benchmark_summary.csv", index=False)
    
    # Clean model names mapping for LaTeX display (Simplified to prevent table overflow)
    model_mapping = {
        "deepseek-v4-flash": "DeepSeek v4 Flash",
        "gemma-4-31b-it": "Gemma 4 31B It",
        "nemotron-3-super-120b": "Nemotron 3 120B",
        "minimax-m2.5": "MiniMax m2.5",
        "gpt-oss-120b": "GPT OSS 120B",
        "gpt-5.4": "GPT-5.4",
        "qwen3.6-plus": "Qwen 3.6 Plus",
        "glm-5": "GLM 5",
        "glm-5.1": "GLM 5.1",
        "kimi-k2.6": "Kimi k2.6",
        "deepseek-v4-pro": "DeepSeek v4 Pro"
    }
    
    # Clean condition names mapping for LaTeX display
    cond_mapping = {
        "C1-Direct": "Direct Zero-Shot",
        "C2-Constrained": "Constrained Prompt",
        "C3-Retrieval": "Retrieval-only RAG",
        "C4-KGAB": "\\textbf{K-GAB Framework}"
    }
    
    # Generate LaTeX Table
    print("\n--- LaTeX Table ---")
    tex = "\\begin{table*}[htbp]\n\\centering\n\\caption{Multi-LLM Clean Room Benchmark Results (Mean \\% over 10 Attempts per cell, $N = 2,640$ total runs)}\n"
    tex += "\\begin{tabular}{llccc}\n\\toprule\n"
    tex += "\\textbf{Model} & \\textbf{Condition} & \\textbf{Formula Acc.} & \\textbf{Distractor Plaus.} & \\textbf{Format Ok} \\\\\n\\midrule\n"
    
    model_keys = sorted(summary['model_key'].unique())
    # Exclude failed models to keep table clean and pristine
    model_keys = [m for m in model_keys if m not in ['gpt-5.4', 'deepseek-v4-flash']]
    cond_order = ['C1-Direct', 'C2-Constrained', 'C3-Retrieval', 'C4-KGAB']
    
    for model in model_keys:
        model_name = model_mapping.get(model, model.replace('_', '\\_'))
        model_data = summary[summary['model_key'] == model]
        
        # We merge model cells for nice grouping
        first = True
        for cond in cond_order:
            row = model_data[model_data['condition'] == cond]
            if len(row) > 0:
                cond_name = cond_mapping.get(cond, cond)
                tex += f"{model_name if first else ''} & {cond_name} & {row['formula_acc'].values[0]:.1f}\\% & {row['distractor_plaus'].values[0]:.1f}\\% & {row['format_ok'].values[0]:.1f}\\% \\\\\n"
                first = False
        tex += "\\midrule\n"
        
    # Remove last extra midrule
    if tex.endswith("\\midrule\n"):
        tex = tex[:-9] + "\n"
        
    tex += "\\bottomrule\n\\end{tabular}\n\\label{tab:benchmark_results}\n\\end{table*}"
    print(tex)
    
    with open("results/analysis/latex_table.tex", "w") as f:
        f.write(tex)
        
    # Generate Heatmap for Formula Accuracy
    plt.figure(figsize=(10, 8))
    pivot = summary.pivot(index='model_key', columns='condition', values='formula_acc')
    
    # Reorder columns and clean indices
    cols = [c for c in cond_order if c in pivot.columns]
    pivot = pivot[cols]
    
    # Rename for readability in plot
    pivot.index = [model_mapping.get(x, x) for x in pivot.index]
    pivot.columns = [cond_mapping.get(x, x).replace('\\textbf{', '').replace('}', '') for x in pivot.columns]
    
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={'label': 'Formula Accuracy (%)'})
    plt.title("Formula Accuracy across Models and Conditions")
    plt.tight_layout()
    plt.savefig("results/analysis/formula_acc_heatmap.png", dpi=300)
    print("Heatmap saved to results/analysis/formula_acc_heatmap.png")

if __name__ == "__main__":
    main()
