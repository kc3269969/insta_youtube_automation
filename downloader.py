from instagrapi import Client
import os
import json
from utils import get_env, update_uploaded_db, get_uploaded_db

ACCOUNTS = ["account1", "account2"]  # Set your target IG accounts

def login_instagram():
    cl = Client()
    cl.login(get_env("INSTAGRAM_USERNAME"), get_env("INSTAGRAM_PASSWORD"))
    return cl

def download_new_reels():
    cl = login_instagram()
    uploaded = get_uploaded_db()
    for account in ACCOUNTS:
        user_id = cl.user_id_from_username(account)
        medias = cl.user_medias(user_id, 10)
        for media in medias:
            if str(media.pk) in uploaded:
                continue
            if media.media_type != 2:
                continue  # Not a video
            video_url = cl.media_info(media.pk).video_url
            filename = f"downloads/{media.pk}.mp4"
            cl.video_download(media.pk, filename=filename)
            update_uploaded_db(media.pk, {
                "filename": filename,
                "source": account,
                "status": "downloaded"
            })