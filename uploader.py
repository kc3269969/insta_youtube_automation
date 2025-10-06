import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from utils import log_message

# The SCOPES required for YouTube Data API v3 upload
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service(env):
    """Authenticates (using modified fixed-port loopback flow) and returns the YouTube API service."""
    credentials = None
    token_path = 'token.json'
    
    # 1. Check for existing token file
    if os.path.exists(token_path):
        log_message("INFO", "Loading credentials from token.json.")
        try:
            with open(token_path, 'r') as token:
                creds_data = json.load(token)
            credentials = Credentials.from_authorized_user_info(creds_data, SCOPES)
        except Exception as e:
            log_message("WARN", f"Error loading existing token. Forcing re-auth. {e}")
            credentials = None
            
    # 2. If no valid credentials, run the manual authentication flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            log_message("INFO", "Token expired. Attempting refresh.")
            credentials.refresh(Request())
        else:
            # Reverting to the Fixed Port Loopback with manual browser opening.
            log_message("WARN", "Running FIXED-PORT loopback authentication (Manual Browser Open).")
            log_message("WARN", "You MUST register http://localhost:8080 and/or http://127.0.0.1:8080 in the Google Console.")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                env['GOOGLE_CLIENT_SECRETS'], SCOPES)
            
            # --- FIXED PORT LOOPBACK FLOW ---
            # Forces port 8080, which MUST be registered as a Redirect URI.
            credentials = flow.run_local_server(
                port=8080,         # Fixed port to match your registered URI
                open_browser=False # Prevents browser auto-open
            )
            
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(credentials.to_json())
            log_message("SUCCESS", "Authentication successful! token.json saved.")

    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def upload_video(video_path, metadata, scheduled_time, env):
    """Uploads a video to YouTube and returns the video URL."""
    log_message("INFO", "Authenticating YouTube service...")
    youtube = get_authenticated_service(env)
    
    # Combine title and hashtags for the final video title (Shorts style)
    final_title = f"{metadata['title']} {metadata['hashtags']}"
    
    # Build the request body
    body = {
        'snippet': {
            'title': final_title,
            'description': metadata['description'],
            'tags': metadata['tags'].split(','),
            'categoryId': '28', # Category 28 is "Science & Technology"
        },
        'status': {
            'privacyStatus': 'private', # Use 'private' for scheduled uploads
            'publishAt': scheduled_time, # Must be in RFC 3339 format
            'selfDeclaredMadeForKids': False, 
        }
    }

    # Upload the video file
    try:
        media_file = MediaFileUpload(video_path)
        log_message("INFO", f"Starting upload for: {os.path.basename(video_path)}")
        
        response = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media_file
        ).execute()

        video_id = response.get('id')
        video_url = f"https://youtu.be/{video_id}"
        
        log_message("SUCCESS", f"Video uploaded and scheduled successfully! URL: {video_url}")
        return video_url

    except Exception as e:
        log_message("ERROR", f"YouTube upload failed: {e}")
        return None
