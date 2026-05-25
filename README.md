# K-GAB: Knowledge Graph-Guided Assessment Builder for High School Physics

This repository contains the anonymized replication package, datasets, and core implementation code for **K-GAB** (Knowledge Graph-Guided Assessment Builder), a neuro-symbolic framework designed to generate high-rigor, curriculum-aligned, and psychometrically balanced assessment items for high school physics.

---

## 📌 Overview

Traditional Generative AI approaches in educational assessment often suffer from physical hallucinations, dimensional inconsistencies, and lack of alignment with formal pedagogical standards. **K-GAB** solves this by coupling:
1. **Pedagogical Graph-RAG Layer**: A Neo4j knowledge graph encoding the official Vietnamese Ministry of Education and Training (MOET) high school physics curriculum standard (GDPT 2018).
2. **Deterministic Symbolic CAS Engine**: Translates curriculum formulas into computer algebra systems (SymPy/Sage) to dynamically compute exact answers and diagnostic misconception distractors.
3. **Neural LLM Generator**: Bounded by rigorous prompt envelopes compiled programmatically from the graph and symbolic locks.

---

## 📂 Repository Structure

```directory
├── cypher/
│   └── import_ontology.cypher              # Neo4j Cypher query to import the curriculum ontology
├── data/
│   ├── curriculum_ontology.json            # Anonymized Vietnamese High School Physics curriculum standard dataset
│   └── evaluation_locked/                  # Locked empirical evaluation and psychometric results
│       ├── generated_items_matrix.json     # Sample K-GAB generated physics items
│       ├── irt_parameters_fitted.json      # Fitted 3PL IRT parameters (a, b, c) for generated items
│       ├── national_correlation_results.json# Regional correlation fit results (Urban vs. Rural vs. National)
│       └── *.png / *.pdf                   # Generated vector charts and empirical calibration plots
├── verify_contribution_architecture.py     # Python script verifying symbolic graph-guidance constraints
└── verify_experiment_architecture_completeness.py # Python script verifying experimental metric completeness
```

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Neo4j Database (optional, for deploying the knowledge graph)

### Setup Codebase
Clone this repository and install dependencies:
```bash
git clone https://github.com/tranducle/K-GAB.git
cd K-GAB
pip install -r requirements.txt # standard scientific libraries: numpy, pandas, matplotlib, networkx
```

---

## 🚀 Usage

### 1. Importing the Curriculum Ontology into Neo4j
Ensure you have a running Neo4j instance. Open the browser or `cypher-shell` and run the script inside `cypher/import_ontology.cypher` to initialize the high school physics nodes, cognitive skill hierarchies, and physical system parameters:
```bash
cat cypher/import_ontology.cypher | cypher-shell -u neo4j -p <your_password>
```

### 2. Verifying the Graph-Guidance Constraints
To verify that K-GAB programmatically enforces semantic constraints (such as physical answer bounds and misconception slip tracking), execute:
```bash
python3 verify_contribution_architecture.py
```
This script audits the graph's constraint ledger to ensure that no item is generated without symbolic CAS validation blocks.

### 3. Verifying Experimental Metric Completeness
To ensure that all empirical metrics reported in the manuscript (such as Fleiss' Kappa, Mantel-Haenszel DIF, and Pearson correlations) are fully reproducible and valid, run:
```bash
python3 verify_experiment_architecture_completeness.py
```

---

## 🔒 Double-Blind Peer Review Statement

To comply with the double-blind peer review policy of Taylor & Francis journals, all institutional markers, author names, provincial identifiers, and university affiliations have been strictly removed or masked from the codebases, datasets, and figures in this repository. 

---

## 📧 Contact & Citation

For questions regarding the knowledge graph schema or replication dataset, please contact the corresponding author as specified in the published paper. 
