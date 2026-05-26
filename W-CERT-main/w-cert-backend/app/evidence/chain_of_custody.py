"""
W-CERT Chain of Custody Module
Tracks every access to evidence files in an immutable, append-only log.
Ensures forensic accountability for all evidence interactions.
"""

import uuid
from datetime import datetime
from ..database.sheets import append_row, find_rows


def record_access(evidence_id, user_id, action, details=''):
    """
    Record an access event in the chain of custody.
    This is an append-only operation — entries cannot be modified or deleted.
    
    Args:
        evidence_id (str): ID of the evidence being accessed.
        user_id (str): ID of the user performing the action.
        action (str): Type of access (UPLOAD, VIEW, DOWNLOAD, VERIFY).
        details (str): Additional context.
    """
    from ..security.audit import _get_client_ip

    entry = {
        'log_id': str(uuid.uuid4())[:8].upper(),
        'user_id': user_id,
        'action': f'COC_{action}',
        'resource_type': 'evidence',
        'resource_id': evidence_id,
        'ip_address': _get_client_ip(),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'details': details
    }

    append_row('Audit_Log', entry)


def get_chain(evidence_id):
    """
    Get the full chain of custody for an evidence item.
    Returns all access records in chronological order.
    
    Args:
        evidence_id (str): The evidence ID to look up.
    
    Returns:
        list: List of access records (dicts), oldest first.
    """
    all_entries = find_rows('Audit_Log', 'resource_id', evidence_id)
    # Filter to only chain-of-custody entries
    coc_entries = [
        entry for entry in all_entries
        if entry.get('action', '').startswith('COC_')
    ]
    return coc_entries


# ── Chain of Custody Action Constants ──────────────────────────
class CoCActions:
    """Standard chain of custody action types."""
    UPLOAD = 'UPLOAD'
    VIEW = 'VIEW'
    DOWNLOAD = 'DOWNLOAD'
    VERIFY = 'VERIFY'
    INTEGRITY_CHECK = 'INTEGRITY_CHECK'
