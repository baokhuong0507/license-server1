# app/services/keys.py
import sqlite3
from app.config import settings
import os

def get_db_path():
    # Lấy đường dẫn tệp từ DATABASE_URL
    return settings.DATABASE_URL.split("///")[-1]

def init_db():
    """Tạo bảng trong CSDL nếu chưa tồn tại."""
    db_path = get_db_path()
    # Đảm bảo thư mục cha tồn tại
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keys (
            key_value TEXT PRIMARY KEY NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        )
    ''')
    conn.commit()
    conn.close()

def add_key(key_value: str) -> bool:
    """Thêm một key mới vào CSDL."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO keys (key_value) VALUES (?)", (key_value,))
        conn.commit()
        return True
    except sqlite3.IntegrityError: # Key đã tồn tại
        return False
    finally:
        conn.close()

def delete_key(key_value: str):
    """Xóa một key khỏi CSDL."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("DELETE FROM keys WHERE key_value = ?", (key_value,))
    conn.commit()
    conn.close()

def get_key_status(key_value: str) -> str | None:
    """Lấy trạng thái của một key."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM keys WHERE key_value = ?", (key_value,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def update_key_status(key_value: str, new_status: str):
    """Cập nhật trạng thái của một key."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("UPDATE keys SET status = ? WHERE key_value = ?", (new_status, key_value))
    conn.commit()
    conn.close()
