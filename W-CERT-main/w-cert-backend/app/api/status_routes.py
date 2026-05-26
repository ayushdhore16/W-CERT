"""
W-CERT Status Routes
Publicly accessible endpoints for incident status tracking.
"""

from flask import Blueprint, jsonify
from ..database.sheets import find_row

status_bp = Blueprint('status', __name__)

@status_bp.route('/status/<incident_id>', methods=['GET'])
def check_incident_status(incident_id):
    """
    Check the status of an incident report.
    Publicly accessible - returns only status and severity info.
    """
    incident, _ = find_row('Incidents', 'incident_id', incident_id)
    
    if not incident:
        return jsonify({"error": "Incident not found"}), 404
        
    return jsonify({
        "status": "success",
        "incident": {
            "incident_id": incident_id,
            "status": incident.get('status'),
            "severity": incident.get('severity'),
            "created_at": incident.get('created_at'),
            "updated_at": incident.get('updated_at')
        }
    }), 200
