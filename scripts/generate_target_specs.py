import json
import os
import hashlib

TARGET_FILE = "../data/target_specs/target_specs.jsonl"
os.makedirs(os.path.dirname(TARGET_FILE), exist_ok=True)

# Generate 60 physics curriculum targets for VNHSGE
topics = [
    ("Grade 10", "Kinematics", "PHYS-G10-KIN"),
    ("Grade 10", "Dynamics", "PHYS-G10-DYN"),
    ("Grade 10", "Work & Energy", "PHYS-G10-WEN"),
    ("Grade 11", "Electrostatics", "PHYS-G11-ELE"),
    ("Grade 11", "Electromagnetism", "PHYS-G11-MAG"),
    ("Grade 11", "Optics", "PHYS-G11-OPT"),
    ("Grade 12", "Mechanical Oscillations", "PHYS-G12-OSC"),
    ("Grade 12", "AC Circuits", "PHYS-G12-ACC"),
    ("Grade 12", "Quantum & Nuclear Physics", "PHYS-G12-NUC"),
    ("Grade 12", "Wave Optics", "PHYS-G12-WAV")
]

target_specs = []
id_counter = 1

for grade, topic_name, code_prefix in topics:
    for i in range(1, 7): # 6 targets per topic = 60 targets total
        target_id = f"{code_prefix}-{i:02d}"
        
        # Determine cognitive tier
        if i <= 2:
            tier = "Recall / Comprehension (Level 1-2)"
        elif i <= 4:
            tier = "Application (Level 3)"
        else:
            tier = "High Application (Level 4)"
            
        spec = {
            "target_id": target_id,
            "source_file": "synthetic_curriculum_v1.pdf",
            "source_hash": hashlib.md5(target_id.encode()).hexdigest(),
            "grade": grade,
            "topic": topic_name,
            "curriculum_standard_code": target_id,
            "cognitive_tier": tier,
            "physical_law_formula": "Generic Formula for " + topic_name,
            "variables_and_ranges": {"var1": [0, 100], "var2": [0.1, 5.0]},
            "vietnamese_terminology_notes": f"Sử dụng thuật ngữ chuẩn SGK Vật lý {grade[-2:]}",
            "correct_answer_calculation_template": "var1 * var2",
            "misconception_slip_candidates": [
                {"slip_id": "M1", "formula": "var1 / var2", "description": "Inverse relationship error"},
                {"slip_id": "M2", "formula": "var1 + var2", "description": "Additive instead of multiplicative"},
                {"slip_id": "M3", "formula": "var1 * (var2^2)", "description": "Squared term hallucination"}
            ],
            "exclusion_criteria": "Avoid calculus-based derivations",
            "train_test_split": "main_in_domain" if i <= 5 else "heldout_topic"
        }
        target_specs.append(spec)

with open(TARGET_FILE, "w", encoding="utf-8") as f:
    for spec in target_specs:
        f.write(json.dumps(spec, ensure_ascii=False) + "\n")

print(f"Generated {len(target_specs)} target specs at {TARGET_FILE}")
