from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import math
from datetime import datetime

@dataclass
class RoadmapItem:
    priority: str # 'immediate', 'short', 'medium'
    timeframe: str # '0-30 dias', etc.
    domain: str
    action: str
    impact: str
    effort: str # 'low', 'medium', 'high'
    question_id: str
    subcat_id: str

@dataclass
class QuestionScore:
    question_id: str
    response_score: Optional[float]
    evidence_multiplier: Optional[float]
    effective_score: Optional[float]
    is_applicable: bool

@dataclass
class SubcategoryMetrics:
    subcat_id: str
    subcat_name: str
    domain_id: str
    score: float
    maturity_level: str
    total_questions: int
    answered_questions: int
    applicable_questions: int
    coverage: float
    criticality: str
    weight: float
    critical_gaps: int

@dataclass
class DomainMetrics:
    domain_id: str
    domain_name: str
    nist_function: str
    score: float
    maturity_level: str
    total_questions: int
    answered_questions: int
    applicable_questions: int
    coverage: float
    subcategory_metrics: List[SubcategoryMetrics]
    critical_gaps: int

# --- Constants & Helpers ---

RESPONSE_SCORES = {
    'Sim': 1.0,
    'Parcial': 0.5,
    'Não': 0.0,
    'NA': None
}

EVIDENCE_MULTIPLIERS = {
    'Sim': 1.0,
    'Parcial': 0.85,
    'Não': 0.7,
    'NA': 0.7  # Default if no evidence provided
}

def get_maturity_level(score: float) -> str:
    if score >= 0.9: return "Optimized (4)"
    if score >= 0.7: return "Measured (3)"
    if score >= 0.5: return "Managed (2)"
    if score >= 0.3: return "Defined (1)"
    if score > 0: return "Initial (0)"
    return "Inexistent"

# --- Scoring Logic ---

def calculate_question_score(question_id: str, answer_data: Dict[str, Any]) -> QuestionScore:
    response = answer_data.get('response')
    evidence_ok = answer_data.get('evidence_ok', 'NA')
    
    if not response or response == 'NA':
        return QuestionScore(
            question_id=question_id,
            response_score=None,
            evidence_multiplier=None,
            effective_score=None,
            is_applicable=(response != 'NA')
        )

    response_score = RESPONSE_SCORES.get(response, 0.0)
    evidence_multiplier = EVIDENCE_MULTIPLIERS.get(evidence_ok, 0.7)
    
    effective_score = response_score * evidence_multiplier if response_score is not None else None

    return QuestionScore(
        question_id=question_id,
        response_score=response_score,
        evidence_multiplier=evidence_multiplier,
        effective_score=effective_score,
        is_applicable=True
    )

def calculate_subcategory_metrics(
    subcat_id: str, 
    subcat_name: str,
    domain_id: str,
    questions: List[Dict[str, Any]], 
    answers_map: Dict[str, Dict[str, Any]],
    criticality: str = "Medium",
    weight: float = 1.0
) -> SubcategoryMetrics:
    
    total_effective_score = 0.0
    applicable_count = 0
    answered_count = 0
    critical_gaps = 0

    for q in questions:
        q_id = q.get('question_id') or q.get('id')
        answer = answers_map.get(q_id, {})
        score_data = calculate_question_score(q_id, answer)

        if answer.get('response'):
            answered_count += 1

        if score_data.is_applicable:
            applicable_count += 1
            if score_data.effective_score is not None:
                total_effective_score += score_data.effective_score

                # Count critical gaps (low score in high/critical subcategory)
                if score_data.effective_score < 0.5 and criticality in ['High', 'Critical']:
                    critical_gaps += 1

    score = total_effective_score / applicable_count if applicable_count > 0 and answered_count > 0 else 0.0
    coverage = answered_count / applicable_count if applicable_count > 0 else 0.0

    return SubcategoryMetrics(
        subcat_id=subcat_id,
        subcat_name=subcat_name,
        domain_id=domain_id,
        score=score,
        maturity_level=get_maturity_level(score),
        total_questions=len(questions),
        answered_questions=answered_count,
        applicable_questions=applicable_count,
        coverage=coverage,
        criticality=criticality,
        weight=weight,
        critical_gaps=critical_gaps
    )

def calculate_domain_metrics(
    domain_id: str,
    domain_name: str,
    nist_function: str,
    subcategories_data: List[Dict[str, Any]], # Contains subcat info + its questions
    answers_map: Dict[str, Dict[str, Any]]
) -> DomainMetrics:
    
    subcat_metrics_list = []
    total_weighted_score = 0.0
    total_weight = 0.0
    total_answered = 0
    total_applicable = 0
    total_critical_gaps = 0
    total_questions = 0

    for sc in subcategories_data:
        metrics = calculate_subcategory_metrics(
            subcat_id=sc['id'],
            subcat_name=sc['name'],
            domain_id=domain_id,
            questions=sc['questions'],
            answers_map=answers_map,
            criticality=sc.get('criticality', 'Medium'),
            weight=sc.get('weight', 1.0)
        )
        subcat_metrics_list.append(metrics)
        
        if metrics.applicable_questions > 0 and metrics.answered_questions > 0:
            total_weighted_score += metrics.score * metrics.weight
            total_weight += metrics.weight
        
        total_answered += metrics.answered_questions
        total_applicable += metrics.applicable_questions
        total_critical_gaps += metrics.critical_gaps
        total_questions += metrics.total_questions

    score = total_weighted_score / total_weight if total_weight > 0 else 0.0
    coverage = total_answered / total_applicable if total_applicable > 0 else 0.0

    return DomainMetrics(
        domain_id=domain_id,
        domain_name=domain_name,
        nist_function=nist_function,
        score=score,
        maturity_level=get_maturity_level(score),
        total_questions=total_questions,
        answered_questions=total_answered,
        applicable_questions=total_applicable,
        coverage=coverage,
        subcategory_metrics=subcat_metrics_list,
        critical_gaps=total_critical_gaps
    )

def generate_roadmap(domain_metrics: List[DomainMetrics], max_items: int = 10) -> List[RoadmapItem]:
    """
    Generates a prioritized action plan based on identified critical gaps.
    """
    gaps = []
    for dm in domain_metrics:
        for sm in dm.subcategory_metrics:
            if sm.critical_gaps > 0 or sm.score < 0.5:
                gaps.append(sm)
    
    # Sort by criticality (High/Critical first) then score (Lowest first)
    crit_map = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    gaps.sort(key=lambda x: (crit_map.get(x.criticality, 2), x.score))
    
    roadmap = []
    for sm in gaps[:max_items]:
        priority = 'immediate' if sm.criticality in ['High', 'Critical'] and sm.score < 0.3 else \
                   ('short' if sm.criticality in ['High', 'Critical'] or sm.score < 0.5 else 'medium')
        
        timeframe = '0-30 dias' if priority == 'immediate' else \
                    ('30-60 dias' if priority == 'short' else '60-90 dias')
        
        impact = 'Alto impacto em risco' if sm.criticality in ['High', 'Critical'] else 'Médio impacto em risco'
        effort = 'high' if sm.score < 0.2 else ('medium' if sm.score < 0.5 else 'low')
        
        roadmap.append(RoadmapItem(
            priority=priority,
            timeframe=timeframe,
            domain=sm.domain_name if hasattr(sm, 'domain_name') else sm.domain_id,
            action=f"Implementar controle: {sm.subcat_name}",
            impact=impact,
            effort=effort,
            question_id=sm.subcat_id, # Simplified to subcat for action
            subcat_id=sm.subcat_id
        ))
        
    return roadmap
