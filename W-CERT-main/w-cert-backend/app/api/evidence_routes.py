"""
W-CERT Evidence Routes
Handles evidence file uploads, retrieval, and chain of custody queries.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..security.auth import role_required, get_current_user_info
from ..security.audit import log_action, Actions
from ..evidence.manager import process_upload
from ..evidence.chain_of_custody import record_access, get_chain, CoCActions
from ..evidence.storage import retrieve_file, file_exists
from ..database.sheets import find_rows, find_row, update_row
from ..analysis.verification_engine import verify_authenticity
import io

evidence_bp = Blueprint('evidence', __name__)


@evidence_bp.route('/incidents/<incident_id>/evidence', methods=['POST'])
@jwt_required()
def upload_evidence(incident_id):
    """Upload an evidence file for a specific incident."""
    # Verify incident exists
    incident, _ = find_row('Incidents', 'incident_id', incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    # Check for file in request
    if 'file' not in request.files:
        return jsonify({"error": "No file provided. Use 'file' as the form field name."}), 400

    file = request.files['file']
    user = get_current_user_info()

    try:
        metadata = process_upload(file, incident_id, user['user_id'])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

    # ── Update Incident Authenticity ───────────────────────────
    # Fetch updated evidence list including the one just uploaded
    updated_evidence_list = find_rows('Evidence_Metadata', 'incident_id', incident_id)
    # Re-run verification
    auth_check = verify_authenticity(incident.get('description'), updated_evidence_list)
    
    # Update Incident record
    _, row_idx = find_row('Incidents', 'incident_id', incident_id)
    update_row('Incidents', row_idx, {
        'authenticity_score': str(auth_check['authenticity_score']),
        'authenticity_status': auth_check['authenticity_status'],
        'verification_insights': ', '.join(auth_check['verification_insights'])
    })

    # Audit log
    log_action(user['user_id'], Actions.EVIDENCE_UPLOADED, 'evidence',
               metadata['evidence_id'],
               f'File: {metadata["original_filename"]}, Hash: {metadata["file_hash"][:16]}...')

    return jsonify({
        "status": "success",
        "message": "Evidence uploaded successfully and report authenticity re-calculated",
        "authenticity": auth_check,
        "evidence": {
            "evidence_id": metadata['evidence_id'],
            "incident_id": incident_id,
            "original_filename": metadata['original_filename'],
            "file_hash": metadata['file_hash'],
            "file_size": metadata['file_size'],
            "mime_type": metadata['mime_type'],
            "uploaded_at": metadata['uploaded_at']
        }
    }), 201


@evidence_bp.route('/incidents/<incident_id>/evidence', methods=['GET'])
@jwt_required()
def list_evidence(incident_id):
    """List all evidence files for a specific incident."""
    # Verify incident exists
    incident, _ = find_row('Incidents', 'incident_id', incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    # Access control
    user = get_current_user_info()
    if user['role'] == 'USER' and incident.get('reporter_id') != user['user_id']:
        return jsonify({"error": "Access denied"}), 403

    evidence_list = find_rows('Evidence_Metadata', 'incident_id', incident_id)

    # Strip storage paths from response
    safe_evidence = []
    for ev in evidence_list:
        safe_evidence.append({
            'evidence_id': ev.get('evidence_id'),
            'incident_id': ev.get('incident_id'),
            'original_filename': ev.get('original_filename'),
            'file_hash': ev.get('file_hash'),
            'file_size': ev.get('file_size'),
            'mime_type': ev.get('mime_type'),
            'uploaded_by': ev.get('uploaded_by'),
            'uploaded_at': ev.get('uploaded_at')
        })

    return jsonify({
        "status": "success",
        "count": len(safe_evidence),
        "evidence": safe_evidence
    }), 200


@evidence_bp.route('/evidence/<evidence_id>/download', methods=['GET'])
@jwt_required()
def download_evidence(evidence_id):
    """Download an evidence file."""
    user = get_current_user_info()

    # Find evidence metadata
    evidence, _ = find_row('Evidence_Metadata', 'evidence_id', evidence_id)
    if not evidence:
        return jsonify({"error": "Evidence not found"}), 404

    # Access control
    incident, _ = find_row('Incidents', 'incident_id', evidence.get('incident_id'))
    if user['role'] == 'USER' and incident and incident.get('reporter_id') != user['user_id']:
        return jsonify({"error": "Access denied"}), 403

    # Retrieve file
    storage_path = evidence.get('storage_path')
    if not file_exists(storage_path):
        return jsonify({"error": "Evidence file not found in storage"}), 404

    file_data = retrieve_file(storage_path)

    # Chain of custody: record download
    record_access(evidence_id, user['user_id'], CoCActions.DOWNLOAD,
                  f'Downloaded by {user["email"]}')

    log_action(user['user_id'], Actions.EVIDENCE_ACCESSED, 'evidence', evidence_id,
               f'File downloaded: {evidence.get("original_filename")}')

    return send_file(
        io.BytesIO(file_data),
        mimetype=evidence.get('mime_type', 'application/octet-stream'),
        as_attachment=True,
        download_name=evidence.get('original_filename', 'evidence')
    )


@evidence_bp.route('/evidence/<evidence_id>/chain', methods=['GET'])
@role_required('ANALYST', 'ADMIN')
def get_custody_chain(evidence_id):
    """Get the full chain of custody for an evidence item. Analyst/Admin only."""
    # Verify evidence exists
    evidence, _ = find_row('Evidence_Metadata', 'evidence_id', evidence_id)
    if not evidence:
        return jsonify({"error": "Evidence not found"}), 404

    chain = get_chain(evidence_id)

    return jsonify({
        "status": "success",
        "evidence_id": evidence_id,
        "file_hash": evidence.get('file_hash'),
        "original_filename": evidence.get('original_filename'),
        "chain_of_custody": chain
    }), 200
