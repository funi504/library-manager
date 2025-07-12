import sqlite3
from datetime import datetime

DB_NAME = "history.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            FOREIGN KEY(scan_id) REFERENCES scans(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def add_to_history(folder_path, scanned_files):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    timestamp = datetime.now().isoformat()

    # Insert scan entry
    c.execute("INSERT INTO scans (folder, timestamp) VALUES (?, ?)", (folder_path, timestamp))
    scan_id = c.lastrowid

    # Insert all scanned files
    for file_path in scanned_files:
        c.execute("INSERT INTO files (scan_id, file_path) VALUES (?, ?)", (scan_id, file_path))

    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        SELECT scans.id, scans.folder, scans.timestamp, GROUP_CONCAT(files.file_path)
        FROM scans
        LEFT JOIN files ON scans.id = files.scan_id
        GROUP BY scans.id
        ORDER BY scans.timestamp DESC
    ''')

    history = []
    for row in c.fetchall():
        scan_id, folder, timestamp, files_csv = row
        files = files_csv.split(",") if files_csv else []
        history.append({
            "id": scan_id,
            "folder": folder,
            "timestamp": timestamp,
            "files": files
        })

    conn.close()
    return history
