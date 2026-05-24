# src/core/user_store.py
import json, hashlib, os

USERS_FILE = "users.json"

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def register_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password_hash": _hash(password),
    }
    save_users(users)
    return True

def verify(username: str, password: str) -> bool:
    users = load_users()
    if username not in users:
        return False
    return users[username]["password_hash"] == _hash(password)