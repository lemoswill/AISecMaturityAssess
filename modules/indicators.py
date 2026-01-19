from typing import Dict, List, Any
import streamlit as st

# Keyword definitions from ai-assess-insight
INDICATORS_CONFIG = {
    'AI_SECURITY': [
        {
            'id': 'model-risks',
            'label': 'Riscos de Modelo',
            'keywords': ['model', 'ml', 'machine learning', 'training', 'inference', 'bias', 'drift', 'adversarial', 'prompt injection', 'hallucination', 'llm'],
            'icon': '🧠',
            'color': '#8B5CF6',
            'description': 'Drift, degradação, overfitting e vulnerabilidades do modelo.'
        },
        {
            'id': 'data-governance',
            'label': 'Governança de Dados',
            'keywords': ['training data', 'dataset', 'data quality', 'data governance', 'privacy', 'lineage'],
            'icon': '📁',
            'color': '#3B82F6',
            'description': 'Qualidade, proveniência e viés nos dados de treinamento.'
        },
        {
            'id': 'adversarial-defense',
            'label': 'Defesa Adversarial',
            'keywords': ['adversarial', 'attack', 'injection', 'jailbreak', 'prompt', 'mitre atlas', 'red teaming'],
            'icon': '⚠️',
            'color': '#EF4444',
            'description': 'Proteção contra prompt injection, evasion e poisoning attacks.'
        },
        {
            'id': 'bias-ethics',
            'label': 'Ética e Viés',
            'keywords': ['bias', 'fairness', 'discrimination', 'ethics', 'explainability', 'transparency', 'accountability'],
            'icon': '⚖️',
            'color': '#10B981',
            'description': 'Viés algorítmico, explicabilidade e transparência.'
        }
    ]
}

def calculate_indicators(questions: List[Dict[str, Any]], answers_map: Dict[str, Any], domain_key="AI_SECURITY"):
    """
    Groups questions by keywords and calculates maturity for each group.
    """
    config = INDICATORS_CONFIG.get(domain_key, INDICATORS_CONFIG['AI_SECURITY'])
    results = []

    for indicator in config:
        matched_questions = []
        for q in questions:
            q_text = (q.get('text', '') + ' ' + q.get('help', '')).lower()
            if any(kw in q_text for kw in indicator['keywords']):
                matched_questions.append(q)
        
        if not matched_questions:
            continue
            
        answered_count = 0
        total_score = 0.0
        
        for q in matched_questions:
            q_id = q.get('question_id') or q.get('id')
            # Look for answer in session state or map
            ans_val = answers_map.get(f"score_{q_id}", 0) or answers_map.get(q_id, 0)
            if isinstance(ans_val, str):
                # Handle string responses if any
                score_map = {"Sim": 1.0, "Parcial": 0.5, "Não": 0.0}
                ans_val = score_map.get(ans_val, 0.0)
            
            if ans_val > 0:
                answered_count += 1
                total_score += ans_val
        
        percentage = (total_score / len(matched_questions)) * 100
        results.append({
            **indicator,
            'value': answered_count,
            'total': len(matched_questions),
            'percentage': percentage
        })
    
    return results
