"""
W-CERT Evidence Manager
Handles file uploads with hashing, timestamping, and metadata storage.
Coordinates between storage, hashing, and chain of custody modules.
"""

import uuid
from datetime import datetime
from flask import current_app
from ..security.hashing import hash_bytes
from ..database.sheets import append_row
from .storage import get_storage_path, save_file
from .chain_of_custody import record_access, CoCActions


# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'eml', 'msg', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def allowed_file(filename):
    """Check if a file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_upload(file, incident_id, user_id):
    """
    Process an evidence file upload:
    1. Validate file type and size
    2. Read and hash the file content (SHA-256)
    3. Save to secure local storage
    4. Record metadata in Google Sheets
    5. Create chain of custody entry
    
    Args:
        file: Werkzeug FileStorage object from Flask request.
        incident_id (str): ID of the associated incident.
        user_id (str): ID of the uploading user.
    
    Returns:
        dict: Evidence metadata on success.
        None: If validation fails (caller should check).
    
    Raises:
        ValueError: If file is invalid.
    """
    # ── Validation ─────────────────────────────────────────────
    if not file or not file.filename:
        raise ValueError('No file provided')

    if not allowed_file(file.filename):
        raise ValueError(
            f'File type not allowed. Accepted: {", ".join(ALLOWED_EXTENSIONS)}'
        )

    # Read file data
    file_data = file.read()

    if len(file_data) > MAX_FILE_SIZE:
        raise ValueError(f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB')

    if len(file_data) == 0:
        raise ValueError('File is empty')

    # ── Hash the file ──────────────────────────────────────────
    file_hash = hash_bytes(file_data)

    # ── Store the file ─────────────────────────────────────────
    storage_path = get_storage_path(current_app.config, file_hash)
    save_file(file_data, storage_path)

    # ── Generate metadata ──────────────────────────────────────
    evidence_id = str(uuid.uuid4())[:8].upper()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Determine MIME type
    extension = file.filename.rsplit('.', 1)[1].lower()
    mime_types = {
        'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
        'gif': 'image/gif', 'pdf': 'application/pdf', 'txt': 'text/plain',
        'eml': 'message/rfc822', 'msg': 'application/vnd.ms-outlook',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }

    metadata = {
        'evidence_id': evidence_id,
        'incident_id': incident_id,
        'file_hash': file_hash,
        'original_filename': file.filename,
        'storage_path': storage_path,
        'mime_type': mime_types.get(extension, 'application/octet-stream'),
        'file_size': str(len(file_data)),
        'uploaded_by': user_id,
        'uploaded_at': timestamp
    }

    # ── Save metadata to Sheets ────────────────────────────────
    append_row('Evidence_Metadata', metadata)

    # ── Chain of custody: record initial upload ────────────────
    record_access(
        evidence_id=evidence_id,
        user_id=user_id,
        action=CoCActions.UPLOAD,
        details=f'File uploaded: {file.filename} ({len(file_data)} bytes, hash: {file_hash[:16]}...)'
    )

    return metadata
