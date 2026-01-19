from typing import Dict, List, Any
from modules import data, scoring

def get_v2_metrics(answers_map: Dict[str, Dict[str, Any]], scope="org", project_type="cloud") -> List[scoring.DomainMetrics]:
    """
    Adapts the filtered ASSESSMENT_DATA from modules.data into the v2 DomainMetrics structure.
    """
    filtered_data = data.get_controls_for_scope(scope=scope, project_type=project_type)
    
    domain_metrics_list = []
    
    # NIST functions act as our Top-Level Domains
    nist_names = {
        "GOVERN": "Policies & Governance (GOVERN)",
        "MAP": "Contextualization & Mapping (MAP)",
        "MEASURE": "Measurement & Evaluation (MEASURE)",
        "MANAGE": "Incident Management & Mitigation (MANAGE)",
        "CSA_EXTRA": "Cloud & Infrastructure Security (CSA)"
    }

    for nist_func, subcats in filtered_data.items():
        domain_id = nist_func
        domain_name = nist_names.get(nist_func, nist_func)
        
        subcategories_data = []
        
        for subcat_id, subcat_val in subcats.items():
            # In v1, subcat_val['description'] is the NIST text
            # subcat_val['csa_controls'] is the list of questions
            
            questions = []
            for ctrl in subcat_val.get('csa_controls', []):
                questions.append({
                    'question_id': ctrl['id'],
                    'text': ctrl['text'],
                    'help': ctrl.get('help', ''),
                    'domain': ctrl.get('domain', ''), # CSA Domain
                    'wave': ctrl.get('wave', 1)
                })
            
            # Default weights and criticality based on wave or heuristics
            # Wave 1 = High, Wave 2 = Medium, Wave 3 = Low
            wave_avg = sum([q['wave'] for q in questions]) / len(questions) if questions else 2
            criticality = "High" if wave_avg <= 1.5 else ("Medium" if wave_avg <= 2.5 else "Low")
            
            subcategories_data.append({
                'id': subcat_id,
                'name': subcat_id, # e.g. "GOVERN 1.1"
                'questions': questions,
                'criticality': criticality,
                'weight': 1.0 # Can be refined later
            })
            
        if subcategories_data:
            domain_metrics = scoring.calculate_domain_metrics(
                domain_id=domain_id,
                domain_name=domain_name,
                nist_function=nist_func,
                subcategories_data=subcategories_data,
                answers_map=answers_map
            )
            domain_metrics_list.append(domain_metrics)
            
    return domain_metrics_list

def get_overall_metrics(domain_metrics: List[scoring.DomainMetrics]) -> Dict[str, Any]:
    """
    Calculates overall platform metrics from domain metrics.
    """
    if not domain_metrics:
        return {
            "score": 0.0,
            "maturity_level": "Inexistent",
            "coverage": 0.0,
            "total_questions": 0,
            "answered_questions": 0,
            "critical_gaps": 0
        }
        
    total_score = sum([dm.score for dm in domain_metrics])
    avg_score = total_score / len(domain_metrics)
    
    total_q = sum([dm.total_questions for dm in domain_metrics])
    total_ans = sum([dm.answered_questions for dm in domain_metrics])
    total_gaps = sum([dm.critical_gaps for dm in domain_metrics])
    
    return {
        "score": avg_score,
        "maturity_level": scoring.get_maturity_level(avg_score),
        "coverage": total_ans / total_q if total_q > 0 else 0.0,
        "total_questions": total_q,
        "answered_questions": total_ans,
        "critical_gaps": total_gaps
    }
