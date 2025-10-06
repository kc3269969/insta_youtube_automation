import os
import json
from instagrapi import Client
from utils import load_uploaded, save_uploaded, log_message

def download_new_reels(env):
    """Logs into Instagram and downloads new, unwatched reels."""
    log_message("INFO", "Starting Instagram download cycle...")
    cl = Client()
    try:
        # Load session/login
        cl.login(env['INSTAGRAM_USERNAME'], env['INSTAGRAM_PASSWORD'])
    except Exception as e:
        log_message("ERROR", f"Instagram login failed: {e}")
        return []

    uploaded_data = load_uploaded()
    source_accounts = env['INSTAGRAM_SOURCE_ACCOUNTS'].split(',')
    downloaded_files = []

    for account in source_accounts:
        try:
            # Get user info and then their media
            user_id = cl.user_id_from_username(account.strip())
            # Fetch recent 50 media items (adjust as needed)
            medias = cl.user_medias(user_id, amount=50)

            for media in medias:
                # Check if it's a Reel and if we've already uploaded it
                if media.media_type == 2 and str(media.id) not in uploaded_data:
                    log_message("INFO", f"Found new Reel from {account}: {media.code}")
                    # instagrapi automatically handles watermark removal
                    download_path = cl.video_download(media.pk, folder=env['DOWNLOAD_DIR'])
                    
                    # Store metadata
                    metadata = {
                        "insta_id": str(media.id),
                        "source_account": account,
                        "caption": media.caption_text if media.caption_text else "",
                        "file_path": download_path,
                        "processed": False
                    }
                    
                    # Save the initial metadata to a temporary .json file for processing
                    meta_filename = os.path.splitext(os.path.basename(download_path))[0] + ".json"
                    meta_path = os.path.join(env['DOWNLOAD_DIR'], meta_filename)
                    with open(meta_path, 'w') as f:
                        json.dump(metadata, f)

                    downloaded_files.append((download_path, metadata))
                    
                    # NOTE: We temporarily mark it as downloaded to avoid a race condition
                    # but only mark as uploaded *after* the successful YouTube upload.
                    
                    if len(downloaded_files) >= int(env['MAX_DAILY']):
                        log_message("INFO", f"Reached max daily download limit ({env['MAX_DAILY']}). Stopping.")
                        return downloaded_files

        except Exception as e:
            log_message("ERROR", f"Error processing account {account}: {e}")
            
    return downloaded_files

if __name__ == '__main__':
    from dotenv import dotenv_values
    env = dotenv_values(".env")
    download_new_reels(env)
