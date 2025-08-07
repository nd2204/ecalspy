import sqlite3

from ecalspy.core.es_config_manager import ConfigManager
from ecalspy.core.es_utils import JsonSerializer
from cryptography.fernet import Fernet

KEY = ConfigManager.CreateOrRetrieveConfig(
    "TokenEncryptionKey",
    valueOnCreate=Fernet.generate_key().decode()
)
cipher = Fernet(KEY.encode())

ES_DB_NAME = "ecals_db"
ES_DB_FILE = f"{ES_DB_NAME}.sqlite"

class UserModel:
    def __init__(self):
        self.id = None
        self.login_id = None
        self.config : dict = None
        self.created_at = None

def InitDb():
    con = sqlite3.connect(ES_DB_FILE)

    cursor = con.cursor()
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login_id TEXT UNIQUE NOT NULL,
        config TEXT,
        cookies TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS external_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        service_name TEXT NOT NULL,
        token_data TEXT NOT NULL,
        expires_at DATETIME,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """
    )
    con.commit()
    con.close()

def AddUser(login_id, config, cookies={}):
    conn = sqlite3.connect(ES_DB_FILE)
    cursor = conn.cursor()
    config_json = JsonSerializer.Serialize(config) if config else None
    cookies_json = JsonSerializer.Serialize(cookies) if cookies else None
    cursor.execute("INSERT INTO users (login_id, config, cookies) VALUES (?, ?)", 
                   (lgoin_id, config))
    conn.commit()
    conn.close()

def GetUserByLoginId(login_id):
    conn = sqlite3.connect(ES_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE login_id = ?", (login_id))
    row = cursor.fetchone()
    conn.close()
    return {
        "id": row[0],
        "login_id": row[1],
        "config": JsonSerializer.Deserialize(row[2]) if row[2] else None,
        "cookies": JsonSerializer.Deserialize(row[3]) if row[3] else None,
        "created_at": row[4]
    }

def GetUserCookiesByLoginId(login_id):
    conn = sqlite3.connect(ES_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT cookies FROM users WHERE login_id = ?", (login_id))
    row = cursor.fetchone()
    conn.close()
    return JsonSerializer.Deserialize(row[0]) if row[0] else None

def UpdateUserConfig(user_id, config):
    conn = sqlite3.connect(ES_DB_FILE)
    cursor = conn.cursor()
    config_json = JsonSerializer.Serialize(config)
    cursor.execute("UPDATE users SET config = ? WHERE id = ?", (config_json, user_id))
    conn.commit()
    conn.close()

def GetUserConfig(user_id):
    conn = sqlite3.connect(ES_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT config FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return JsonSerializer.Deserialize(row[0]) if row and row[0] else None

def StoreToken(user_id, service, token_data, expires_at=None):
    encrypted_token_data = cipher.encrypt(access_token.encode()).decode()

    conn = sqlite3.connect(ES_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO external_tokens (user_id, service_name, token_data, expires_at)
    VALUES (?, ?, ?, ?)
    """, (user_id, service, encrypted_token_data, expires_at))
    conn.commit()
    conn.close()

def GetTokens(user_id):
    conn = sqlite3.connect(ES_DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT service_name, token_data, expires_at FROM external_tokens WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "service": row[0],
            "token_data": cipher.decrypt(row[1].encode()).decode(),
            "expires_at": row[2]
        }
        for row in rows
    ]
