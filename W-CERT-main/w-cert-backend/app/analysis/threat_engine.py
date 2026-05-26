"""
W-CERT Threat Analysis Engine
Core analysis logic for phishing and social engineering threat detection.
Uses weighted keyword matching with category-based scoring.
"""

from .patterns import THREAT_PATTERNS, ATTACK_TYPES, get_recommendations_for_categories
from .severity import classify_severity, should_auto_escalate


def analyze_threat(description):
    """
    Perform comprehensive threat analysis on an incident description.
    
    Uses multi-category weighted keyword matching to:
    1. Calculate a threat score
    2. Identify detected threat indicators (tags)
    3. Classify severity (LOW/MEDIUM/HIGH/CRITICAL)
    4. Determine attack type (PHISHING/SOCIAL_ENGINEERING/COMBINED)
    5. Generate response recommendations
    
    Args:
        description (str): The incident description text.
    
    Returns:
        dict: Analysis result with keys:
            - score (int): Total threat score
            - severity (str): Severity level
            - detected_tags (list): Matched keywords
            - attack_vectors (list): Detected threat categories
            - attack_type (str): PHISHING, SOCIAL_ENGINEERING, or COMBINED
            - recommendations (list): Response actions
            - auto_escalate (bool): Whether auto-escalation is recommended
            - category_scores (dict): Score breakdown by category
    """
    if not description:
        return _empty_result()

    desc_lower = description.lower()
    
    total_score = 0
    detected_tags = []
    category_scores = {}
    detected_categories = set()

    # ── Scan each threat category ──────────────────────────────
    for category, data in THREAT_PATTERNS.items():
        cat_score = 0
        cat_tags = []

        for keyword, base_weight in data['keywords'].items():
            if keyword in desc_lower:
                adjusted_weight = int(base_weight * data['weight_multiplier'])
                cat_score += adjusted_weight
                cat_tags.append(keyword)

        if cat_score > 0:
            category_scores[category] = cat_score
            detected_categories.add(category)
            detected_tags.extend(cat_tags)
            total_score += cat_score

    # ── Determine attack type ──────────────────────────────────
    attack_type = _classify_attack_type(desc_lower)

    # ── Classify severity ──────────────────────────────────────
    severity = classify_severity(total_score)
    auto_escalate = should_auto_escalate(severity)

    # ── Generate recommendations ───────────────────────────────
    recommendations = get_recommendations_for_categories(detected_categories)

    # Add generic recommendations if no specific categories detected
    if not recommendations:
        recommendations = [
            'Monitor the situation and preserve any evidence',
            'Do not share personal information with unknown contacts',
            'Report suspicious activity to local cyber crime authorities'
        ]

    return {
        'score': total_score,
        'severity': severity.value,
        'detected_tags': list(set(detected_tags)),  # Remove duplicates
        'attack_vectors': sorted(list(detected_categories)),
        'attack_type': attack_type,
        'recommendations': recommendations,
        'auto_escalate': auto_escalate,
        'category_scores': category_scores
    }


def _classify_attack_type(desc_lower):
    """
    Determine if the attack is phishing, social engineering, or combined.
    Based on indicator keywords in the description.
    """
    phishing_hits = sum(
        1 for ind in ATTACK_TYPES['PHISHING']['indicators']
        if ind in desc_lower
    )
    se_hits = sum(
        1 for ind in ATTACK_TYPES['SOCIAL_ENGINEERING']['indicators']
        if ind in desc_lower
    )

    if phishing_hits > 0 and se_hits > 0:
        return 'COMBINED'
    elif phishing_hits > 0:
        return 'PHISHING'
    elif se_hits > 0:
        return 'SOCIAL_ENGINEERING'
    else:
        return 'UNKNOWN'


def _empty_result():
    """Return an empty/zero analysis result."""
    return {
        'score': 0,
        'severity': 'LOW',
        'detected_tags': [],
        'attack_vectors': [],
        'attack_type': 'UNKNOWN',
        'recommendations': [
            'No specific threat indicators detected.',
            'If you believe you are at risk, contact local authorities.'
        ],
        'auto_escalate': False,
        'category_scores': {}
    }


def get_threat_summary(analysis_result):
    """
    Generate a human-readable summary of the threat analysis.
    
    Args:
        analysis_result (dict): Output from analyze_threat().
    
    Returns:
        str: A formatted summary string.
    """
    severity = analysis_result['severity']
    score = analysis_result['score']
    vectors = ', '.join(analysis_result['attack_vectors']) or 'None detected'
    tags = ', '.join(analysis_result['detected_tags'][:10]) or 'None'

    summary = (
        f"Threat Level: {severity} (Score: {score})\n"
        f"Attack Vectors: {vectors}\n"
        f"Attack Type: {analysis_result['attack_type']}\n"
        f"Detected Indicators: {tags}\n"
    )

    if analysis_result['auto_escalate']:
        summary += "⚠ AUTO-ESCALATION RECOMMENDED\n"

    return summary
