"""
W-CERT Attack Pattern Definitions
Structured threat pattern data for phishing & social engineering analysis.
Each category contains weighted keywords and response recommendations.
"""


# ── Threat Categories with Weighted Keywords ───────────────────
THREAT_PATTERNS = {
    'sextortion': {
        'description': 'Threats involving intimate content, blackmail, or privacy violations',
        'weight_multiplier': 1.5,  # Higher base weight — most severe for target demographic
        'keywords': {
            'leak': 35,
            'private': 25,
            'photos': 30,
            'intimate': 35,
            'blackmail': 40,
            'expose': 30,
            'nude': 35,
            'video call': 25,
            'screenshot': 20,
            'record': 20,
            'share publicly': 35,
            'morphed': 30,
            'deepfake': 35
        },
        'recommendations': [
            'Do NOT engage with the attacker or pay any amount',
            'Preserve all evidence (screenshots, messages, emails)',
            'Report to Cyber Crime Cell (cybercrime.gov.in)',
            'Contact Women Helpline: 181 or NCW: 7827-170-170',
            'Consider reporting to platform (social media) for account takedown'
        ]
    },
    
    'financial_fraud': {
        'description': 'Monetary scams, fake payments, UPI fraud',
        'weight_multiplier': 1.0,
        'keywords': {
            'money': 15,
            'bank': 15,
            'transfer': 15,
            'payment': 15,
            'upi': 20,
            'credit card': 20,
            'refund': 15,
            'prize': 20,
            'lottery': 25,
            'investment': 15,
            'loan': 15,
            'cashback': 15,
            'wallet': 10
        },
        'recommendations': [
            'Do NOT share OTP, CVV, or banking credentials',
            'Contact your bank immediately to freeze suspicious transactions',
            'Report UPI fraud via NPCI (npci.org.in)',
            'File complaint at cybercrime.gov.in with transaction details'
        ]
    },
    
    'identity_theft': {
        'description': 'Credential harvesting, account takeover, impersonation',
        'weight_multiplier': 1.2,
        'keywords': {
            'password': 20,
            'otp': 20,
            'verify': 15,
            'account': 15,
            'login': 15,
            'credential': 20,
            'aadhaar': 25,
            'pan card': 20,
            'kyc': 20,
            'verify identity': 20,
            'suspended': 15,
            'locked': 15,
            'unauthorized': 20
        },
        'recommendations': [
            'Change passwords immediately on affected accounts',
            'Enable two-factor authentication (2FA)',
            'Check for unauthorized transactions or activities',
            'Do NOT click any links in suspicious messages'
        ]
    },
    
    'impersonation': {
        'description': 'Fake authority figures, social manipulation via trust',
        'weight_multiplier': 1.1,
        'keywords': {
            'police': 10,
            'government': 10,
            'boss': 10,
            'manager': 10,
            'hr': 10,
            'tax': 10,
            'court': 15,
            'arrest': 20,
            'warrant': 20,
            'customs': 15,
            'delivery': 10,
            'colleague': 10,
            'relative': 10
        },
        'recommendations': [
            'Verify identity through official channels (call the person/org directly)',
            'Government agencies NEVER ask for money or OTPs via phone/email',
            'Do NOT share personal info with unverified callers',
            'Report impersonation attempts to the real organization'
        ]
    },
    
    'urgency_manipulation': {
        'description': 'Pressure tactics using urgency and fear',
        'weight_multiplier': 0.8,  # Lower standalone weight — usually combined with other categories
        'keywords': {
            'urgent': 15,
            'immediately': 15,
            'deadline': 10,
            'last chance': 15,
            'expire': 10,
            'hurry': 10,
            'now': 5,
            'emergency': 15,
            'act fast': 15,
            'limited time': 10,
            'within 24 hours': 15,
            'final warning': 20
        },
        'recommendations': [
            'Legitimate organizations allow reasonable response time',
            'Stop and verify before acting — urgency is a manipulation tactic',
            'Contact the supposed sender through independent, verified channels',
            'Take screenshots of urgency-based messages as evidence'
        ]
    }
}


# ── Attack Type Classification ─────────────────────────────────
ATTACK_TYPES = {
    'PHISHING': {
        'description': 'Fraudulent communication designed to steal data/credentials',
        'indicators': ['link', 'url', 'click', 'email', 'website', 'login page', 'form']
    },
    'SOCIAL_ENGINEERING': {
        'description': 'Psychological manipulation to gain trust or create fear',
        'indicators': ['call', 'phone', 'message', 'whatsapp', 'instagram', 
                       'facebook', 'dating', 'relationship', 'friend request']
    },
    'COMBINED': {
        'description': 'Attack using both phishing and social engineering techniques',
        'indicators': []  # Assigned when both types are detected
    }
}


def get_all_keywords():
    """Get a flat dict of all keywords and their weighted scores."""
    all_kw = {}
    for category, data in THREAT_PATTERNS.items():
        for keyword, weight in data['keywords'].items():
            # Apply category weight multiplier
            adjusted_weight = int(weight * data['weight_multiplier'])
            all_kw[keyword] = {
                'weight': adjusted_weight,
                'category': category
            }
    return all_kw


def get_recommendations_for_categories(categories):
    """Get combined recommendations for detected threat categories."""
    recommendations = []
    seen = set()
    for cat in categories:
        if cat in THREAT_PATTERNS:
            for rec in THREAT_PATTERNS[cat]['recommendations']:
                if rec not in seen:
                    recommendations.append(rec)
                    seen.add(rec)
    return recommendations
