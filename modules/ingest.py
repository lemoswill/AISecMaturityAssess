import pandas as pd
import json
import re
import os

NIST_CSV = "nist_ai_rmf_playbook.csv"
CSA_EXCEL = "AICMv1.0.3-generated_at_2025_11_10.xlsx"
OUTPUT_FILE = "data.json"

def normalize_nist_mapping(mapping_str):
    """
    Convert 'GV-1.1-001', 'GOVERN 1.1', 'MP-1.2' to 'GOVERN 1.1', 'MAP 1.2' etc.
    Returns a list of valid NIST Subcategories found.
    """
    if not isinstance(mapping_str, str):
        return []

    mappings = []
    
    # Split by newlines or commas
    tokens = re.split(r'[\n,]', mapping_str)
    
    for token in tokens:
        token = token.strip().upper()
        if not token:
            continue
            
        # Detect Function
        func = None
        if "GV" in token or "GOVERN" in token: func = "GOVERN"
        elif "MP" in token or "MAP" in token: func = "MAP"
        elif "MS" in token or "MEASURE" in token: func = "MEASURE"
        elif "MG" in token or "MANAGE" in token: func = "MANAGE"
        
        if func:
            # Extract Number X.Y
            # Regex to find X.Y (e.g., 1.1, 2.3)
            match = re.search(r'(\d+\.\d+)', token)
            if match:
                number = match.group(1)
                mappings.append(f"{func} {number}")
                
    return list(set(mappings))

def ingest():
    print("Starting ingestion...")
    
    # --- 1. Load NIST Structure (CSV) ---
    if not os.path.exists(NIST_CSV):
        print(f"Error: {NIST_CSV} not found.")
        return

    try:
        nist_df = pd.read_csv(NIST_CSV)
        print("NIST CSV loaded.")
    except Exception as e:
        print(f"Error reading {NIST_CSV}: {e}")
        return

    # Create Base Structure
    final_data = {
        "GOVERN": {},
        "MAP": {},
        "MEASURE": {},
        "MANAGE": {},
        "CSA_EXTRA": {} 
    }
    
    # Find about row
    about_row_idx = -1
    for idx, val in nist_df.iloc[:, 0].items():
        if str(val) == "section_about":
            about_row_idx = idx
            break

    # Build Skeleton
    for col in nist_df.columns:
        col_upper = str(col).upper()
        if re.match(r'^(GOVERN|MAP|MEASURE|MANAGE)\s+\d+\.\d+$', col_upper):
            func = col_upper.split()[0]
            desc = ""
            if about_row_idx != -1:
                desc = str(nist_df.at[about_row_idx, col])
                if desc == "nan": desc = ""
            desc = desc.replace('"', '').strip()
            
            final_data[func][col_upper] = {
                "description": desc,
                "csa_controls": []
            }
            
    print(f"NIST Skeleton built. Categories found: {sum(len(v) for v in final_data.values()) if 'CSA_EXTRA' not in final_data else sum(len(v) for k,v in final_data.items() if k!='CSA_EXTRA')}")

    # --- 2. Load CSA Data ---
    if not os.path.exists(CSA_EXCEL):
        print(f"Error: {CSA_EXCEL} not found.")
        return

    try:
        # Load Mappings
        map_df = pd.read_excel(CSA_EXCEL, sheet_name="Scope Applicability (Mappings)", header=2)
        
        # Load Controls Info
        ctrl_df = pd.read_excel(CSA_EXCEL, sheet_name="AICM", header=2)

        # Load Questions
        q_df = pd.read_excel(CSA_EXCEL, sheet_name="AI-CAIQ", header=1)
        
        print("CSA Excel loaded.")
        
    except Exception as e:
        print(f"Error reading {CSA_EXCEL}: {e}")
        return

    # Build Mapping Dictionary
    csa_map = {}
    for _, row in map_df.iterrows():
        c_id = row.get('Control ID')
        raw_map = row.get('Control Mapping.3')
        if pd.notna(c_id) and pd.notna(raw_map):
            nist_subcats = normalize_nist_mapping(str(raw_map))
            if nist_subcats:
                csa_map[c_id] = nist_subcats

    print(f"Mapped {len(csa_map)} CSA controls to NIST.")

    # Build Question Map
    q_map = {}
    for _, row in q_df.iterrows():
        c_id = row.get('Control ID')
        q_text = row.get('Consensus Assessments Question')
        q_id = row.get('Question ID')
        
        if pd.notna(c_id) and pd.notna(q_text):
            final_text = str(q_text).strip()
            if pd.notna(q_id):
                final_text = f"{q_id} {final_text}"
            q_map[c_id] = final_text

    # --- 3. Populate Controls ---
    count_mapped = 0
    count_extra = 0
    
    unique_ids_mapped = set()
    unique_ids_extra = set()
    
    # Wave Counters
    wave_counts = {1: 0, 2: 0, 3: 0}

    for _, row in ctrl_df.iterrows():
        c_id = row.get('Control ID')
        spec = row.get('Control Specification')
        domain = row.get('Control Domain')
        
        if pd.isna(c_id): continue
        
        # Determine Wave based on Heuristic
        # Goal: Wave 1 (Basic), Wave 2 (Intermediate), Wave 3 (Advanced)
        # Strategy: Mix of Domain keywords and specific priority domains.
        
        wave = 2 # Default to Intermediate
        
        dom_str = str(domain).upper() if pd.notna(domain) else ""
        c_id_str = str(c_id).upper()
        
        # Parse numeric part of ID (e.g., AIS-01 -> 1)
        try:
            id_num = int(re.search(r'(\d+)', c_id_str.split('-')[-1]).group(1))
        except:
            id_num = 99
            
        # --- WAVE 1: FOUNDATION (Governance, Inventory, Basic Security) ---
        # Include keywords related to policy, inventory, strategy, basic awareness
        w1_keywords = ["GOVERNANCE", "INVENTORY", "STRATEGY", "POLICY", "LEGAL", "HUMAN", "DATA SECURITY"]
        
        if any(k in dom_str for k in w1_keywords):
            wave = 1
        elif id_num <= 3: # First few controls in any domain are likely foundational
            wave = 1
            
        # --- WAVE 3: ADVANCED (Forensics, Audit, Specific Ops) ---
        w3_keywords = ["FORENSIC", "INCIDENT", "AUDIT", "BUSINESS CONTINUITY", "INTEROPERABILITY"]
        
        if any(k in dom_str for k in w3_keywords):
            if id_num > 2: # Keep very first incidents controls in Wave 1 or 2
                wave = 3
        
        if id_num >= 10: # High numbering usually implies specific/advanced scenarios
            wave = 3

        wave_counts[wave] += 1
        
        question_text = q_map.get(c_id, str(spec)[:100])
        
        control_obj = {
            "id": str(c_id),
            "text": question_text,
            "help": str(spec)[:300] + "..." if pd.notna(spec) and len(str(spec)) > 300 else str(spec),
            "domain": str(domain),
            "wave": wave
        }
        
        targets = csa_map.get(c_id, [])
        
        if targets:
            # Add to NIST Categories
            mapped_any = False
            for target in targets:
                func = target.split()[0]
                if func in final_data and target in final_data[func]:
                    existing_ids = [c['id'] for c in final_data[func][target]['csa_controls']]
                    if c_id not in existing_ids:
                        final_data[func][target]['csa_controls'].append(control_obj)
                        mapped_any = True
            if mapped_any:
                unique_ids_mapped.add(c_id)
                count_mapped += 1
        else:
            # Add to CSA_EXTRA
            d_key = str(domain) if pd.notna(domain) else "Uncategorized"
            
            if d_key not in final_data["CSA_EXTRA"]:
                final_data["CSA_EXTRA"][d_key] = {
                    "description": f"Controls related to {d_key}",
                    "csa_controls": []
                }
            
            existing_ids = [c['id'] for c in final_data["CSA_EXTRA"][d_key]['csa_controls']]
            if c_id not in existing_ids:
                final_data["CSA_EXTRA"][d_key]['csa_controls'].append(control_obj)
                unique_ids_extra.add(c_id)
                count_extra += 1
            
    print(f"Total Unique Mapped Controls: {len(unique_ids_mapped)}")
    print(f"Total Unique Extra Controls: {len(unique_ids_extra)}")
    print(f"Total Unique Controls in System: {len(unique_ids_mapped) + len(unique_ids_extra)}")
    print(f"Wave Distribution: {wave_counts}")

    # 4. Save JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2)
        
    print(f"Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    ingest()
