import sys
import os

# Ensure we can import from modules
sys.path.append(os.getcwd())

from modules import data

def test_scope(scope, project_type, label):
    print(f"\n--- Testing: {label} ({scope}/{project_type}) ---")
    controls = data.get_controls_for_scope(scope, project_type)
    
    # Check key categories
    categories_present = list(controls.keys())
    # print(f"Categories: {categories_present}")
    
    # Check specific sub-domain visibility
    # We need to look deeper into the subcats to find the controls and check their domain
    domains_found = set()
    total_count = 0
    
    for func in controls:
        for subcat in controls[func]:
            for c in controls[func][subcat]['csa_controls']:
                domains_found.add(c.get('domain'))
                total_count += 1
                
    print(f"Total Controls: {total_count}")
    
    # Assertions based on rules
    if scope == 'org':
        if "Governance, Risk and Compliance" in domains_found:
            print("[OK] Governance present (Expected for Org)")
        else:
            print("[FAIL] Governance MISSING")
            
        if "Datacenter Security" not in domains_found:
            print("[OK] Datacenter Security hidden (Expected for Org)")
        else:
            print("[FAIL] Datacenter Security PRESENT (Should be hidden)")

    if scope == 'project' and project_type == 'cloud':
        if "Infrastructure Security" in domains_found:
            print("[OK] Infrastructure Security present (Expected for Cloud Project)")
        else:
            print("[FAIL] Infrastructure Security MISSING")

    if scope == 'project' and project_type == 'saas':
        if "Datacenter Security" not in domains_found:
            print("[OK] Datacenter Security hidden (Expected for SaaS Project)")
        else:
            print("[FAIL] Datacenter Security PRESENT (Should be hidden)")
            
        if "Supply Chain Management, Transparency, and Accountability" in domains_found:
            print("[OK] Supply Chain present (Expected for SaaS)")
        else:
             print("[FAIL] Supply Chain MISSING")

if __name__ == "__main__":
    print("Initializing Data...")
    # data.load_data() # Already called on import
    
    test_scope("org", "none", "Organization Macro")
    test_scope("project", "cloud", "Project Cloud (Micro)")
    test_scope("project", "saas", "Project SaaS (Consumer)")
