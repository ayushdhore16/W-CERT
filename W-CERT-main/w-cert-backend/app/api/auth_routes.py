"""
W-CERT Authentication Routes
Handles user registration, login, and token refresh.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..security.auth import register_user, authenticate_user
from ..security.audit import log_action, Actions

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')
    display_name = data.get('display_name', '')

    # Validation
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    if '@' not in email:
        return jsonify({"error": "Invalid email format"}), 400

    # Register (default role: USER)
    result = register_user(email, password, display_name)

    if result is None:
        return jsonify({"error": "An account with this email already exists"}), 409

    # Audit log
    log_action(result['user_id'], Actions.REGISTER, 'user', result['user_id'],
               f'New user registered: {email}')

    return jsonify({
        "status": "success",
        "message": "Account created successfully",
        "user": result
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate and receive JWT tokens."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    result = authenticate_user(email, password)

    if result is None:
        return jsonify({"error": "Invalid email or password"}), 401

    # Audit log
    log_action(result['user_id'], Actions.LOGIN, 'user', result['user_id'],
               f'User logged in: {email}')

    return jsonify({
        "status": "success",
        "message": "Login successful",
        "user": {
            "user_id": result['user_id'],
            "email": result['email'],
            "display_name": result['display_name'],
            "role": result['role']
        },
        "access_token": result['access_token'],
        "refresh_token": result['refresh_token']
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh the access token using a valid refresh token."""
    from flask_jwt_extended import create_access_token, get_jwt

    identity = get_jwt_identity()
    claims = get_jwt()

    new_token = create_access_token(
        identity=identity,
        additional_claims={
            'email': claims.get('email', ''),
            'role': claims.get('role', 'USER'),
            'display_name': claims.get('display_name', '')
        }
    )

    return jsonify({
        "status": "success",
        "access_token": new_token
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    """Get the current authenticated user's profile."""
    from ..security.auth import get_current_user_info
    user = get_current_user_info()
    return jsonify({"user": user}), 200
