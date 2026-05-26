"""
W-CERT Database Initializer
Run this script to set up the Google Sheets database structure.
Creates all necessary worksheets with proper headers.
"""

import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database.sheets import get_sheet

def init_db():
    print("[*] Initializing W-CERT Database...")
    
    app = create_app()
    with app.app_context():
        # List of sheets to create/verify
        sheets = [
            'Incidents',
            'Users',
            'Evidence_Metadata',
            'Audit_Log',
            'Escalations'
        ]
        
        for sheet_name in sheets:
            try:
                print(f"[*] Checking worksheet: {sheet_name}...")
                # The get_sheet function auto-creates the sheet if missing + adds headers
                get_sheet(sheet_name)
                print(f"[+] Verified/Created: {sheet_name}")
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"[-] Error initializing {sheet_name}: {e}")
                return

    print("\n[+] Database initialization complete!")
    print("[+] You should now see the worksheets in your Google Sheet.")

if __name__ == '__main__':
    init_db()
