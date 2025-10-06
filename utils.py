import os
import json
from dotenv import load_dotenv

CONFIG_PATH = ".env"
UPLOADED_JSON = "uploaded.json"

def load_config():
    load_dotenv(CONFIG_PATH)

def get_env(key, default=None):
    return os.getenv(key, default)

def get_uploaded_db():
    if not os.path.exists(UPLOADED_JSON):
        return {}
    with open(UPLOADED_JSON, "r") as f:
        return json.load(f)

def update_uploaded_db(media_id, data):
    db = get_uploaded_db()
    db[str(media_id)] = db.get(str(media_id), {})
    db[str(media_id)].update(data)
    with open(UPLOADED_JSON, "w") as f:
        json.dump(db, f, indent=2)

def is_paused():
    # Check for a flag file or environment variable
    return os.path.exists("PAUSED")

def mark_upload_cycle():
    # Mark that an upload cycle has completed, for stats
    pass