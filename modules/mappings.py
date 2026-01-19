import modules.data as data

# Framework Mappings Logic
# Maps NIST AI RMF Categories to other standards.

def get_control_info(control_id):
    """
    Retrieve text/description for a specific control ID.
    Returns dict: {'text': ..., 'help': ...}
    """
    for func, subcats in data.ASSESSMENT_DATA.items():
        for subcat_key, content in subcats.items():
            controls = content.get('csa_controls', [])
            for c in controls:
                if c['id'] == control_id:
                    return {'text': c.get('text', ''), 'help': c.get('help', '')}
    return {'text': 'Control text not found', 'help': ''}

def get_subcat_from_id(control_id):
    """
    Reverse lookup to find which NIST Subcategory a control belongs to.
    e.g. "A&A-01" -> "GOVERN 1.1"
    """
    # Iterate through loaded data
    # This is efficient enough for ~100 controls
    for func, subcats in data.ASSESSMENT_DATA.items():
        for subcat_key, content in subcats.items():
            controls = content.get('csa_controls', [])
            for c in controls:
                if c['id'] == control_id:
                    return subcat_key
    return "Unmapped"

def get_compliance_mapping(nist_subcat_key):
    """
    Returns framework mappings for a given NIST AI RMF Subcategory.
    Matches primarily on the Category level (e.g. GOVERN 1) if specific subcat not found.
    """
    # Extract Category Base (e.g. "GOVERN 1.1" -> "GOVERN 1")
    parts = nist_subcat_key.split('.')
    if len(parts) >= 2:
        base_cat = parts[0].strip() # "GOVERN 1"
    else:
        base_cat = nist_subcat_key

    # Default / Fallback
    mapping = {
        "nist_600_1": "General GenAI Risk Management",
        "iso_27001": "A.5 Organizational Controls",
        "eu_ai_act": "General Principles (Art 4)"
    }

    # --- GOVERNANCE ---
    if "GOVERN 1" in base_cat: # Culture & Policies
        mapping = {
            "nist_600_1": "GV 1: GenAI Policies (Public vs Enterprise usage)",
            "iso_27001": "A.5.1 Policies for information security",
            "eu_ai_act": "Art 17: Quality Management System"
        }
    elif "GOVERN 2" in base_cat: # Strategy & Objectives
        mapping = {
            "nist_600_1": "GV 2: GenAI Business Case & Risk Appetite",
            "iso_27001": "A.5.8 Information security in project management",
            "eu_ai_act": "Art 9: Risk Management System"
        }
    elif "GOVERN 3" in base_cat: # Workforce & Roles
        mapping = {
            "nist_600_1": "GV 3: Human Oversight of GenAI & Training",
            "iso_27001": "A.6 People Controls",
            "eu_ai_act": "Art 14: Human Oversight"
        }
    elif "GOVERN 4" in base_cat: # Engagement
        mapping = {
            "nist_600_1": "GV 4: Feedback loops for GenAI transparency",
            "iso_27001": "A.5.4 Management responsibilities",
            "eu_ai_act": "Art 52: Transparency Obligations"
        }
    elif "GOVERN 5" in base_cat: # Impact & Legal
        mapping = {
            "nist_600_1": "GV 5: GenAI IP & Copyright Risk Assessment",
            "iso_27001": "A.5.32 Intellectual property rights",
            "eu_ai_act": "Art 10: Data & Governance (Copyright)"
        }
    elif "GOVERN 6" in base_cat: # Third Party
        mapping = {
            "nist_600_1": "GV 6: LLM Provider/API Supply Chain Risk",
            "iso_27001": "A.5.19 Supplier relationships",
            "eu_ai_act": "Art 28: Responsibilities along the AI value chain"
        }

    # --- MAP ---
    elif "MAP 1" in base_cat: # Context & Use Case
        mapping = {
            "nist_600_1": "MAP 1: Establish Context for GenAI Use",
            "iso_27001": "A.4 Context of the organization",
            "eu_ai_act": "Art 6: Classification rules for high-risk AI"
        }
    elif "MAP 2" in base_cat: # Impacts
        mapping = {
            "nist_600_1": "MAP 2: Assess Bias & Hallucination Impact",
            "iso_27001": "A.5.25 Assessment of events",
            "eu_ai_act": "Art 71: Penalties & Compliance"
        }
    elif "MAP 3" in base_cat: # Risks
        mapping = {
            "nist_600_1": "MAP 3: Model Inversion & Prompt Injection Risks",
            "iso_27001": "A.8.8 Management of technical vulnerabilities",
            "eu_ai_act": "Art 15: Accuracy, Robustness and Cybersecurity"
        }
    elif "MAP 4" in base_cat: # Knowledge
        mapping = {
            "nist_600_1": "MAP 4: Scientific Integrity of GenAI outputs",
            "iso_27001": "A.5.6 Contact with special interest groups",
            "eu_ai_act": "Recital 60: Technical Documentation"
        }

    # --- MEASURE ---
    elif "MEASURE 1" in base_cat: # Approaches & Metrics
        mapping = {
            "nist_600_1": "TE 1: Red-teaming & Jailbreak Testing",
            "iso_27001": "A.8.29 Information security testing",
            "eu_ai_act": "Art 15: Robustness/Cybersecurity"
        }
    elif "MEASURE 2" in base_cat: # Quality
        mapping = {
            "nist_600_1": "TE 2: Data Provenance & Training Data Quality",
            "iso_27001": "A.5.33 Protection of records",
            "eu_ai_act": "Art 10: Training, Validation, Testing Data"
        }
    elif "MEASURE 3" in base_cat: # Feedback
        mapping = {
            "nist_600_1": "TE 3: Monitoring Model Drift & Toxicity",
            "iso_27001": "A.8.16 Monitoring activities",
            "eu_ai_act": "Art 61: Post-market monitoring"
        }

    # --- MANAGE ---
    elif "MANAGE 1" in base_cat: # Prioritize
        mapping = {
            "nist_600_1": "MG 1: Prioritize GenAI Risks (e.g. CBRN)",
            "iso_27001": "A.5.21 Managing ICT supply chain security",
            "eu_ai_act": "Art 9: Risk Management System"
        }
    elif "MANAGE 2" in base_cat: # Strategy
        mapping = {
            "nist_600_1": "MG 2: Incident Response for Deepfakes/Content",
            "iso_27001": "A.5.24 Information security incident management",
            "eu_ai_act": "Art 62: Reporting of serious incidents"
        }
    elif "MANAGE 3" in base_cat: # Response
        mapping = {
            "nist_600_1": "MG 3: Decommissioning Unsafe Models",
            "iso_27001": "A.8.10 Information deletion",
            "eu_ai_act": "Art 65: Procedure for dealing with AI systems presenting a risk"
        }
    elif "MANAGE 4" in base_cat: # Feedback
        mapping = {
            "nist_600_1": "MG 4: Continuous Learning from GenAI Incidents",
            "iso_27001": "A.5.5 Contact with authorities",
            "eu_ai_act": "Art 11: Technical Documentation"
        }

    return mapping
