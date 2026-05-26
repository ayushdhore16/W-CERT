"""
W-CERT Test Suite — Threat Analysis Engine
Tests the core threat analysis functionality.
"""

import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.analysis.threat_engine import analyze_threat, get_threat_summary
from app.analysis.severity import classify_severity, SeverityLevel, should_auto_escalate


class TestThreatEngine:
    """Tests for the threat analysis engine."""

    def test_phishing_description(self):
        """Phishing description should detect identity_theft keywords."""
        result = analyze_threat(
            "I received an email asking me to verify my password and login credentials. "
            "It said my account would be suspended if I didn't click the link urgently."
        )
        assert result['score'] > 0
        assert result['severity'] in ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
        assert 'password' in result['detected_tags'] or 'login' in result['detected_tags']
        assert result['attack_type'] in ('PHISHING', 'COMBINED', 'UNKNOWN')

    def test_sextortion_description(self):
        """Sextortion threats should score HIGH or CRITICAL."""
        result = analyze_threat(
            "Someone is threatening to leak my private photos and intimate images "
            "unless I send them money. They are blackmailing me and threatening to "
            "share publicly on social media."
        )
        assert result['score'] >= 50
        assert result['severity'] in ('HIGH', 'CRITICAL')
        assert 'sextortion' in result['attack_vectors']
        assert result['auto_escalate'] or result['severity'] == 'HIGH'

    def test_financial_fraud_description(self):
        """Financial fraud should detect relevant keywords."""
        result = analyze_threat(
            "I received a message saying I won a lottery prize and need to make a "
            "UPI payment to claim it. They asked for my bank details."
        )
        assert result['score'] > 0
        assert 'financial_fraud' in result['attack_vectors']
        assert any(tag in result['detected_tags'] for tag in ['lottery', 'upi', 'bank', 'payment'])

    def test_impersonation_description(self):
        """Authority impersonation should be detected."""
        result = analyze_threat(
            "Someone called pretending to be from the police saying there is an "
            "arrest warrant against me and I need to pay a fine immediately."
        )
        assert result['score'] > 0
        assert 'impersonation' in result['attack_vectors']

    def test_empty_description(self):
        """Empty description should return LOW severity with score 0."""
        result = analyze_threat("")
        assert result['score'] == 0
        assert result['severity'] == 'LOW'
        assert result['detected_tags'] == []

    def test_benign_description(self):
        """Benign text with no threat indicators should score LOW."""
        result = analyze_threat(
            "I had a wonderful day at work today. The weather was nice and I "
            "enjoyed my lunch at the cafeteria."
        )
        assert result['score'] == 0 or result['severity'] == 'LOW'

    def test_combined_attack(self):
        """Description with both phishing and SE indicators."""
        result = analyze_threat(
            "I got a suspicious email with a link to a fake login page. Someone "
            "also called me on WhatsApp pretending to be from my bank asking for "
            "my OTP and password."
        )
        assert result['score'] > 0
        assert result['attack_type'] in ('COMBINED', 'PHISHING', 'SOCIAL_ENGINEERING')

    def test_recommendations_generated(self):
        """Analysis should always include recommendations."""
        result = analyze_threat("Someone asked for my password via email")
        assert len(result['recommendations']) > 0

    def test_category_scores_present(self):
        """Category score breakdown should be included."""
        result = analyze_threat("Someone is blackmailing me with private photos for money")
        assert isinstance(result['category_scores'], dict)
        assert len(result['category_scores']) > 0

    def test_threat_summary(self):
        """Human-readable summary should be generated."""
        result = analyze_threat("Urgent: Your account will be locked. Verify your password now.")
        summary = get_threat_summary(result)
        assert 'Threat Level:' in summary
        assert 'Score:' in summary


class TestSeverity:
    """Tests for severity classification."""

    def test_low_severity(self):
        assert classify_severity(0) == SeverityLevel.LOW
        assert classify_severity(10) == SeverityLevel.LOW
        assert classify_severity(24) == SeverityLevel.LOW

    def test_medium_severity(self):
        assert classify_severity(25) == SeverityLevel.MEDIUM
        assert classify_severity(40) == SeverityLevel.MEDIUM
        assert classify_severity(49) == SeverityLevel.MEDIUM

    def test_high_severity(self):
        assert classify_severity(50) == SeverityLevel.HIGH
        assert classify_severity(60) == SeverityLevel.HIGH
        assert classify_severity(74) == SeverityLevel.HIGH

    def test_critical_severity(self):
        assert classify_severity(75) == SeverityLevel.CRITICAL
        assert classify_severity(100) == SeverityLevel.CRITICAL
        assert classify_severity(200) == SeverityLevel.CRITICAL

    def test_auto_escalate_critical_only(self):
        assert should_auto_escalate(SeverityLevel.CRITICAL) is True
        assert should_auto_escalate(SeverityLevel.HIGH) is False
        assert should_auto_escalate(SeverityLevel.LOW) is False


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
