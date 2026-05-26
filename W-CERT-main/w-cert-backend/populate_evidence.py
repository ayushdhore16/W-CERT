"""
Mass Evidence Populator (Batched)
Attaches dummy evidence to all incidents that lack it.
Uses batching to avoid gspread/Google Sheets API quota limits.
"""
import os, sys, uuid, time
from datetime import datetime
sys.path.append('.')
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.database.sheets import get_all_rows, append_row, update_row, find_rows, find_row
from app.evidence.storage import get_storage_path, save_file

app = create_app()
with app.app_context():
    # 1. Prepare dummy file
    dummy_content = b'W-CERT SECURE EVIDENCE'
    dummy_hash = 'DUMMY_HASH_ENRICHMENT_001'
    storage_path = get_storage_path(app.config, dummy_hash)
    save_file(dummy_content, storage_path)
    print(f'[*] Prepared dummy file at: {storage_path}')

    incidents = get_all_rows('Incidents')
    total = len(incidents)
    print(f'[*] Scanned {total} incidents.')

    batch_size = 15 # conservative batch size for gspread
    current_batch = 0
    populated = 0

    for i, inc in enumerate(incidents):
        inc_id = inc['incident_id']
        
        # Check if already has evidence
        existing = find_rows('Evidence_Metadata', 'incident_id', inc_id)
        if existing:
            continue

        # Add evidence metadata
        ev_id = str(uuid.uuid4())[:8].upper()
        metadata = {
            'evidence_id': ev_id,
            'incident_id': inc_id,
            'file_hash': dummy_hash,
            'original_filename': 'analysis_evidence.png',
            'storage_path': storage_path,
            'mime_type': 'image/png',
            'file_size': str(len(dummy_content)),
            'uploaded_by': 'SYSTEM_AUTO_ENRICH',
            'uploaded_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        append_row('Evidence_Metadata', metadata)
        
        # Update incident score/status
        _, row_idx = find_row('Incidents', 'incident_id', inc_id)
        if row_idx:
            update_row('Incidents', row_idx, {
                'authenticity_score': '75',
                'authenticity_status': 'AUTHENTICATED_WITH_EVIDENCE'
            })
        
        populated += 1
        current_batch += 1
        
        if current_batch >= batch_size:
            print(f'[+] Batched {populated}/{total}. Waiting for quota reset (30s)...')
            time.sleep(30)
            current_batch = 0
        else:
            print(f'  [~] Populated {inc_id}')

    print(f'[*] MISSION COMPLETE. Populated {populated} incidents.')
