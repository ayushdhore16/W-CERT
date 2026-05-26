"""
W-CERT Dashboard Routes
Provides statistics, severity breakdowns, recent incidents, and trend data.
"""

from flask import Blueprint, jsonify, request
from ..security.auth import role_required
from ..database.sheets import get_all_rows, count_rows
from ..analysis.severity import get_severity_color, get_severity_description

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
@role_required('ANALYST', 'ADMIN')
def get_stats():
    """Get overall incident statistics."""
    incidents = get_all_rows('Incidents')
    total = len(incidents)

    # Count by status
    status_counts = {}
    severity_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}

    for inc in incidents:
        # Status
        status = inc.get('status', 'UNKNOWN')
        status_counts[status] = status_counts.get(status, 0) + 1

        # Severity
        sev = inc.get('severity', 'LOW')
        if sev in severity_counts:
            severity_counts[sev] += 1

    # Count other resources
    users_count = count_rows('Users')
    evidence_count = count_rows('Evidence_Metadata')
    escalation_count = count_rows('Escalations')

    return jsonify({
        "status": "success",
        "stats": {
            "total_incidents": total,
            "by_status": status_counts,
            "by_severity": severity_counts,
            "total_users": users_count,
            "total_evidence": evidence_count,
            "total_escalations": escalation_count,
            "open_incidents": status_counts.get('OPEN', 0),
            "critical_incidents": severity_counts.get('CRITICAL', 0)
        }
    }), 200


@dashboard_bp.route('/severity', methods=['GET'])
@role_required('ANALYST', 'ADMIN')
def get_severity_breakdown():
    """Get detailed severity breakdown with metadata."""
    incidents = get_all_rows('Incidents')

    severity_data = {}
    for level in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
        level_incidents = [i for i in incidents if i.get('severity') == level]
        severity_data[level] = {
            'count': len(level_incidents),
            'color': get_severity_color(level),
            'description': get_severity_description(level),
            'percentage': round(len(level_incidents) / len(incidents) * 100, 1) if incidents else 0
        }

    return jsonify({
        "status": "success",
        "severity_breakdown": severity_data,
        "total": len(incidents)
    }), 200


@dashboard_bp.route('/recent', methods=['GET'])
@role_required('ANALYST', 'ADMIN')
def get_recent_incidents():
    """Get the most recent incidents."""
    limit = request.args.get('limit', 10, type=int)
    limit = min(limit, 50)  # Cap at 50

    incidents = get_all_rows('Incidents')

    # Get last N incidents
    recent = incidents[-limit:] if len(incidents) > limit else incidents
    recent.reverse()  # Most recent first

    # Strip sensitive data
    safe_recent = []
    for inc in recent:
        safe_recent.append({
            'incident_id': inc.get('incident_id'),
            'attack_type': inc.get('attack_type'),
            'threat_score': inc.get('threat_score'),
            'severity': inc.get('severity'),
            'severity_color': get_severity_color(inc.get('severity', 'LOW')),
            'detected_tags': inc.get('detected_tags'),
            'status': inc.get('status'),
            'created_at': inc.get('created_at')
        })

    return jsonify({
        "status": "success",
        "count": len(safe_recent),
        "incidents": safe_recent
    }), 200


@dashboard_bp.route('/trends', methods=['GET'])
@role_required('ANALYST', 'ADMIN')
def get_trends():
    """
    Get threat trends over time.
    Groups incidents by date and severity.
    """
    incidents = get_all_rows('Incidents')

    # Group by date
    daily_counts = {}
    attack_type_counts = {}
    tag_counts = {}

    for inc in incidents:
        # Date grouping (extract date from timestamp)
        created = inc.get('created_at', '')
        date = created.split(' ')[0] if ' ' in created else created

        if date:
            if date not in daily_counts:
                daily_counts[date] = {'total': 0, 'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
            daily_counts[date]['total'] += 1
            sev = inc.get('severity', 'LOW')
            if sev in daily_counts[date]:
                daily_counts[date][sev] += 1

        # Attack type counts
        at = inc.get('attack_type', 'UNKNOWN')
        attack_type_counts[at] = attack_type_counts.get(at, 0) + 1

        # Tag frequency
        tags = inc.get('detected_tags', '')
        if tags:
            for tag in tags.split(', '):
                tag = tag.strip()
                if tag:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Sort tags by frequency
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:15]

    return jsonify({
        "status": "success",
        "trends": {
            "daily": daily_counts,
            "by_attack_type": attack_type_counts,
            "top_threat_indicators": [{"tag": t[0], "count": t[1]} for t in top_tags]
        }
    }), 200
