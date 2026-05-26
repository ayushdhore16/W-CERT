"""
W-CERT Escalation Routes
Handles escalation of incidents to authorities (Cyber Crime Cell, CERT-In, Women's Helpline).
"""

import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..security.auth import role_required, get_current_user_info
from ..security.audit import log_action, Actions
from ..database.sheets import append_row, find_row, find_rows, get_all_rows, update_row

escalation_bp = Blueprint('escalation', __name__)

# ── Escalation Targets ─────────────────────────────────────────
ESCALATION_TARGETS = {
    'CYBER_CRIME_CELL': {
        'name': 'Cyber Crime Cell',
        'description': 'National Cyber Crime Reporting Portal',
        'contact': 'cybercrime.gov.in',
        'helpline': '1930'
    },
    'CERT_IN': {
        'name': 'CERT-In',
        'description': 'Indian Computer Emergency Response Team',
        'contact': 'cert-in.org.in',
        'email': 'incident@cert-in.org.in'
    },
    'WOMEN_HELPLINE': {
        'name': "Women's Helpline",
        'description': 'National Commission for Women',
        'contact': 'ncw.nic.in',
        'helpline': '181 / 7827-170-170'
    }
}


@escalation_bp.route('/incidents/<incident_id>/escalate', methods=['POST'])
@role_required('ANALYST', 'ADMIN')
def escalate_incident(incident_id):
    """
    Escalate an incident to authorities.
    Creates an escalation record and updates incident status.
    """
    data = request.get_json() or {}

    # Validate incident exists
    incident, row_idx = find_row('Incidents', 'incident_id', incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    # Validate target
    escalate_to = data.get('escalate_to', '').upper()
    valid_targets = list(ESCALATION_TARGETS.keys())

    if escalate_to not in valid_targets:
        return jsonify({
            "error": f"Invalid escalation target. Must be one of: {', '.join(valid_targets)}",
            "available_targets": ESCALATION_TARGETS
        }), 400

    reason = data.get('reason', f'Severity: {incident.get("severity")} — Manual escalation by analyst')
    target_name = data.get('target_name')
    user = get_current_user_info()

    # Determine what to save in the database
    escalated_to_save = target_name if target_name else escalate_to

    # ── Create escalation record ───────────────────────────────
    escalation_id = str(uuid.uuid4())[:8].upper()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    escalation = {
        'escalation_id': escalation_id,
        'incident_id': incident_id,
        'escalated_by': user['user_id'],
        'escalated_to': escalated_to_save,
        'reason': reason,
        'status': 'PENDING',
        'created_at': timestamp
    }

    append_row('Escalations', escalation)

    # ── Update incident status ─────────────────────────────────
    update_row('Incidents', row_idx, {
        'status': 'ESCALATED',
        'updated_at': timestamp
    })

    # ── Audit log ──────────────────────────────────────────────
    log_action(user['user_id'], Actions.ESCALATION_CREATED, 'escalation', escalation_id,
               f'Incident {incident_id} escalated to {escalated_to_save}')

    target_info = ESCALATION_TARGETS[escalate_to]
    display_name = target_name if target_name else target_info['name']

    return jsonify({
        "status": "success",
        "message": f"Incident escalated to {display_name}",
        "escalation": {
            "escalation_id": escalation_id,
            "incident_id": incident_id,
            "escalated_to": target_info,
            "target_name": display_name,
            "escalation_status": "PENDING",
            "created_at": timestamp
        },
        "next_steps": [
            f"Contact {target_info['name']} at {target_info.get('contact', 'N/A')}",
            f"Helpline: {target_info.get('helpline', 'N/A')}",
            "Provide the incident ID and evidence hashes for reference",
            "Monitor escalation status for updates"
        ]
    }), 201


@escalation_bp.route('/escalations', methods=['GET'])
@role_required('ADMIN')
def list_escalations():
    """List all escalated cases. Admin only."""
    from ..security.encryption import decrypt_pii
    escalations = get_all_rows('Escalations')
    incidents = get_all_rows('Incidents')
    
    # Map incident_id to state
    incident_states = {}
    for inc in incidents:
        incident_states[inc.get('incident_id')] = inc.get('encrypted_state', '')

    # Enrich with target info
    enriched = []
    for esc in escalations:
        target_key = esc.get('escalated_to', '')
        target_info = ESCALATION_TARGETS.get(target_key, {'name': target_key})
        
        inc_id = esc.get('incident_id')
        enc_state = incident_states.get(inc_id, '')
        location = "Unknown"
        if enc_state:
            try:
                location = decrypt_pii(enc_state)
            except:
                pass
                
        enriched.append({
            **esc,
            'target_info': target_info,
            'location': location
        })

    return jsonify({
        "status": "success",
        "count": len(enriched),
        "escalations": enriched
    }), 200


@escalation_bp.route('/escalation-targets', methods=['GET'])
@role_required('ANALYST', 'ADMIN')
def get_escalation_targets():
    """Get available escalation targets and their contact information."""
    from .authorities import STATE_AUTHORITIES
    return jsonify({
        "status": "success",
        "targets": ESCALATION_TARGETS,
        "state_authorities": STATE_AUTHORITIES
    }), 200


@escalation_bp.route('/incidents/<incident_id>/docket', methods=['GET'])
@jwt_required()
def generate_escalation_docket(incident_id):
    """
    Generate a printable HTML escalation docket for an incident.
    Includes AI analysis summary, evidence hashes, IPC sections, and authority contacts.
    Designed to be handed off to law enforcement / CERT-In.
    """
    from ..database.sheets import find_rows
    from ..security.hashing import hash_content
    from ..security.encryption import decrypt_pii
    from .authorities import STATE_AUTHORITIES

    incident, _ = find_row('Incidents', 'incident_id', incident_id)
    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    # Fetch evidence list
    evidence_records = find_rows('Evidence', 'incident_id', incident_id)

    # Build evidence table rows
    evidence_rows = ''
    for ev in evidence_records:
        fname = ev.get('original_filename', 'N/A')
        fhash = ev.get('file_hash', 'N/A')
        ftype = ev.get('mime_type', 'N/A')
        fsize = ev.get('file_size', 'N/A')
        uploaded = ev.get('uploaded_at', 'N/A')
        evidence_rows += f"""
        <tr>
            <td>{fname}</td>
            <td>{ftype}</td>
            <td>{fsize}</td>
            <td class="hash">{fhash}</td>
            <td>{uploaded}</td>
        </tr>"""

    if not evidence_rows:
        evidence_rows = '<tr><td colspan="5" style="text-align:center;color:#888">No evidence files uploaded</td></tr>'

    # IPC sections
    ipc_raw = incident.get('ipc_sections', '')
    ipc_list = [s.strip() for s in ipc_raw.split(',') if s.strip()] if ipc_raw else ['IT Act 66 - Computer related offences']
    ipc_html = ''.join(f'<li>{s}</li>' for s in ipc_list)

    # Evidence gaps
    gaps_raw = incident.get('evidence_gaps', '')
    gaps_list = [s.strip() for s in gaps_raw.split(',') if s.strip()] if gaps_raw else []
    gaps_html = ''.join(f'<li>{g}</li>' for g in gaps_list) or '<li>No additional evidence gaps identified</li>'

    severity = incident.get('severity', 'UNKNOWN')
    severity_color = {
        'CRITICAL': '#dc2626', 'HIGH': '#ea580c', 'MEDIUM': '#ca8a04', 'LOW': '#16a34a'
    }.get(severity, '#6b7280')

    risk_level = incident.get('victim_risk_level', 'ACTIVE')
    risk_color = {
        'IMMEDIATE': '#dc2626', 'ACTIVE': '#ea580c', 'SUBSIDED': '#ca8a04', 'HISTORICAL': '#6b7280'
    }.get(risk_level, '#6b7280')

    timestamp_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    content_hash = incident.get('content_hash', 'N/A')

    # Decrypt state location
    enc_state = incident.get('encrypted_state', '')
    state_location = "Unknown"
    if enc_state:
        try:
            state_location = decrypt_pii(enc_state)
        except:
            pass

    state_authorities_html = ''
    if state_location in STATE_AUTHORITIES:
        sa = STATE_AUTHORITIES[state_location]
        state_authorities_html = f"""
        <div class="authority-box" style="background: #fdfcff; border-color: #6d28d9;">
            <h4 style="color: #6d28d9;">{sa['cyber_cell']['name']} (State Nodal Agency)</h4>
            <div>Email: {sa['cyber_cell'].get('email', 'N/A')}</div>
            <div>Helpline: {sa['cyber_cell'].get('phone', 'N/A')}</div>
            <div style="font-size:10px;color:#888;margin-top:4px;">Primary state-level Cyber Crime response unit for {state_location}.</div>
        </div>
        <div class="authority-box" style="background: #fdfcff; border-color: #6d28d9;">
            <h4 style="color: #6d28d9;">{sa['women_cell']['name']}</h4>
            <div>Email: {sa['women_cell'].get('email', 'N/A')}</div>
            <div>Helpline: {sa['women_cell'].get('phone', 'N/A')}</div>
            <div style="font-size:10px;color:#888;margin-top:4px;">State-level commission handling cases of violence against women.</div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>W-CERT Escalation Docket — {incident_id}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Courier New', monospace; color: #1a1a2e; background: #fff; padding: 40px; font-size: 12px; }}
        .header {{ border-bottom: 3px solid #1a1a2e; padding-bottom: 20px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-start; }}
        .logo {{ font-size: 22px; font-weight: bold; letter-spacing: 4px; }}
        .logo span {{ color: #6d28d9; }}
        .doc-meta {{ text-align: right; font-size: 10px; color: #555; line-height: 1.6; }}
        .classified {{ background: #1a1a2e; color: #fff; padding: 6px 16px; font-size: 11px; letter-spacing: 3px; text-align: center; margin-bottom: 24px; }}
        h2 {{ font-size: 13px; letter-spacing: 2px; text-transform: uppercase; border-bottom: 1px solid #ddd; padding-bottom: 6px; margin: 20px 0 12px; color: #1a1a2e; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 16px; }}
        th {{ background: #1a1a2e; color: #fff; padding: 8px; text-align: left; font-size: 10px; letter-spacing: 1px; }}
        td {{ padding: 8px; border-bottom: 1px solid #eee; vertical-align: top; }}
        td.hash {{ font-size: 9px; word-break: break-all; color: #555; }}
        .badge {{ display: inline-block; padding: 3px 10px; border-radius: 3px; color: #fff; font-weight: bold; font-size: 11px; }}
        .reasoning {{ background: #f8f8f8; border-left: 4px solid #6d28d9; padding: 12px; font-style: italic; color: #444; margin: 8px 0; }}
        ul {{ padding-left: 20px; line-height: 2; }}
        .authority-box {{ border: 1px solid #ddd; padding: 12px; margin-bottom: 8px; border-radius: 4px; }}
        .authority-box h4 {{ font-size: 11px; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; }}
        .footer {{ border-top: 2px solid #1a1a2e; margin-top: 32px; padding-top: 16px; font-size: 10px; color: #888; text-align: center; line-height: 1.8; }}
        @media print {{
            body {{ padding: 20px; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>

<div class="header">
    <div>
        <div class="logo">W‑<span>CERT</span></div>
        <div style="font-size:10px;color:#555;margin-top:4px;">Women's Cyber Emergency Response Team</div>
    </div>
    <div class="doc-meta">
        <div><strong>ESCALATION DOCKET</strong></div>
        <div>Generated: {timestamp_now}</div>
        <div>Incident ID: <strong>{incident_id}</strong></div>
        <div>Classification: RESTRICTED</div>
    </div>
</div>

<div class="classified">⚠ RESTRICTED — FOR AUTHORIZED PERSONNEL AND LAW ENFORCEMENT ONLY ⚠</div>

<h2>Incident Summary</h2>
<table>
    <tr><th style="width:30%">Field</th><th>Value</th></tr>
    <tr><td>Incident ID</td><td><strong>{incident_id}</strong></td></tr>
    <tr><td>Severity</td><td><span class="badge" style="background:{severity_color}">{severity}</span></td></tr>
    <tr><td>Attack Classification</td><td>{incident.get('attack_type', 'Unknown')}</td></tr>
    <tr><td>Victim Risk Level</td><td><span class="badge" style="background:{risk_color}">{risk_level}</span></td></tr>
    <tr><td>Identified Location (IP State)</td><td><strong>{state_location}</strong></td></tr>
    <tr><td>Authenticity Status</td><td>{incident.get('authenticity_status', 'N/A')}</td></tr>
    <tr><td>AI Threat Score</td><td>{incident.get('threat_score', 'N/A')} / 100</td></tr>
    <tr><td>Authenticity Score</td><td>{incident.get('authenticity_score', 'N/A')} / 100</td></tr>
    <tr><td>Current Status</td><td>{incident.get('status', 'OPEN')}</td></tr>
    <tr><td>Reported At</td><td>{incident.get('created_at', 'N/A')}</td></tr>
    <tr><td>Reporter ID (Anonymised)</td><td>{incident.get('reporter_id', 'N/A')}</td></tr>
</table>

<h2>Victim's Statement</h2>
<div class="reasoning" style="font-style:normal">
    {incident.get('description', 'No description provided.')}
</div>

<h2>AI Forensic Assessment</h2>
<div class="reasoning">{incident.get('ai_reasoning', 'AI reasoning not available.')}</div>

<h2>Applicable Legal Sections</h2>
<ul>{ipc_html}</ul>

<h2>Evidence Chain of Custody</h2>
<table>
    <tr>
        <th>Filename</th><th>Type</th><th>Size (bytes)</th><th>SHA-256 Hash</th><th>Uploaded At</th>
    </tr>
    {evidence_rows}
</table>
<div style="font-size:10px;color:#888;margin-top:-8px;">
    * Incident description hash: <span style="word-break:break-all">{content_hash}</span>
</div>

<h2>Evidence Gaps (Recommended for Stronger Case)</h2>
<ul>{gaps_html}</ul>

<h2>Target Escalation Authorities</h2>
{state_authorities_html}
{''.join(f"""
<div class="authority-box">
    <h4>{info['name']} (National)</h4>
    <div>Portal: {info.get('contact', 'N/A')}</div>
    <div>Helpline: {info.get('helpline', info.get('email', 'N/A'))}</div>
    <div style="font-size:10px;color:#888;margin-top:4px;">{info['description']}</div>
</div>""" for info in ESCALATION_TARGETS.values())}

<div class="footer">
    This document is auto-generated by the W-CERT Threat Intelligence Platform.<br>
    All PII is encrypted at rest (AES-256-GCM). Evidence integrity verified via SHA-256.<br>
    This docket does not constitute a legal complaint. Please file a formal FIR at your nearest police station or at cybercrime.gov.in.
</div>

<script>
    // Auto-print if opened directly
    window.onload = function() {{
        document.title = 'W-CERT Docket {incident_id}';
    }};
</script>
</body>
</html>"""

    from flask import Response
    return Response(html, mimetype='text/html'), 200
