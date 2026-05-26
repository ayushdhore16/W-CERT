"""
W-CERT Google Sheets Database Layer
Provides CRUD operations over Google Sheets using gspread.
Each worksheet acts as a table with row 1 as headers.
"""

import os
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials
from flask import current_app


# ── Sheet Schemas (column headers for each worksheet) ──────────
SHEET_SCHEMAS = {
    'Incidents': [
        'incident_id', 'reporter_id', 'encrypted_name', 'encrypted_contact',
        'description', 'attack_type', 'threat_score', 'severity',
        'detected_tags', 'content_hash', 'status', 'authenticity_score',
        'authenticity_status', 'verification_insights', 'ai_reasoning',
        'created_at', 'updated_at',
        'victim_risk_level', 'ipc_sections', 'evidence_gaps', 'score_breakdown',
        'encrypted_state'
    ],
    'Users': [
        'user_id', 'email', 'password_hash', 'display_name', 'role', 'created_at'
    ],
    'Evidence_Metadata': [
        'evidence_id', 'incident_id', 'file_hash', 'original_filename',
        'storage_path', 'mime_type', 'file_size', 'uploaded_by', 'uploaded_at'
    ],
    'Audit_Log': [
        'log_id', 'user_id', 'action', 'resource_type', 'resource_id',
        'ip_address', 'timestamp', 'details'
    ],
    'Escalations': [
        'escalation_id', 'incident_id', 'escalated_by', 'escalated_to',
        'reason', 'status', 'created_at'
    ]
}

# Module-level client and cache
_sheets_client = None
_sheets_cache = {}  # {sheet_name: {'data': data, 'expiry': timestamp}}
CACHE_TTL = 60      # Cache data for 60 seconds to reduce API calls


def _get_client():
    """Get or create a gspread client using service account credentials."""
    global _sheets_client
    if _sheets_client is not None:
        return _sheets_client

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Resolve service account path
    sa_path = current_app.config.get('SERVICE_ACCOUNT_PATH', '../service_account.json')
    if not os.path.isabs(sa_path):
        sa_path = os.path.join(current_app.root_path, '..', sa_path)
    sa_path = os.path.abspath(sa_path)

    creds = ServiceAccountCredentials.from_json_keyfile_name(sa_path, scope)
    _sheets_client = gspread.authorize(creds)
    return _sheets_client


def _get_spreadsheet():
    """Get the W-CERT spreadsheet."""
    client = _get_client()
    spreadsheet_id = current_app.config.get('SPREADSHEET_ID')
    if spreadsheet_id:
        return client.open_by_key(spreadsheet_id)
    
    # Fallback to name if ID not set
    spreadsheet_name = current_app.config.get('SPREADSHEET_NAME', 'W-CERT_Database')
    return client.open(spreadsheet_name)


def get_sheet(sheet_name):
    """
    Get a worksheet by name. If it doesn't exist, create it with headers.
    """
    spreadsheet = _get_spreadsheet()

    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        # Auto-create worksheet with headers
        headers = SHEET_SCHEMAS.get(sheet_name, [])
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers) or 10)
        if headers:
            worksheet.append_row(headers)
        print(f"[+] Created worksheet: {sheet_name}")

    return worksheet


def append_row(sheet_name, data_dict):
    """
    Append a row to a worksheet. Data is a dict matching column headers.
    Returns True on success, raises on failure.
    """
    sheet = get_sheet(sheet_name)
    headers = SHEET_SCHEMAS.get(sheet_name, [])

    # Build row in column order
    row = [str(data_dict.get(col, '')) for col in headers]
    sheet.append_row(row, value_input_option='RAW')
    # Invalidate cache on write
    _sheets_cache.pop(sheet_name, None)
        
    return True


def get_all_rows(sheet_name):
    """
    Get all rows from a worksheet as a list of dicts.
    Uses manual mapping from SHEET_SCHEMAS to avoid gspread.get_all_records bugs.
    Uses TTL cache to avoid 429 API errors.
    """
    global _sheets_cache
    
    # Check cache
    now = time.time()
    if sheet_name in _sheets_cache:
        cache_entry = _sheets_cache[sheet_name]
        if now < cache_entry['expiry']:
            return cache_entry['data']

    # Fetch RAW values
    sheet = get_sheet(sheet_name)
    all_values = sheet.get_all_values()
    
    if not all_values:
        return []

    # Map headers (Row 1) to data
    headers = SHEET_SCHEMAS.get(sheet_name, all_values[0])
    data_rows = all_values[1:]
    
    records = []
    for row in data_rows:
        record = {}
        for i, h in enumerate(headers):
            # Ensure index safety and strip whitespace
            val = row[i].strip() if i < len(row) else ''
            record[h] = val
        records.append(record)
    
    # Update cache
    _sheets_cache[sheet_name] = {
        'data': records,
        'expiry': now + CACHE_TTL
    }
    
    return records


def find_rows(sheet_name, column, value):
    """
    Find all rows where a column matches a value.
    Returns list of dicts.
    """
    all_rows = get_all_rows(sheet_name)
    return [row for row in all_rows if str(row.get(column, '')) == str(value)]


def find_row(sheet_name, column, value):
    """
    Find the first row where a column matches a value.
    Returns (row_dict, row_index) or (None, None).
    row_index is 1-based (includes header row offset).
    Uses cached data to avoid extra API calls.
    """
    all_rows = get_all_rows(sheet_name)
    str_value = str(value)

    for i, row in enumerate(all_rows):
        if str(row.get(column, '')) == str_value:
            # row_index is 1-based: row 1 = headers, row 2 = first data row
            return row, i + 2

    return None, None


def update_row(sheet_name, row_index, data_dict):
    """
    Update a row at a given index (1-based, header is row 1).
    Only updates columns present in data_dict.
    Uses batch_update to send one API call instead of N.
    """
    sheet = get_sheet(sheet_name)
    headers = SHEET_SCHEMAS.get(sheet_name, [])

    # Build batch update cells list
    cells_to_update = []
    for col_name, value in data_dict.items():
        if col_name in headers:
            col_index = headers.index(col_name) + 1
            cells_to_update.append(
                gspread.Cell(row=row_index, col=col_index, value=str(value))
            )

    if cells_to_update:
        sheet.update_cells(cells_to_update, value_input_option='RAW')

    # Invalidate cache on update
    _sheets_cache.pop(sheet_name, None)

    return True


def count_rows(sheet_name):
    """Count all data rows (excluding header). Uses cache when available."""
    rows = get_all_rows(sheet_name)
    return len(rows)


def get_recent_rows(sheet_name, limit=10):
    """Get the most recent N rows (last N entries)."""
    all_rows = get_all_rows(sheet_name)
    return all_rows[-limit:] if len(all_rows) > limit else all_rows


def reset_client():
    """Reset the cached client (useful for testing or credential refresh)."""
    global _sheets_client
    _sheets_client = None
