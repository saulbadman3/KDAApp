# src/core/profile_io.py
import json
import hashlib
import base64

def _key(pw):
    return hashlib.sha256(pw.encode()).digest()

def save_profile(p, path, pw="kda_secret"):
    raw = json.dumps(p).encode()
    k = _key(pw)
    enc = bytes(b ^ k[i%32] for i, b in enumerate(raw))
    with open(path, "w") as f:
        json.dump({"d": base64.b64encode(enc).decode(), "c": hashlib.md5(raw).hexdigest()}, f)

def load_profile(path, pw="kda_secret"):
    with open(path) as f:
        w = json.load(f)
    k = _key(pw)
    raw = bytes(b ^ k[i%32] for i, b in enumerate(base64.b64decode(w["d"])))
    if hashlib.md5(raw).hexdigest() != w["c"]:
        raise ValueError("Profile corrupted or wrong key")
    return json.loads(raw.decode())