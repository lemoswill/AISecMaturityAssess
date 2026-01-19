import json
import os

from modules import i18n

# Weighted Waves for Staged Assessment
def get_maturity_waves():
    return {
        1: i18n.t("maturity_foundation"),
        2: i18n.t("maturity_security"),
        3: i18n.t("maturity_ops")
    }

# NIST AI RMF Categories (Top Level)
def get_nist_functions():
    return {
        "GOVERN": i18n.t("nist_govern"),
        "MAP": i18n.t("nist_map"),
        "MEASURE": i18n.t("nist_measure"),
        "MANAGE": i18n.t("nist_manage"),
        "CSA_EXTRA": i18n.t("nist_csa")
    }

# Variable to hold the loaded data
ASSESSMENT_DATA = {}

# --- Scoping & Heuristics ---

# Classify CSA Domains into Scopes
# Keys match the 'domain' field in data.json
DOMAIN_SCOPES = {
    # Organization Level (Macro)
    "Governance, Risk and Compliance": ["org"],
    "Human Resources": ["org"],
    "Audit & Assurance": ["org", "project_cloud"], # Audits happen at both levels
    "Business Continuity Management and Operational Resilience": ["org", "project_cloud"],
    
    # Project Level - shared
    "Application & Interface Security": ["project_cloud", "project_saas"],
    "Data Security and Privacy Lifecycle Management": ["org", "project_cloud", "project_saas"], # Data policies are org, implementation is project
    "Identity & Access Management": ["project_cloud", "project_saas"],
    "Security Incident Management, E-Discovery, & Cloud Forensics": ["org", "project_cloud"],
    "Supply Chain Management, Transparency, and Accountability": ["org", "project_saas"], # SaaS is essentially supply chain risk
    "Threat & Vulnerability Management": ["project_cloud"],
    
    # Project Level - Cloud/Builder Only
    "Change Control and Configuration Management": ["project_cloud"],
    "Datacenter Security": ["project_cloud"], # Renamed in UI Level usually
    "Infrastructure Security": ["project_cloud"],
    "Logging and Monitoring": ["project_cloud", "project_saas"], # SaaS logs are important too
    "Model Security": ["project_cloud"], # If consuming SaaS, you rarely secure the model itself
    "Universal Endpoint Management": ["project_cloud", "org"]
}

DEFAULT_PROJECT_TYPE = "project_cloud"

def load_data():
    global ASSESSMENT_DATA
    # Look for data.json in CWD or parent of modules
    paths = [
        "data.json",
        os.path.join(os.path.dirname(__file__), "..", "data.json")
    ]
    
    loaded = False
    
    # Decide which file to load based on language
    lang = i18n.get_lang()
    data_file = "data_pt.json" if lang == "pt" else "data.json"
    
    paths = [
        data_file,
        os.path.join(os.path.dirname(__file__), "..", data_file),
        "data.json", # Fallback
        os.path.join(os.path.dirname(__file__), "..", "data.json")
    ]
    
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ASSESSMENT_DATA = data # Overwrite instead of update for clean switch
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

# Track current loaded language
CURRENT_LOADED_LANG = None

def get_controls_for_scope(scope="org", project_type="cloud"):
    """
    Returns a filtered view of ASSESSMENT_DATA based on scope.
    Now reacts to language changes by reloading data if necessary.
    """
    global CURRENT_LOADED_LANG
    
    # Check if we need to reload due to language change
    if i18n.get_lang() != CURRENT_LOADED_LANG:
        load_data()
        CURRENT_LOADED_LANG = i18n.get_lang()
        
    target_tag = "org"
    if scope == "project":
        target_tag = f"project_{project_type}"
        
    filtered_data = {}
    
    for func, subcats in ASSESSMENT_DATA.items():
        filtered_subcats = {}
        for subcat_key, subcat_val in subcats.items():
            
            # Filter controls within this subcategory
            original_controls = subcat_val.get('csa_controls', [])
            valid_controls = []
            
            for c in original_controls:
                domain = c.get('domain', '')
                allowed_tags = DOMAIN_SCOPES.get(domain, ["org", "project_cloud", "project_saas"]) # Default to all if unknown
                
                # Logic:
                # 1. If target is 'org', allow if 'org' in tags.
                # 2. If target is 'project_cloud', allow if 'project_cloud' in tags.
                # 3. If target is 'project_saas', allow if 'project_saas' in tags.
                
                # Special Handling for SaaS vs Cloud nuances even if domain matches
                if target_tag == "project_saas" and domain == "Datacenter Security":
                    continue # Hard exclude physical for SaaS
                    
                if target_tag in allowed_tags:
                    valid_controls.append(c)
            
            if valid_controls:
                # Create copy of subcat with filtered controls
                new_subcat = subcat_val.copy()
                new_subcat['csa_controls'] = valid_controls
                filtered_subcats[subcat_key] = new_subcat
        
        if filtered_subcats:
            filtered_data[func] = filtered_subcats
            
    return filtered_data
