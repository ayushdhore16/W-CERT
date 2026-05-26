"""
W-CERT Admin Routes
Administrative tools for user management and audit log review.
"""

from flask import Blueprint, jsonify, request
from ..security.auth import role_required
from ..database.sheets import get_all_rows, find_row, update_row

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@role_required('ADMIN')
def list_users():
    """List all registered users. Admin only."""
    users = get_all_rows('Users')
    
    # Strip passwords for security
    safe_users = []
    for u in users:
        safe_users.append({
            'user_id': u.get('user_id'),
            'display_name': u.get('display_name'),
            'email': u.get('email'),
            'role': u.get('role'),
            'created_at': u.get('created_at')
        })
        
    return jsonify({
        "status": "success",
        "count": len(safe_users),
        "users": safe_users
    }), 200

@admin_bp.route('/users/<user_id>/role', methods=['PATCH'])
@role_required('ADMIN')
def update_user_role(user_id):
    """Update a user's role. Admin only."""
    data = request.get_json()
    new_role = data.get('role', '').upper()
    
    if new_role not in ['USER', 'ANALYST', 'ADMIN']:
        return jsonify({"error": "Invalid role. Use USER, ANALYST, or ADMIN"}), 400
        
    user, row_idx = find_row('Users', 'user_id', user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    update_row('Users', row_idx, {'role': new_role})
    
    return jsonify({
        "status": "success",
        "message": f"User {user_id} promoted/demoted to {new_role}",
        "user_id": user_id,
        "new_role": new_role
    }), 200

@admin_bp.route('/audit-logs', methods=['GET'])
@role_required('ADMIN')
def list_audit_logs():
    """List all system audit logs. Admin only."""
    logs = get_all_rows('Audit_Log')
    
    # Audit logs are usually returned latest first
    logs.reverse()
    
    return jsonify({
        "status": "success",
        "count": len(logs),
        "logs": logs
    }), 200
