#!/usr/bin/env python3
"""
Verification Script for K-GAB Experiment Planning Assets.
Audits the presence, completeness, JSON syntax, and placeholder status of all files.
"""

import os
import json
import re
import sys

# Directory Setup
WORK_DIR = "/Users/let/Documents/DO_A_PAPER_May_18/Papers/HONGPHYSIC/gap_to_idea_workspace"
OUTPUT_DIR = os.path.join(WORK_DIR, "experiment_plan_output")

REQUIRED_MD_FILES = [
    "EXPERIMENT_CONTEXT_INVENTORY.md",
    "MANUSCRIPT_EXPERIMENT_CONTEXT.md",
    "EXISTING_EXPERIMENT_AUDIT.md",
    "CLAIM_RQ_EVIDENCE_CONTRACT.md",
    "DATASET_DISCOVERY_AND_FIT_REGISTER.md",
    "DATASET_ACQUISITION_AND_ACCESS_PLAN.md",
    "BASELINE_BENCHMARK_SELECTION_PLAN.md",
    "ACADEMIC_SOURCE_SUPPORT_PLAN.md",
    "COMPLETE_EXPERIMENT_PLAN.md",
    "EXPERIMENT_DESIGN_MATRIX.md",
    "METRICS_AND_STATISTICAL_VALIDATION_PLAN.md",
    "ABLATION_SENSITIVITY_ROBUSTNESS_PLAN.md",
    "FAILURE_MODE_AND_NEGATIVE_RESULT_PLAN.md",
    "VALIDITY_THREATS_AND_MITIGATION_PLAN.md",
    "EXPECTED_TABLE_FIGURE_PLAN.md",
    "REVIEWER_EXPERIMENT_RISK_CLOSURE_MATRIX.md",
    "PRE_REVIEW_EXPERIMENT_COMPLETENESS_AUDIT.md",
    "EXECUTION_DEPENDENCY_AND_RESOURCE_PLAN.md",
    "EXPERIMENT_DESIGN_DEFENSE_DOSSIER.md",
    "PILOT_AND_POWER_ANALYSIS_PLAN.md",
    "BASELINE_FAIRNESS_AND_TUNING_PROTOCOL.md",
    "DATA_SPLIT_LEAKAGE_AND_CONTAMINATION_CHECK.md",
    "EXPERIMENT_STOPPING_AND_DECISION_RULES.md",
    "SEQUENTIAL_EXECUTION_AND_REVIEW_CHECKPOINTS.md",
    "EXPERIMENT_DESIGN_DEFENSE_REPORT.md",
    "PLAN_REVIEW_AND_GAP_CLOSURE_REPORT.md",
    "EXPERIMENT_COMPLETENESS_SCORECARD.md",
    "EXPERIMENT_READINESS_BOARD.md",
    "ADVERSARIAL_EXPERIMENT_PREMORTEM.md",
    "BACKUP_AND_CONTINGENCY_EXPERIMENT_PLAN.md",
    "FINAL_EXECUTION_GO_NO_GO_RECORD.md",
    "EXPERIMENT_EXECUTION_QUEUE.md",
    "REPRODUCIBILITY_ARTIFACT_PLAN.md"
]

REQUIRED_JSON_FILES = [
    "claim_rq_evidence_contract.json",
    "dataset_discovery_register.json",
    "experiment_design_matrix.json",
    "experiment_design_defense.json",
    "plan_review_gate.json",
    "experiment_completeness_scorecard.json",
    "experiment_readiness_board.json",
    "final_execution_gate.json"
]

def main():
    print("=== STARTING K-GAB EXPERIMENT PLANNING COMPLETENESS AUDIT ===")
    errors = 0
    warnings = 0

    # 1. Check Directory Existence
    if not os.path.exists(OUTPUT_DIR):
        print(f"[ERROR] Output directory not found: {OUTPUT_DIR}")
        sys.exit(1)

    # 2. Check Required Markdown Files
    for filename in REQUIRED_MD_FILES:
        filepath = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(filepath):
            print(f"[ERROR] Required markdown file missing: {filename}")
            errors += 1
            continue

        size = os.path.getsize(filepath)
        if size == 0:
            print(f"[ERROR] Markdown file is empty: {filename}")
            errors += 1
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for placeholders
        placeholders = re.findall(r"(TODO|FIXME|\[Insert.*?\]|\btemp\b)", content, re.IGNORECASE)
        if placeholders:
            print(f"[WARNING] Placeholders found in {filename}: {set(placeholders)}")
            warnings += 1

    # 3. Check Required JSON Files
    for filename in REQUIRED_JSON_FILES:
        filepath = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(filepath):
            print(f"[ERROR] Required JSON file missing: {filename}")
            errors += 1
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Basic structural assertion
            if not isinstance(data, dict):
                print(f"[ERROR] JSON root is not an object: {filename}")
                errors += 1
        except Exception as e:
            print(f"[ERROR] Failed to parse JSON file {filename}: {e}")
            errors += 1

    # Summary
    print("\n=== AUDIT SUMMARY ===")
    print(f"Total Errors: {errors}")
    print(f"Total Warnings: {warnings}")

    if errors > 0:
        print("[FAIL] Experiment Planning Audit failed due to errors.")
        sys.exit(1)
    else:
        print("[PASS] Experiment Planning Audit completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
