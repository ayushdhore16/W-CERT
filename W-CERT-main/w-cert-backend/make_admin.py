import os
import sys
from dotenv import load_dotenv

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database.sheets import find_row, update_row

def make_admin(email):
    """
    Promote a registered user to ADMIN role directly in the User sheet.
    """
    app = create_app('development')
    
    with app.app_context():
        print(f"[*] Looking for user: {email}...")
        
        # 1. Find the user in the 'Users' sheet
        user, row_idx = find_row('Users', 'email', email)
        
        if not user:
            print(f"[!] User not found! Please register with {email} first.")
            return

        print(f"[*] Found User: {user.get('display_name')} (Current Role: {user.get('role')})")

        # 2. Update role to ADMIN
        if user.get('role') == 'ADMIN':
            print("[!] User is already an ADMIN.")
            return

        update_row('Users', row_idx, {'role': 'ADMIN'})
        print(f"[+] SUCCESS: {email} is now an ADMIN.")
        print("    They can now access the full Dashboard and User Management.")

if __name__ == "__main__":
    load_dotenv()
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <email>")
    else:
        make_admin(sys.argv[1])
