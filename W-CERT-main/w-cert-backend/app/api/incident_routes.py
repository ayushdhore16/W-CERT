"""
W-CERT Incident Routes
CRUD operations for incident reports with threat analysis.
"""

import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..security.auth import role_required, get_current_user_info
from ..security.encryption import encrypt_pii
from ..security.hashing import hash_content
from ..security.audit import log_action, Actions
from ..analysis.threat_engine import analyze_threat
from ..analysis.verification_engine import verify_authenticity
from ..database.sheets import append_row, get_all_rows, find_row, update_row, find_rows

incident_bp = Blueprint('incidents', __name__)


@incident_bp.route('', methods=['POST'])
@jwt_required()
def submit_incident():
    """
    Submit a new incident report.
    Automatically performs threat analysis and severity classification.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    description = data.get('description', '').strip()
    if not description:
        return jsonify({"error": "Incident description is required"}), 400

    user = get_current_user_info()

    # ── Get reporter details ───────────────────────────────────
    reporter_name = data.get('name', 'Anonymous')
    reporter_contact = data.get('contact', 'N/A')
    state_location = data.get('state_location', 'Unknown')

    # ── Unified AI Analysis (Gemini Vision) ─────────────────────
    # verify_authenticity now returns BOTH threat + authenticity scores
    # when Gemini is available. Falls back to rule-based if not.
    auth_check = verify_authenticity(description, [])  # No evidence yet at submission
    
    # Use Gemini's scores if AI-powered, else fall back to keyword engine
    if auth_check.get('ai_powered'):
        threat_score = auth_check['threat_score']
        severity = auth_check['severity']
        attack_type = auth_check['attack_type']
        detected_tags = auth_check.get('verification_insights', [])
    else:
        # Fallback: use old keyword-based engine
        analysis = analyze_threat(description)
        threat_score = analysis['score']
        severity = analysis['severity']
        attack_type = analysis['attack_type']
        detected_tags = analysis['detected_tags']

    # ── Encrypt PII ────────────────────────────────────────────
    encrypted_name = encrypt_pii(reporter_name)
    encrypted_contact = encrypt_pii(reporter_contact)
    encrypted_state = encrypt_pii(state_location)

    # ── Hash for integrity ─────────────────────────────────────
    content_hash = hash_content(description)

    # ── Build incident record ──────────────────────────────────
    incident_id = str(uuid.uuid4())[:8].upper()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    incident = {
        'incident_id': incident_id,
        'reporter_id': user['user_id'],
        'encrypted_name': encrypted_name,
        'encrypted_contact': encrypted_contact,
        'encrypted_state': encrypted_state,
        'description': description,
        'attack_type': attack_type,
        'threat_score': str(threat_score),
        'severity': severity,
        'detected_tags': ', '.join(detected_tags) if isinstance(detected_tags, list) else detected_tags,
        'content_hash': content_hash,
        'status': 'OPEN',
        'authenticity_score': str(auth_check['authenticity_score']),
        'authenticity_status': auth_check['authenticity_status'],
        'verification_insights': ', '.join(auth_check['verification_insights']) if isinstance(auth_check['verification_insights'], list) else auth_check['verification_insights'],
        'ai_reasoning': auth_check.get('reasoning', ''),
        'victim_risk_level': auth_check.get('victim_risk_level', 'ACTIVE'),
        'ipc_sections': ', '.join(auth_check.get('ipc_sections', [])),
        'evidence_gaps': ', '.join(auth_check.get('evidence_gaps', [])),
        'score_breakdown': str(auth_check.get('score_breakdown', {})),
        'created_at': timestamp,
        'updated_at': timestamp
    }

    # ── Save to Sheets ─────────────────────────────────────────
    append_row('Incidents', incident)

    # ── Audit log ──────────────────────────────────────────────
    log_action(user['user_id'], Actions.REPORT_SUBMITTED, 'incident', incident_id,
               f'Severity: {severity}, Score: {threat_score}, AI: {auth_check.get("ai_powered", False)}')

    return jsonify({
        "status": "success",
        "message": "Incident report submitted and analyzed by Gemini AI",
        "incident": {
            "incident_id": incident_id,
            "severity": severity,
            "threat_score": threat_score,
            "attack_type": attack_type,
            "authenticity_score": auth_check['authenticity_score'],
            "authenticity_status": auth_check['authenticity_status'],
            "victim_risk_level": auth_check.get('victim_risk_level', 'ACTIVE'),
            "ipc_sections": auth_check.get('ipc_sections', []),
            "evidence_gaps": auth_check.get('evidence_gaps', []),
            "score_breakdown": auth_check.get('score_breakdown', {}),
            "ai_reasoning": auth_check.get('reasoning', ''),
            "verification_insights": auth_check['verification_insights'],
            "status": "OPEN",
            "content_hash": content_hash[:16] + '...',
            "created_at": timestamp
        }
    }), 201


@incident_bp.route('', methods=['GET'])
@jwt_required()
def list_incidents():
    """
    List incident reports.
    - USER role: sees only their own incidents.
    - ANALYST/ADMIN: sees all incidents.
    """
    user = get_current_user_info()
    all_incidents = get_all_rows('Incidents')
    print(f"[DEBUG] Fetching incidents for {user['email']} (Role: {user['role']})")
    print(f"[DEBUG] Total raw incidents in DB: {len(all_incidents)}")

    # Filter by role
    if user['role'] == 'USER':
        incidents = [i for i in all_incidents if i.get('reporter_id') == user['user_id']]
    else:
        incidents = all_incidents

    print(f"[DEBUG] Incidents after role filter: {len(incidents)}")

    # Optional severity filter
    severity_filter = request.args.get('severity')
    if severity_filter:
        incidents = [i for i in incidents if i.get('severity') == severity_filter.upper()]

    # Optional status filter
    status_filter = request.args.get('status')
    if status_filter:
        incidents = [i for i in incidents if i.get('status') == status_filter.upper()]

    # Strip sensitive fields for response
    safe_incidents = []
    for inc in incidents:
        safe_incidents.append({
            'incident_id': inc.get('incident_id'),
            'attack_type': inc.get('attack_type'),
            'threat_score': inc.get('threat_score'),
            'severity': inc.get('severity'),
            'detected_tags': [t.strip() for t in inc.get('detected_tags', '').split(',')] if inc.get('detected_tags') else [],
            'status': inc.get('status'),
            'authenticity_score': inc.get('authenticity_score', '50'),
            'authenticity_status': inc.get('authenticity_status', 'POTENTIALLY_AUTHENTIC'),
            'victim_risk_level': inc.get('victim_risk_level', 'ACTIVE'),
            'verification_insights': [t.strip() for t in inc.get('verification_insights', '').split(',')] if inc.get('verification_insights') else [],
            'ai_reasoning': inc.get('ai_reasoning', ''),
            'created_at': inc.get('created_at'),
            'updated_at': inc.get('updated_at')
        })

    return jsonify({
        "status": "success",
        "count": len(safe_incidents),
        "incidents": safe_incidents
    }), 200


@incident_bp.route('/<incident_id>', methods=['GET'])
@jwt_required()
def get_incident(incident_id):
    """Get detailed view of a specific incident."""
    user = get_current_user_info()
    incident, row_idx = find_row('Incidents', 'incident_id', incident_id)

    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    # Access control: users can only view their own
    if user['role'] == 'USER' and incident.get('reporter_id') != user['user_id']:
        return jsonify({"error": "Access denied"}), 403

    # Audit log
    log_action(user['user_id'], Actions.REPORT_VIEWED, 'incident', incident_id)

    # Remove redundant real-time verification to fix 429/loading issues.
    # We now rely on data stored during submission/upload.

    # Build response (include description for authorized viewers)
    response_data = {
        'incident_id': incident.get('incident_id'),
        'attack_type': incident.get('attack_type'),
        'threat_score': incident.get('threat_score'),
        'severity': incident.get('severity'),
        'detected_tags': [t.strip() for t in incident.get('detected_tags', '').split(',')] if incident.get('detected_tags') else [],
        'content_hash': incident.get('content_hash'),
        'status': incident.get('status'),
        'description': incident.get('description'),
        'authenticity_score': incident.get('authenticity_score', '50'),
        'authenticity_status': incident.get('authenticity_status', 'POTENTIALLY_AUTHENTIC'),
        'victim_risk_level': incident.get('victim_risk_level', 'ACTIVE'),
        'ipc_sections': [s.strip() for s in incident.get('ipc_sections', '').split(',')] if incident.get('ipc_sections') else [],
        'evidence_gaps': [s.strip() for s in incident.get('evidence_gaps', '').split(',')] if incident.get('evidence_gaps') else [],
        'verification_insights': [t.strip() for t in incident.get('verification_insights', '').split(',')] if incident.get('verification_insights') else [],
        'ai_reasoning': incident.get('ai_reasoning', ''),
        'created_at': incident.get('created_at'),
        'updated_at': incident.get('updated_at')
    }

    # Only ANALYST/ADMIN can see encrypted PII fields
    if user['role'] in ('ANALYST', 'ADMIN'):
        from ..security.encryption import decrypt_pii
        response_data['encrypted_name'] = incident.get('encrypted_name')
        response_data['encrypted_contact'] = incident.get('encrypted_contact')
        
        enc_state = incident.get('encrypted_state', '')
        state_location = "Unknown"
        if enc_state:
            try:
                state_location = decrypt_pii(enc_state)
            except:
                pass
        response_data['state_location'] = state_location
        response_data['reporter_id'] = incident.get('reporter_id')

    return jsonify({"status": "success", "incident": response_data}), 200


@incident_bp.route('/<incident_id>/status', methods=['PATCH'])
@role_required('ANALYST', 'ADMIN')
def update_incident_status(incident_id):
    """
    Update the status of an incident.
    Only ANALYST and ADMIN roles can perform this action.
    Valid statuses: OPEN, TRIAGED, INVESTIGATING, ESCALATED, RESOLVED, CLOSED
    """
    data = request.get_json()
    new_status = data.get('status', '').upper()

    valid_statuses = {'OPEN', 'TRIAGED', 'INVESTIGATING', 'ESCALATED', 'RESOLVED', 'CLOSED'}
    if new_status not in valid_statuses:
        return jsonify({
            "error": f"Invalid status. Must be one of: {', '.join(sorted(valid_statuses))}"
        }), 400

    incident, row_idx = find_row('Incidents', 'incident_id', incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    # Update status and timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    update_row('Incidents', row_idx, {
        'status': new_status,
        'updated_at': timestamp
    })

    user = get_current_user_info()
    log_action(user['user_id'], Actions.STATUS_UPDATED, 'incident', incident_id,
               f'Status changed: {incident.get("status")} → {new_status}')

    return jsonify({
        "status": "success",
        "message": f"Incident status updated to {new_status}",
        "incident_id": incident_id,
        "new_status": new_status,
        "updated_at": timestamp
    }), 200

@incident_bp.route('/<incident_id>/similar', methods=['GET'])
@jwt_required()
def get_similar_incidents(incident_id):
    """
    Get similar past incidents (RAG UI).
    Uses the heuristic similarity engine.
    """
    from ..analysis.similarity import find_similar_cases
    from ..analysis.threat_engine import analyze_threat

    incident, _ = find_row('Incidents', 'incident_id', incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    # We need the base tags and attack type to compare against
    attack_type = incident.get('attack_type', 'Unknown')
    tags_raw = incident.get('detected_tags', '')
    
    # If it's an old record without tags, quickly re-analyze description
    if not tags_raw and incident.get('description'):
        analysis = analyze_threat(incident.get('description'))
        tags = analysis['detected_tags']
    else:
        tags = [t.strip() for t in tags_raw.split(',') if t.strip()]

    all_incidents = get_all_rows('Incidents')
    
    similar_cases = find_similar_cases(
        target_desc=incident.get('description', ''),
        target_attack_type=attack_type,
        target_tags=tags,
        all_incidents=all_incidents,
        target_id=incident_id,
        limit=3
    )

    return jsonify({
        "status": "success",
        "similar_cases": similar_cases
    }), 200
