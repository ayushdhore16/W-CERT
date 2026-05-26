"""
W-CERT Incident Model
Defines incident data structure and status constants.
"""


class IncidentStatus:
    """Incident lifecycle statuses."""
    OPEN = 'OPEN'
    TRIAGED = 'TRIAGED'
    INVESTIGATING = 'INVESTIGATING'
    ESCALATED = 'ESCALATED'
    RESOLVED = 'RESOLVED'
    CLOSED = 'CLOSED'

    ALL = [OPEN, TRIAGED, INVESTIGATING, ESCALATED, RESOLVED, CLOSED]


class AttackType:
    """Attack type classification."""
    PHISHING = 'PHISHING'
    SOCIAL_ENGINEERING = 'SOCIAL_ENGINEERING'
    COMBINED = 'COMBINED'
    UNKNOWN = 'UNKNOWN'


def create_incident_dict(**kwargs):
    """Create an incident data dictionary matching the Sheets schema."""
    return {
        'incident_id': kwargs.get('incident_id', ''),
        'reporter_id': kwargs.get('reporter_id', ''),
        'encrypted_name': kwargs.get('encrypted_name', ''),
        'encrypted_contact': kwargs.get('encrypted_contact', ''),
        'description': kwargs.get('description', ''),
        'attack_type': kwargs.get('attack_type', AttackType.UNKNOWN),
        'threat_score': str(kwargs.get('threat_score', 0)),
        'severity': kwargs.get('severity', 'LOW'),
        'detected_tags': kwargs.get('detected_tags', ''),
        'content_hash': kwargs.get('content_hash', ''),
        'status': kwargs.get('status', IncidentStatus.OPEN),
        'created_at': kwargs.get('created_at', ''),
        'updated_at': kwargs.get('updated_at', '')
    }
