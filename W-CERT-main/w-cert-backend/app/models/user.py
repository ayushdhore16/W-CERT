"""
W-CERT User Model
Defines user data structure for Google Sheets storage.
"""


class UserRole:
    """User role constants for RBAC."""
    USER = 'USER'
    ANALYST = 'ANALYST'
    ADMIN = 'ADMIN'

    ALL = [USER, ANALYST, ADMIN]


def create_user_dict(user_id, email, password_hash, display_name='', role='USER', created_at=''):
    """Create a user data dictionary matching the Sheets schema."""
    return {
        'user_id': user_id,
        'email': email,
        'password_hash': password_hash,
        'display_name': display_name,
        'role': role,
        'created_at': created_at
    }


def sanitize_user(user_dict):
    """Remove sensitive fields from user data for API responses."""
    if not user_dict:
        return None
    return {
        'user_id': user_dict.get('user_id'),
        'email': user_dict.get('email'),
        'display_name': user_dict.get('display_name'),
        'role': user_dict.get('role'),
        'created_at': user_dict.get('created_at')
    }
