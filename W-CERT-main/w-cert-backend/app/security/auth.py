"""
W-CERT Authentication & Authorization Module
JWT-based authentication with Role-Based Access Control (RBAC).
User data stored in Google Sheets.
"""

import uuid
from datetime import datetime
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    get_jwt_identity, verify_jwt_in_request, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from ..database.sheets import append_row, find_row


# ── Role Definitions ──────────────────────────────────────────
ROLES = {
    'USER': 0,       # Can submit reports, view own incidents
    'ANALYST': 1,    # Can triage, update status, view all incidents
    'ADMIN': 2       # Full access — manage users, escalate, configure
}


def register_user(email, password, display_name='', role='USER'):
    """
    Register a new user.
    
    Returns:
        dict: User data (without password) on success.
        None: If email already exists.
    """
    # Check if user already exists
    existing, _ = find_row('Users', 'email', email)
    if existing:
        return None

    user_id = str(uuid.uuid4())[:8].upper()
    password_hash = generate_password_hash(password)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    user_data = {
        'user_id': user_id,
        'email': email,
        'password_hash': password_hash,
        'display_name': display_name or email.split('@')[0],
        'role': role,
        'created_at': timestamp
    }

    append_row('Users', user_data)

    return {
        'user_id': user_id,
        'email': email,
        'display_name': user_data['display_name'],
        'role': role
    }


def authenticate_user(email, password):
    """
    Authenticate a user with email and password.
    
    Returns:
        dict: User data + tokens on success.
        None: On invalid credentials.
    """
    user, _ = find_row('Users', 'email', email)
    if not user:
        return None

    if not check_password_hash(user['password_hash'], password):
        return None

    # Create JWT tokens with user identity and role
    identity = user['user_id']
    additional_claims = {
        'email': user['email'],
        'role': user['role'],
        'display_name': user['display_name']
    }

    access_token = create_access_token(
        identity=identity,
        additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(
        identity=identity,
        additional_claims=additional_claims
    )

    return {
        'user_id': user['user_id'],
        'email': user['email'],
        'display_name': user['display_name'],
        'role': user['role'],
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def get_current_user_role():
    """Get the role of the currently authenticated user from the JWT."""
    claims = get_jwt()
    return claims.get('role', 'USER')


def get_current_user_info():
    """Get full user info from the current JWT."""
    claims = get_jwt()
    return {
        'user_id': get_jwt_identity(),
        'email': claims.get('email', ''),
        'role': claims.get('role', 'USER'),
        'display_name': claims.get('display_name', '')
    }


def role_required(*allowed_roles):
    """
    Decorator to enforce role-based access control.
    
    Usage:
        @role_required('ADMIN', 'ANALYST')
        def admin_only_route():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_role = get_current_user_role()

            if current_role not in allowed_roles:
                return jsonify({
                    "error": "Insufficient permissions",
                    "code": "FORBIDDEN",
                    "required_roles": list(allowed_roles),
                    "your_role": current_role
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
