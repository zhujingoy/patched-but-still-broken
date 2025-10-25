import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = 'generation_statistics.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generation_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                client_address TEXT NOT NULL,
                upload_file_count INTEGER NOT NULL,
                upload_text_chars INTEGER NOT NULL,
                upload_content_size INTEGER NOT NULL,
                generated_scene_count INTEGER DEFAULT 0,
                generated_content_size INTEGER DEFAULT 0,
                username TEXT,
                filename TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute("PRAGMA table_info(generation_statistics)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'username' not in columns:
            cursor.execute('ALTER TABLE generation_statistics ADD COLUMN username TEXT')
        
        if 'filename' not in columns:
            cursor.execute('ALTER TABLE generation_statistics ADD COLUMN filename TEXT')
        
        conn.commit()

def insert_statistics(session_id, client_address, upload_file_count, upload_text_chars, upload_content_size, username=None, filename=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO generation_statistics 
            (session_id, client_address, upload_file_count, upload_text_chars, upload_content_size, username, filename)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, client_address, upload_file_count, upload_text_chars, upload_content_size, username, filename))
        conn.commit()
        return cursor.lastrowid

def update_generation_stats(session_id, generated_scene_count, generated_content_size):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE generation_statistics 
            SET generated_scene_count = ?, generated_content_size = ?
            WHERE session_id = ?
        ''', (generated_scene_count, generated_content_size, session_id))
        conn.commit()

def get_statistics(session_id=None, username=None, limit=None):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if session_id:
            cursor.execute('SELECT * FROM generation_statistics WHERE session_id = ?', (session_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        elif username:
            query = 'SELECT * FROM generation_statistics WHERE username = ? ORDER BY created_at DESC'
            if limit:
                query += f' LIMIT {limit}'
            cursor.execute(query, (username,))
            return [dict(row) for row in cursor.fetchall()]
        else:
            cursor.execute('SELECT * FROM generation_statistics ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]

init_db()
