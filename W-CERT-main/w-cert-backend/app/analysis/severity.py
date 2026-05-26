"""
W-CERT Severity Classification Module
Maps threat scores to severity levels with configurable thresholds.
"""

from enum import Enum


class SeverityLevel(Enum):
    """Severity levels for incident classification."""
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'


# ── Default Thresholds ─────────────────────────────────────────
SEVERITY_THRESHOLDS = {
    'CRITICAL': 75,
    'HIGH': 50,
    'MEDIUM': 25,
    'LOW': 0
}


def classify_severity(score):
    """
    Classify a threat score into a severity level.
    
    Args:
        score (int): Threat analysis score.
    
    Returns:
        SeverityLevel: The classified severity level.
    """
    if score >= SEVERITY_THRESHOLDS['CRITICAL']:
        return SeverityLevel.CRITICAL
    elif score >= SEVERITY_THRESHOLDS['HIGH']:
        return SeverityLevel.HIGH
    elif score >= SEVERITY_THRESHOLDS['MEDIUM']:
        return SeverityLevel.MEDIUM
    else:
        return SeverityLevel.LOW


def should_auto_escalate(severity):
    """
    Determine if an incident should be auto-escalated based on severity.
    CRITICAL incidents are flagged for immediate escalation.
    
    Args:
        severity (SeverityLevel): The incident severity.
    
    Returns:
        bool: True if auto-escalation is recommended.
    """
    return severity == SeverityLevel.CRITICAL


def get_severity_color(severity):
    """Get display color for severity level (for dashboard use)."""
    colors = {
        SeverityLevel.LOW: '#28a745',       # Green
        SeverityLevel.MEDIUM: '#ffc107',    # Yellow
        SeverityLevel.HIGH: '#fd7e14',      # Orange
        SeverityLevel.CRITICAL: '#dc3545'   # Red
    }
    if isinstance(severity, str):
        severity = SeverityLevel(severity)
    return colors.get(severity, '#6c757d')


def get_severity_description(severity):
    """Get human-readable description for each severity level."""
    descriptions = {
        SeverityLevel.LOW: 'Low risk — informational, no immediate threat detected.',
        SeverityLevel.MEDIUM: 'Moderate risk — potential threat indicators found, monitoring advised.',
        SeverityLevel.HIGH: 'High risk — strong threat indicators, immediate review required.',
        SeverityLevel.CRITICAL: 'Critical — active threat detected, immediate action and escalation required.'
    }
    if isinstance(severity, str):
        severity = SeverityLevel(severity)
    return descriptions.get(severity, 'Unknown severity level.')
