"""
W-CERT Authenticity Verification Engine — Gemini Vision Edition
Uses Google Gemini 1.5 Flash to perform real AI-powered analysis of:
  - Uploaded evidence (images, PDFs, screenshots)
  - The victim's written description
  - Combined threat + authenticity scoring
"""

import os
import json
import base64
import mimetypes
from pathlib import Path
from dotenv import load_dotenv
from ..security.encryption import encrypt_pii
from ..database.sheets import get_all_rows
from .threat_engine import analyze_threat
from .similarity import find_similar_cases

load_dotenv()

# ── Gemini SDK (new google-genai package) ──────────────────────────
try:
    from google import genai
    from google.genai import types as genai_types
    _GEMINI_KEY = os.getenv('GEMINI_API_KEY')
    if _GEMINI_KEY:
        _gemini_client = genai.Client(api_key=_GEMINI_KEY)
        _GEMINI_AVAILABLE = True
    else:
        _gemini_client = None
        _GEMINI_AVAILABLE = False
except ImportError:
    _gemini_client = None
    _GEMINI_AVAILABLE = False


# ── Forensic Prompt Template (4-Step Framework) ───────────────────────────
_ANALYSIS_PROMPT = """
You are a senior cybercrime forensic analyst for W-CERT (Women's Cyber Emergency Response Team), specializing in crimes against women in India.

A victim has submitted an incident report. Analyze it using this structured forensic framework:

VICTIM'S DESCRIPTION:
"{description}"

EVIDENCE FILES PROVIDED: {file_count} file(s)
{file_descriptions}

{rag_context}

---
FORENSIC ANALYSIS FRAMEWORK:

STEP 1 — EVIDENCE AUTHENTICITY
Does the uploaded evidence (if any) match the victim's description?
- Rate each piece of evidence for: relevance, credibility, and signs of tampering.
- If no evidence is uploaded for a serious claim (sextortion, blackmail, financial fraud), authenticity_score must be 20–40.
- If evidence clearly shows threatening language, financial demands, or intimate content threats matching the description, authenticity_score must be 70–95.

STEP 2 — THREAT VECTOR CLASSIFICATION
Identify the PRIMARY attack type from:
[Sextortion, Financial Fraud, Identity Theft, Impersonation, Phishing, Stalking, Online Harassment, Morphed Image Abuse, Deepfake Threat, Ransomware, Social Engineering, Unknown]

STEP 3 — VICTIM RISK ASSESSMENT
Is the victim in ongoing danger?
- IMMEDIATE: Active threat, perpetrator has leverage or access
- ACTIVE: Ongoing harassment/fraud, victim still at risk
- SUBSIDED: Attack appears to have stopped
- HISTORICAL: Past incident, no ongoing threat

STEP 4 — EVIDENCE QUALITY & GAPS
What additional evidence would strengthen this case for law enforcement?

---
Return ONLY this valid JSON object, no other text:
{{
  "authenticity_score": <integer 0-100>,
  "threat_score": <integer 0-100>,
  "severity": "<CRITICAL|HIGH|MEDIUM|LOW>",
  "authenticity_status": "<HIGHLY_AUTHENTIC|POTENTIALLY_AUTHENTIC|LOW_AUTHENTICITY>",
  "attack_type": "<primary attack type from Step 2>",
  "victim_risk_level": "<IMMEDIATE|ACTIVE|SUBSIDED|HISTORICAL>",
  "evidence_gaps": ["<what additional evidence is needed>", "<another gap>"],
  "ipc_sections": ["<relevant IPC/IT Act section e.g. IPC 354D - Stalking>", "<another section>"],
  "verification_insights": [
    "<specific observation from evidence or description>",
    "<another observation>"
  ],
  "score_breakdown": {{
    "evidence_match": <integer 0-40>,
    "threat_indicators": <integer 0-30>,
    "urgency_signals": <integer 0-20>,
    "victim_vulnerability": <integer 0-10>
  }},
  "reasoning": "<2-3 sentence forensic explanation of your assessment>"
}}

Scoring guidelines for score_breakdown (must sum approximately to threat_score):
- evidence_match: How well evidence supports the claim (0-40)
- threat_indicators: Severity of attack type and perpetrator capability (0-30)
- urgency_signals: Time pressure, deadlines, payment demands (0-20)
- victim_vulnerability: Emotional state, repeat targeting, isolation tactics (0-10)

Return ONLY the JSON object, no other text.
"""


def _encode_file_for_gemini(file_path: str) -> dict | None:
    """Encode a file as base64 for Gemini multimodal input."""
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        
        mime_type, _ = mimetypes.guess_type(str(path))
        if not mime_type:
            # Fallback detection
            with open(file_path, 'rb') as f:
                header = f.read(4)
            if header.startswith(b'\x89PNG'):
                mime_type = 'image/png'
            elif header.startswith(b'\xff\xd8'):
                mime_type = 'image/jpeg'
            elif header.startswith(b'%PDF'):
                mime_type = 'application/pdf'
            else:
                mime_type = 'application/octet-stream'
        
        # Gemini supports: image/png, image/jpeg, image/gif, image/webp, application/pdf
        supported = {'image/png', 'image/jpeg', 'image/gif', 'image/webp', 'application/pdf'}
        if mime_type not in supported:
            return None
        
        with open(file_path, 'rb') as f:
            data = base64.b64encode(f.read()).decode('utf-8')
        
        return {
            'mime_type': mime_type,
            'data': data
        }
    except Exception:
        return None


def _gemini_analyze(description: str, evidence_list: list) -> dict:
    """Send description + evidence to Gemini Vision for analysis."""
    # Build content parts list
    content_parts = []
    file_descriptions = []
    
    for ev in evidence_list:
        file_path = ev.get('storage_path', '')
        filename = ev.get('original_filename', 'unknown')
        
        encoded = _encode_file_for_gemini(file_path)
        if encoded:
            # New SDK uses inline_data parts
            content_parts.append(
                genai_types.Part.from_bytes(
                    data=base64.b64decode(encoded['data']),
                    mime_type=encoded['mime_type']
                )
            )
            file_descriptions.append(f"- {filename} ({encoded['mime_type']})")
        else:
            file_descriptions.append(f"- {filename} (could not be read)")
    
    # --- RAG INJECTION ---
    rag_context = ""
    try:
        all_incidents = get_all_rows('Incidents')
        # Lightweight heuristic baseline
        baseline = analyze_threat(description)
        similar = find_similar_cases(
            target_desc=description, 
            target_attack_type=baseline['attack_type'], 
            target_tags=baseline['detected_tags'], 
            all_incidents=all_incidents, 
            limit=2
        )
        if similar:
            rag_context = "--- HISTORICAL CONTEXT (RAG) ---\n"
            rag_context += "Here are similar past cases and how they were classified. Use these as precedent if relevant:\n"
            for s in similar:
                rag_context += f"- Case ID {s['incident_id']}: Classified as '{s['attack_type']}' (Severity: {s['severity']}). Context: {s['description'][:150]}...\n"
    except Exception as e:
        print(f"RAG context generation failed: {e}")

    # Build the text prompt
    prompt = _ANALYSIS_PROMPT.format(
        description=description or "No description provided.",
        file_count=len(evidence_list),
        file_descriptions='\n'.join(file_descriptions) if file_descriptions else "No files uploaded.",
        rag_context=rag_context
    )
    
    # Text prompt goes first
    content_parts.insert(0, prompt)
    
    response = _gemini_client.models.generate_content(
        model='gemini-2.0-flash',
        contents=content_parts
    )
    
    # Parse JSON from response
    raw = response.text.strip()
    # Strip markdown code fences if present
    if raw.startswith('```'):
        raw = raw.split('```')[1]
        if raw.startswith('json'):
            raw = raw[4:]
    
    return json.loads(raw.strip())


def _fallback_analyze(description: str, evidence_list: list) -> dict:
    """Rule-based fallback when Gemini is unavailable."""
    score = 50
    insights = []
    desc_lower = (description or '').lower()

    # Negation guard — exclude negated keyword matches
    negations = ['not ', 'no ', "wasn't", "didn't", "don't", "never "]
    def keyword_active(kw):
        idx = desc_lower.find(kw)
        if idx == -1:
            return False
        # Check the 15 chars before the keyword for negation words
        prefix = desc_lower[max(0, idx - 15):idx]
        return not any(neg in prefix for neg in negations)

    high_stakes = any(keyword_active(kw) for kw in [
        'sextortion', 'private', 'leak', 'blackmail', 'morphed',
        'nude', 'intimate', 'ransom', 'threat'
    ])

    if high_stakes and not evidence_list:
        score -= 30
        insights.append("High-stakes claim made without supporting evidence.")
    elif high_stakes and evidence_list:
        score += 15
        insights.append("Supporting evidence provided for sensitive claim.")

    if not description or len(description) < 20:
        score -= 15
        insights.append("Extremely brief description reduces credibility.")

    if len(evidence_list) > 2:
        score += 10
        insights.append("Multiple evidence files provided — improves case strength.")

    final = max(0, min(100, score))

    # Determine threat score + attack type from keywords
    threat_map = {
        'sextortion': (90, 'Sextortion'),
        'blackmail': (85, 'Blackmail'),
        'ransom': (80, 'Ransomware'),
        'morphed': (82, 'Morphed Image Abuse'),
        'deepfake': (82, 'Deepfake Threat'),
        'phishing': (65, 'Phishing'),
        'fraud': (70, 'Financial Fraud'),
        'hack': (60, 'Identity Theft'),
        'threat': (55, 'Online Harassment'),
        'stalk': (65, 'Stalking'),
    }
    threat_score = 40
    attack_type = 'General Cybercrime'
    for kw, (ts, at) in threat_map.items():
        if keyword_active(kw):
            threat_score = ts
            attack_type = at
            break

    severity = 'CRITICAL' if threat_score >= 85 else 'HIGH' if threat_score >= 65 else 'MEDIUM' if threat_score >= 45 else 'LOW'
    status = 'HIGHLY_AUTHENTIC' if final >= 75 else 'POTENTIALLY_AUTHENTIC' if final >= 40 else 'LOW_AUTHENTICITY'

    # Victim risk level heuristic
    risk_keywords = ['immediately', 'threatening', 'calling', 'still', 'ongoing', 'now', 'today']
    victim_risk = 'ACTIVE' if any(keyword_active(k) for k in risk_keywords) else 'HISTORICAL'
    if high_stakes and not evidence_list:
        victim_risk = 'IMMEDIATE'

    # IPC sections mapping
    ipc_map = {
        'Sextortion': ['IPC 354C - Voyeurism', 'IT Act 66E - Privacy violation', 'IPC 383 - Extortion'],
        'Stalking': ['IPC 354D - Stalking', 'IT Act 67 - Obscene material'],
        'Phishing': ['IT Act 66C - Identity theft', 'IT Act 66D - Cheating by personation'],
        'Financial Fraud': ['IPC 420 - Cheating', 'IT Act 66C - Identity theft'],
        'Blackmail': ['IPC 383 - Extortion', 'IPC 503 - Criminal intimidation'],
        'Identity Theft': ['IT Act 66C - Identity theft', 'IPC 419 - Cheating by impersonation'],
        'Morphed Image Abuse': ['IPC 499 - Defamation', 'IT Act 67A - Obscene act', 'IPC 354C'],
    }
    ipc_sections = ipc_map.get(attack_type, ['IT Act 66 - Computer related offences', 'IPC 509 - Insulting modesty'])

    # Evidence gaps
    evidence_gaps = []
    if not evidence_list:
        evidence_gaps.append("Upload screenshots of threatening messages")
        evidence_gaps.append("Provide chat exports or email headers")
    if attack_type in ('Financial Fraud', 'Phishing'):
        evidence_gaps.append("Bank transaction records or UPI screenshots")
    if attack_type in ('Sextortion', 'Morphed Image Abuse', 'Deepfake Threat'):
        evidence_gaps.append("Original images for forensic comparison")

    # Score breakdown
    evidence_match = min(40, (15 if evidence_list else 0) + (10 if final >= 60 else 0))
    threat_indicators = min(30, int(threat_score * 0.3))
    urgency_signals = 10 if any(keyword_active(k) for k in ['urgent', 'deadline', 'immediately', 'within 24', 'final warning']) else 0
    victim_vuln = 5 if high_stakes else 0

    return {
        'authenticity_score': final,
        'threat_score': threat_score,
        'severity': severity,
        'authenticity_status': status,
        'attack_type': attack_type,
        'victim_risk_level': victim_risk,
        'ipc_sections': ipc_sections,
        'evidence_gaps': evidence_gaps,
        'verification_insights': insights,
        'score_breakdown': {
            'evidence_match': evidence_match,
            'threat_indicators': threat_indicators,
            'urgency_signals': urgency_signals,
            'victim_vulnerability': victim_vuln
        },
        'reasoning': 'Analyzed using rule-based heuristics (Gemini AI unavailable). AI-powered analysis will run when quota resets.'
    }


def verify_authenticity(description: str, evidence_list: list = None) -> dict:
    """
    Main entry point. Analyzes a report using Gemini Vision if available,
    falls back to rule-based scoring otherwise.
    
    Returns a unified dict with both authenticity AND threat scoring.
    """
    import time
    
    if evidence_list is None:
        evidence_list = []
    
    if _GEMINI_AVAILABLE:
        # Retry up to 2 times for rate-limit (429) errors
        last_error = None
        for attempt in range(3):
            try:
                result = _gemini_analyze(description, evidence_list)
                result.setdefault('authenticity_score', 50)
                result.setdefault('threat_score', 50)
                result.setdefault('severity', 'MEDIUM')
                result.setdefault('authenticity_status', 'POTENTIALLY_AUTHENTIC')
                result.setdefault('attack_type', 'Unknown')
                result.setdefault('victim_risk_level', 'ACTIVE')
                result.setdefault('ipc_sections', [])
                result.setdefault('evidence_gaps', [])
                result.setdefault('verification_insights', [])
                result.setdefault('score_breakdown', {
                    'evidence_match': 0, 'threat_indicators': 0,
                    'urgency_signals': 0, 'victim_vulnerability': 0
                })
                result.setdefault('reasoning', '')
                result['files_analyzed'] = len(evidence_list)
                result['ai_powered'] = True
                return result
            except Exception as e:
                last_error = e
                err_str = str(e)
                # If rate limited, wait and retry
                if '429' in err_str or 'RESOURCE_EXHAUSTED' in err_str:
                    wait = 40 * (attempt + 1)  # 40s, 80s
                    print(f"[Gemini] Rate limited. Waiting {wait}s before retry {attempt + 1}/2...")
                    time.sleep(wait)
                    continue
                # For other errors, fall back immediately
                break
        
        # All retries exhausted — use fallback
        result = _fallback_analyze(description, evidence_list)
        result['verification_insights'].append(
            f"[AI analysis pending — rate limit reached. Rule-based score used.]"
        )
        result['ai_powered'] = False
        result['files_analyzed'] = len(evidence_list)
        return result
    else:
        result = _fallback_analyze(description, evidence_list)
        result['ai_powered'] = False
        result['files_analyzed'] = len(evidence_list)
        return result
