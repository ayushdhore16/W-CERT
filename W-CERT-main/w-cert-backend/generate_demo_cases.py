import sys
import os
import uuid
import random
from datetime import datetime, timedelta

# Add current directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database.sheets import get_sheet, SHEET_SCHEMAS
from app.security.encryption import encrypt_pii
from app.security.hashing import hash_content
from app.api.authorities import STATE_AUTHORITIES

app = create_app()

INDIAN_STATES = list(STATE_AUTHORITIES.keys())

CASE_TEMPLATES = [
    {
        "type": "SEXTORTION",
        "severity": "CRITICAL",
        "description": "I received an email saying they hacked my webcam and have a video of me changing. They included a password I actually used to use years ago to prove it. They are demanding $2000 in Bitcoin to a wallet address or they will send the video to all my LinkedIn and Instagram contacts. I am terrified.",
        "threat_score": 88,
        "victim_risk_level": "IMMEDIATE",
        "ipc_sections": "IPC Sec 384 - Extortion, IT Act 66E - Violation of Privacy, IT Act 67A - Transmitting sexually explicit material",
        "evidence_gaps": "Original email headers (.eml file) required to trace source IP. Blockchain transaction ID if any payment was made.",
        "ai_reasoning": "High-confidence sextortion scam. The inclusion of an old password indicates data sourced from a historic public breach (credential stuffing), not an active webcam hack. However, the threat to distribute intimate material classifies the psychological risk as IMMEDIATE. Rapid preservation of email headers and Bitcoin wallet tracking is prioritized.",
        "auth_status": "POTENTIALLY_AUTHENTIC",
        "auth_score": 65,
        "score_breakdown": {"evidence_match": 25, "threat_indicators": 28, "urgency_signals": 25, "victim_vulnerability": 10}
    },
    {
        "type": "SOCIAL_ENGINEERING",
        "severity": "HIGH",
        "description": "A person claiming to be a Customs Officer from Delhi Airport called me. They said a parcel under my name containing illegal drugs was intercepted. They asked me to verify my Aadhaar and bank details to clear my name, otherwise an arrest warrant would be issued. They sent a fake ID card on WhatsApp.",
        "threat_score": 75,
        "victim_risk_level": "ACTIVE",
        "ipc_sections": "IPC Sec 419 - Cheating by personation, IPC Sec 420 - Cheating, IT Act 66D - Cheating by personation using computer resource",
        "evidence_gaps": "Call recordings, WhatsApp chat exports, and the exact phone number used by the scammer.",
        "ai_reasoning": "Classic 'Customs/FedEx Parcel Scam'. The modus operandi heavily utilizes authority bias and urgency to bypass logical defenses. The fake ID card shared on WhatsApp is a strong forensic artifact. Risk is ACTIVE until the phone numbers are reported to DoT for blocking.",
        "auth_status": "AUTHENTICATED_WITH_EVIDENCE",
        "auth_score": 85,
        "score_breakdown": {"evidence_match": 35, "threat_indicators": 20, "urgency_signals": 15, "victim_vulnerability": 5}
    },
    {
        "type": "FINANCIAL_FRAUD",
        "severity": "HIGH",
        "description": "I was looking for a part-time job and saw an ad on Instagram for rating YouTube videos. They paid me 150 rupees initially. Then they added me to a Telegram group and asked me to invest 10,000 rupees for 'premium tasks'. After I transferred the money via UPI, they blocked me.",
        "threat_score": 72,
        "victim_risk_level": "SUBSIDED",
        "ipc_sections": "IPC Sec 420 - Cheating and dishonestly inducing delivery of property, IT Act 66D",
        "evidence_gaps": "UPI Transaction IDs (12-digit UTR), Bank account statement of the victim, Telegram group invite links.",
        "ai_reasoning": "Identified as a 'Task Fraud' or 'YouTube Like Scam'. Initial micro-payments were used to build trust before the primary extraction. The financial loss is concrete, but physical risk is low. Financial tracing via UTR numbers and freezing of the beneficiary account through 1930 is the immediate next step.",
        "auth_status": "HIGHLY_AUTHENTIC",
        "auth_score": 92,
        "score_breakdown": {"evidence_match": 38, "threat_indicators": 18, "urgency_signals": 10, "victim_vulnerability": 6}
    },
    {
        "type": "CYBER_STALKING",
        "severity": "CRITICAL",
        "description": "My ex-boyfriend created fake profiles on Instagram using my photos. He is messaging my friends and family with abusive language, claiming I am available for escort services, and even posted my phone number publicly. I am receiving calls from unknown men all day.",
        "threat_score": 95,
        "victim_risk_level": "IMMEDIATE",
        "ipc_sections": "IPC Sec 354D - Stalking, IPC Sec 509 - Word/gesture intending to insult modesty, IT Act 66C - Identity Theft",
        "evidence_gaps": "Profile URLs (not just usernames) of the fake accounts, screenshots of the abusive messages, Call Detail Records (CDR) of incoming harassment calls.",
        "ai_reasoning": "Severe case of Cyber Stalking and Identity Theft with immediate real-world consequences (harassment calls). The psychological and physical risk to the victim is extremely high. Immediate escalation to Women's Commission and nodal Cyber Cell required to mandate social media platforms to take down the profiles.",
        "auth_status": "AUTHENTICATED_WITH_EVIDENCE",
        "auth_score": 88,
        "score_breakdown": {"evidence_match": 35, "threat_indicators": 30, "urgency_signals": 20, "victim_vulnerability": 10}
    },
    {
        "type": "PHISHING",
        "severity": "MEDIUM",
        "description": "I received an SMS claiming my electricity bill wasn't updated and power would be cut at 9:30 PM. I clicked the link and entered my details on a portal that looked exactly like the state electricity board. I realized it was fake before entering OTP.",
        "threat_score": 45,
        "victim_risk_level": "HISTORICAL",
        "ipc_sections": "IT Act 66C - Identity Theft (Attempted), IT Act 66D - Cheating by personation",
        "evidence_gaps": "Screenshot of the original SMS showing the sender ID and the exact phishing URL.",
        "ai_reasoning": "Standard 'Electricity Bill Phishing' vector. The victim identified the threat before financial compromise (OTP was not shared). Immediate risk is low, but the phishing infrastructure (URL, hosting provider) should be flagged for takedown to protect others.",
        "auth_status": "POTENTIALLY_AUTHENTIC",
        "auth_score": 70,
        "score_breakdown": {"evidence_match": 20, "threat_indicators": 15, "urgency_signals": 5, "victim_vulnerability": 5}
    }
]

def generate_demo_cases(num_cases=50):
    print(f"[*] Generating {num_cases} highly realistic cyber-crime cases...")
    
    with app.app_context():
        sheet = get_sheet('Incidents')
        schema = SHEET_SCHEMAS['Incidents']
        
        all_new_rows = []
        
        for i in range(num_cases):
            # Pick a template
            template = random.choice(CASE_TEMPLATES)
            state = random.choice(INDIAN_STATES)
            
            # Tweak the description slightly to make them unique
            desc = template["description"]
            if "Bitcoin" in desc:
                desc = desc.replace("2000", str(random.randint(5, 50) * 100))
            if "rupees" in desc:
                desc = desc.replace("10,000", str(random.randint(10, 200) * 1000))
            
            incident_id = str(uuid.uuid4())[:8].upper()
            
            # Generate a realistic recent date
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            mins_ago = random.randint(0, 59)
            dt = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=mins_ago)
            timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Status
            status = random.choice(["OPEN", "OPEN", "OPEN", "INVESTIGATING", "ESCALATED", "CLOSED"])
            
            # Encrypt PII
            reporter_name = f"Victim_{incident_id}"
            reporter_contact = f"+91 {random.randint(7000000000, 9999999999)}"
            encrypted_name = encrypt_pii(reporter_name)
            encrypted_contact = encrypt_pii(reporter_contact)
            encrypted_state = encrypt_pii(state)
            
            content_hash = hash_content(desc)
            
            # Tweak scores slightly
            threat_score = template["threat_score"] + random.randint(-5, 5)
            auth_score = template["auth_score"] + random.randint(-5, 5)
            
            incident_record = {
                'incident_id': incident_id,
                'reporter_id': 'SYS_ADMIN_DEMO',
                'encrypted_name': encrypted_name,
                'encrypted_contact': encrypted_contact,
                'description': desc,
                'attack_type': template["type"],
                'threat_score': str(threat_score),
                'severity': template["severity"],
                'detected_tags': f"{template['type'].lower()}, automated, demo",
                'content_hash': content_hash,
                'status': status,
                'authenticity_score': str(auth_score),
                'authenticity_status': template["auth_status"],
                'verification_insights': "System Generated Demo Case",
                'ai_reasoning': template["ai_reasoning"],
                'created_at': timestamp,
                'updated_at': timestamp,
                'victim_risk_level': template["victim_risk_level"],
                'ipc_sections': template["ipc_sections"],
                'evidence_gaps': template["evidence_gaps"],
                'score_breakdown': str(template["score_breakdown"]).replace("'", '"'),
                'encrypted_state': encrypted_state
            }
            
            # Map dict to row array matching schema
            row_data = []
            for col in schema:
                row_data.append(str(incident_record.get(col, '')))
                
            all_new_rows.append(row_data)
            print(f"[{i+1}/{num_cases}] Prepared {template['type']} case ({incident_id}) in {state}")
            
        print("\n[*] Sending batch API request to Google Sheets to bypass rate limits...")
        sheet.append_rows(all_new_rows)
        print("[+] Successfully injected 50 realistic cases into Google Sheets!")

if __name__ == "__main__":
    generate_demo_cases(50)
