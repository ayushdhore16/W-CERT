# W-CERT Backend Framework

Women-Centric Cyber Emergency Response & Threat-analysis Framework.
A secure, privacy-focused incident response system for phishing and social engineering attacks.

## Features
- **Threat Analysis Engine**: Weighted keyword analysis for Sextortion, Financial Fraud, Identity Theft, Impersonation, and Urgency.
- **Security**: AES-128 encryption for PII, SHA-256 for evidence integrity, JWT authentication.
- **Evidence Management**: Secure file upload, storage, and immutable Chain of Custody tracking.
- **Database**: Google Sheets integration for collaborative access.
- **Escalation**: Workflow for reporting to Cyber Crime Cell, CERT-In, and Women's Helpline.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Set your `SERVICE_ACCOUNT_PATH` (relative to this directory)
   - Ensure `service_account.json` is present

3. **Run the Server**
   ```bash
   python run.py
   ```
   Server starts at `http://localhost:5000`

## Testing
Run the test suite:
```bash
python -m pytest tests/ -v
```

## API Documentation
See `app/api/` for route definitions.
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Get JWT token
- `POST /api/incidents` - Submit incident report
- `POST /api/incidents/<id>/evidence` - Upload evidence
