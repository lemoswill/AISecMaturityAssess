import json
import os

# Weighted Waves for Staged Assessment
# Defines labels and IDs (1, 2, 3)
MATURITY_WAVES = {
    1: "1. Foundation & Governance",
    2: "2. Security & Verification",
    3: "3. Operations & Optimization"
}

# NIST AI RMF Categories (Top Level)
NIST_FUNCTIONS = {
    "GOVERN": "Cultivate a culture of risk management.",
    "MAP": "Context recognized and risks identified.",
    "MEASURE": "Assessed, analyzed, and tracked.",
    "MANAGE": "Prioritize and act upon risks.",
    "CSA_EXTRA": "Additional CSA AICM requirements not directly mapped to NIST AI RMF."
}

# Variable to hold the loaded data
ASSESSMENT_DATA = {}

def load_data():
    global ASSESSMENT_DATA
    # Look for data.json in CWD or parent of modules
    # app.py runs from root, so data.json should be in CWD
    paths = [
        "data.json",
        os.path.join(os.path.dirname(__file__), "..", "data.json")
    ]
    
    loaded = False
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ASSESSMENT_DATA.update(data)
                loaded = True
                break
            except Exception as e:
                print(f"Error loading {p}: {e}")
    
    if not loaded:
        print("WARNING: data.json not found. Ensure ingest.py has been run.")

# Load on import
load_data()

def get_total_controls():
    count = 0
    for func in ASSESSMENT_DATA:
        for subcat in ASSESSMENT_DATA[func]:
            if 'csa_controls' in ASSESSMENT_DATA[func][subcat]:
                count += len(ASSESSMENT_DATA[func][subcat]['csa_controls'])
    return count
