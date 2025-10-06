import os
from utils import get_uploaded_db, update_uploaded_db, get_env
from ai_metadata import generate_metadata

def upload_to_youtube(video_path, title, description, tags):
    # TODO: Implement using google-api-python-client
    # For now, mock upload
    print(f"Uploading {video_path} with title: {title}")
    return "https://youtu.be/dummy123"

def upload_scheduled_videos():
    uploaded = get_uploaded_db()
    count_today = sum(1 for v in uploaded.values() if v.get("uploaded_today"))
    MAX_DAILY = int(get_env("MAX_DAILY", 3))
    if count_today >= MAX_DAILY:
        print("Daily upload limit reached.")
        return
    for fname in os.listdir("processed"):
        path = os.path.join("processed", fname)
        video_id = os.path.splitext(fname)[0]
        meta = uploaded.get(video_id, {})
        if meta.get("status") == "uploaded":
            continue
        title, description, tags = generate_metadata(path)
        url = upload_to_youtube(path, title, description, tags)
        update_uploaded_db(video_id, {
            "filename": fname,
            "upload_time": "now",  # set actual timestamp
            "youtube_url": url,
            "status": "uploaded",
            "uploaded_today": True
        })
        break