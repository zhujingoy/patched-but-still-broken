import sqlite3
import hashlib
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

def init_user_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                video_generation_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'video_generation_count' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN video_generation_count INTEGER DEFAULT 0')
        
        conn.commit()

def hash_password(password):
    salt = os.urandom(32)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + pwdhash.hex()

def verify_password(stored_password, provided_password):
    salt = bytes.fromhex(stored_password[:64])
    stored_hash = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return pwdhash.hex() == stored_hash

def register_user(username, password):
    if not username or not password:
        return False, '用户名和密码不能为空'
    
    if len(username) < 3:
        return False, '用户名至少需要3个字符'
    
    if len(password) < 6:
        return False, '密码至少需要6个字符'
    
    password_hash = hash_password(password)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                         (username, password_hash))
            conn.commit()
            return True, '注册成功'
    except sqlite3.IntegrityError:
        return False, '用户名已存在'
    except Exception as e:
        return False, f'注册失败: {str(e)}'

def login_user(username, password):
    if not username or not password:
        return False, None, '用户名和密码不能为空'
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?',
                         (username,))
            user = cursor.fetchone()
            
            if user and verify_password(user['password_hash'], password):
                return True, {'id': user['id'], 'username': user['username']}, '登录成功'
            else:
                return False, None, '用户名或密码错误'
    except Exception as e:
        return False, None, f'登录失败: {str(e)}'

def get_user_by_id(user_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, created_at, video_generation_count FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
    except Exception as e:
        return None

def get_user_video_count(user_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT video_generation_count FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            return result['video_generation_count'] if result else 0
    except Exception as e:
        return 0

def increment_user_video_count(user_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET video_generation_count = video_generation_count + 1 WHERE id = ?', (user_id,))
            conn.commit()
            return True
    except Exception as e:
        return False

init_user_db()
