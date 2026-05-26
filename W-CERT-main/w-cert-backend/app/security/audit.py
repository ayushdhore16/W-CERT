"""
W-CERT Audit Logging Module
Records all significant actions to the Audit_Log worksheet.
Provides tamper-evident audit trail for forensic accountability.
"""

import uuid
from datetime import datetime
from flask import request
from ..database.sheets import append_row


def log_action(user_id, action, resource_type='', resource_id='', details=''):
    """
    Log an auditable action to Google Sheets.
    
    Args:
        user_id (str): ID of the user performing the action.
        action (str): Action type, e.g. 'LOGIN', 'REPORT_SUBMITTED', 'EVIDENCE_UPLOADED'.
        resource_type (str): Type of resource affected, e.g. 'incident', 'evidence'.
        resource_id (str): ID of the affected resource.
        details (str): Additional context.
    """
    log_entry = {
        'log_id': str(uuid.uuid4())[:8].upper(),
        'user_id': user_id,
        'action': action,
        'resource_type': resource_type,
        'resource_id': resource_id,
        'ip_address': _get_client_ip(),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'details': details
    }

    try:
        append_row('Audit_Log', log_entry)
    except Exception as e:
        # Audit logging should never crash the main application
        print(f"[!] Audit log error: {e}")


def _get_client_ip():
    """Extract client IP address from the request."""
    try:
        # Support for reverse proxies
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        return request.remote_addr or 'unknown'
    except RuntimeError:
        # Outside of request context
        return 'system'


# ── Predefined Action Constants ────────────────────────────────
class Actions:
    """Standard audit action types."""
    LOGIN = 'LOGIN'
    LOGOUT = 'LOGOUT'
    REGISTER = 'REGISTER'
    REPORT_SUBMITTED = 'REPORT_SUBMITTED'
    REPORT_VIEWED = 'REPORT_VIEWED'
    STATUS_UPDATED = 'STATUS_UPDATED'
    EVIDENCE_UPLOADED = 'EVIDENCE_UPLOADED'
    EVIDENCE_ACCESSED = 'EVIDENCE_ACCESSED'
    ESCALATION_CREATED = 'ESCALATION_CREATED'
    USER_ROLE_CHANGED = 'USER_ROLE_CHANGED'
