"""
W-CERT Backend — Entry Point
Run with: python run.py
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("  W-CERT Backend API")
    print("  Women-Centric Cyber Emergency Response")
    print("  & Threat-analysis Framework")
    print("=" * 50)
    print("[*] Starting secure server on http://localhost:5000")
    app.run(debug=True, port=5000)
