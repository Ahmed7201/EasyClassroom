import os
import json
import hashlib
import shutil
from pathlib import Path

USER_DATA_DIR = "user_data"
DB_FILE = "users_db.json"

def _hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def init_user_system():
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({}, f)

def user_exists(user_id):
    init_user_system()
    with open(DB_FILE, 'r') as f:
        db = json.load(f)
    return user_id in db

def register_user(user_id, pin, uploaded_creds_file):
    init_user_system()
    if user_exists(user_id):
        return False, "User ID already exists."

    # Create user directory
    user_dir = os.path.join(USER_DATA_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)

    # Save credentials
    creds_path = os.path.join(user_dir, "credentials.json")
    with open(creds_path, "wb") as f:
        f.write(uploaded_creds_file.getbuffer())

    # Update DB
    with open(DB_FILE, 'r') as f:
        db = json.load(f)
    
    db[user_id] = {
        "pin_hash": _hash_pin(pin),
        "created_at": str(os.path.getctime(creds_path))
    }
    
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)
        
    return True, "User registered successfully!"

def verify_login(user_id, pin):
    init_user_system()
    with open(DB_FILE, 'r') as f:
        db = json.load(f)
    
    if user_id not in db:
        return False
    
    return db[user_id]["pin_hash"] == _hash_pin(pin)

def get_user_paths(user_id):
    user_dir = os.path.join(USER_DATA_DIR, user_id)
    return {
        "credentials": os.path.join(user_dir, "credentials.json"),
        "token": os.path.join(user_dir, "token.json")
    }
