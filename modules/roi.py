
def calculate_roi(maturity_score, baseline_breach_cost=4450000, prob_low_maturity=0.35):
    """
    Calculates the financial ROI of security maturity.
    
    Args:
        maturity_score (float): 0 to 5 score.
        baseline_breach_cost (int): Average cost of a breach (default $4.45M).
        prob_low_maturity (float): Probability of incident at low maturity (Level 1).
    """
    
    # Probability Factor (Inversely proportional to score)
    # Score 0: factor 1.0
    # Score 5: factor 0.1 (90% reduction)
    reduction_factor = 1.0 - (min(maturity_score, 5) / 5.0 * 0.9)
    
    current_ale = baseline_breach_cost * prob_low_maturity * reduction_factor
    baseline_ale = baseline_breach_cost * prob_low_maturity
    
    savings = baseline_ale - current_ale
    
    return {
        "baseline_ale": baseline_ale,
        "current_exposure": current_ale,
        "estimated_savings": savings,
        "reduction_pct": (1 - reduction_factor) * 100
    }
