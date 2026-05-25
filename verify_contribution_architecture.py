#!/usr/bin/env python3
"""
Verification Script for K-GAB Contribution Architecture Assets.
Audits the presence, completeness, Socratic counts, and placeholder status of all files.
"""

import os
import json
import re
import sys

# Directory Setup
WORK_DIR = "/Users/let/Documents/DO_A_PAPER_May_18/Papers/HONGPHYSIC/gap_to_idea_workspace"
OUTPUT_DIR = os.path.join(WORK_DIR, "contribution_architect_output")

REQUIRED_MD_FILES = [
    "TARGET_JOURNAL_AND_SCOPE.md",
    "MANUSCRIPT_CONTEXT_SUMMARY.md",
    "LITERATURE_HUNTER_BRIEF.md",
    "JOURNAL_PROFILE_AND_PATTERN_MAP.md",
    "HOT_TOPIC_AND_GAP_MAP.md",
    "CONTRIBUTION_CANDIDATE_REGISTER.md",
    "SOCRATIC_QUESTION_LOG.md",
    "CONTRIBUTION_EVOLUTION_TRACE.md",
    "PROPOSED_MODEL_METHOD_BLUEPRINT.md",
    "EXPERIMENT_EVIDENCE_BLUEPRINT.md",
    "TOP_TIER_REVIEWER_ATTACK_REPORT.md",
    "TOP_JOURNAL_FIT_SCORECARD.md",
    "MANUSCRIPT_UPGRADE_ROADMAP.md",
    "FINAL_RECOMMENDATION.md"
]

def main():
    print("=== STARTING K-GAB CONTRIBUTION ARCHITECTURE AUDIT ===")
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

    # 3. Verify contribution_candidate_register.json
    json_path = os.path.join(OUTPUT_DIR, "contribution_candidate_register.json")
    if not os.path.exists(json_path):
        print("[ERROR] JSON candidate register missing!")
        errors += 1
    else:
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "candidates" not in data or not isinstance(data["candidates"], list):
                print("[ERROR] JSON format invalid: 'candidates' list missing.")
                errors += 1
            else:
                promoted = [c for c in data["candidates"] if c["status"] == "promoted"]
                print(f"[INFO] Parsed JSON register: {len(data['candidates'])} candidates, {len(promoted)} promoted.")
                if len(promoted) != 4:
                    print(f"[ERROR] Expected exactly 4 promoted candidates, found {len(promoted)}.")
                    errors += 1
        except Exception as e:
            print(f"[ERROR] Failed to parse JSON register: {e}")
            errors += 1

    # 4. Check Socratic Question Counts
    socratic_path = os.path.join(OUTPUT_DIR, "SOCRATIC_QUESTION_LOG.md")
    if os.path.exists(socratic_path):
        with open(socratic_path, "r", encoding="utf-8") as f:
            content = f.read()
        questions = re.findall(r"### Q\d+:", content)
        print(f"[INFO] Found {len(questions)} Socratic questions in SOCRATIC_QUESTION_LOG.md.")
        if len(questions) < 50:
            print(f"[ERROR] Expected at least 50 Socratic questions, found {len(questions)}.")
            errors += 1

    # 5. Check Mathematical Rigor
    blueprint_path = os.path.join(OUTPUT_DIR, "EXPERIMENT_EVIDENCE_BLUEPRINT.md")
    if os.path.exists(blueprint_path):
        with open(blueprint_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Verify 3PL IRT Equation is present
        if "P_{j}(\\theta_i)" not in content and "3PL" not in content:
            print("[ERROR] IRT 3PL mathematical equations missing from blueprint!")
            errors += 1

    # Summary
    print("\n=== AUDIT SUMMARY ===")
    print(f"Total Errors: {errors}")
    print(f"Total Warnings: {warnings}")

    if errors > 0:
        print("[FAIL] Audit failed due to errors.")
        sys.exit(1)
    else:
        print("[PASS] Contribution Architecture Audit completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
