import schedule
import time
from datetime import datetime, timedelta
import os
import json

# Import all modules
from utils import load_env, init_dirs, log_message, load_uploaded, save_uploaded
from downloader import download_new_reels
from editor import process_video
from ai_metadata import generate_metadata_with_ai
from uploader import upload_video

# --- Global State and Environment ---
ENV = load_env()
init_dirs()
UPLOAD_QUEUE = []
UPLOAD_COUNT_TODAY = 0
UPLOAD_LOG = load_uploaded()
AUTOMATION_PAUSED = False

# --- Scheduling Helpers ---

def get_next_available_video():
    """Finds a processed video that hasn't been uploaded yet."""
    processed_files = [f for f in os.listdir(ENV['PROCESS_DIR']) if f.endswith('.mp4')]
    
    for filename in processed_files:
        insta_id = filename.split('_')[1].split('.')[0] # e.g. processed_2345678.mp4 -> 2345678
        if insta_id not in UPLOAD_LOG:
            # Reconstruct the original metadata from the download directory (if necessary)
            # Or assume metadata is generated before upload.
            
            # For simplicity, we assume the original .json file (from downloader) is available
            # We'll use the editor's output path here.
            video_path = os.path.join(ENV['PROCESS_DIR'], filename)
            
            # Placeholder for actual metadata retrieval/generation
            # In a clean run, metadata should be generated *before* adding to the queue.
            # Here we'll generate on the fly if needed.
            
            # To be more robust, we should store metadata with the processed file.
            log_message("INFO", f"Found new processed video for upload: {filename}")
            
            # Placeholder content for AI generation based on file name if no metadata is linked
            simulated_content = f"Fact about ID {insta_id}" 
            
            # --- AI Metadata Generation ---
            try:
                metadata = generate_metadata_with_ai(simulated_content, ENV)
                return video_path, metadata, insta_id
            except Exception as e:
                log_message("ERROR", f"AI metadata generation failed: {e}")
                continue
    return None, None, None

def calculate_scheduled_time(time_str):
    """Calculates the next available time slot (now or in the future) in RFC 3339 format."""
    now = datetime.now()
    hour, minute = map(int, time_str.split(':'))
    
    # Target time for today
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # If the target time is in the past, schedule for a few minutes from now
    if target_time <= now + timedelta(minutes=5):
        # Schedule it for 2 minutes from now to ensure a clean immediate upload
        scheduled = now + timedelta(minutes=2)
        log_message("WARN", f"Scheduled time {time_str} is in the past. Uploading immediately at {scheduled.strftime('%H:%M')}")
    else:
        scheduled = target_time
    
    # Convert to RFC 3339 format (required by YouTube API)
    return scheduled.isoformat("T") + "Z", scheduled.strftime("%I:%M %p")


# --- Main Automation Cycle ---

def download_and_process():
    """Step 1: Download new videos and process them."""
    log_message("INFO", "--- Starting DAILY DOWNLOAD/PROCESSING ---")
    
    # 1. Download
    downloaded_files = download_new_reels(ENV)
    
    # 2. Process
    for download_path, metadata in downloaded_files:
        processed_path = process_video(download_path, ENV)
        if processed_path:
            # Add to the global queue for the uploader
            UPLOAD_QUEUE.append({
                "video_path": processed_path,
                "insta_id": metadata['insta_id'],
                # We should run AI generation here to link to processed file
                "metadata": generate_metadata_with_ai(metadata['caption'], ENV) 
            })
            log_message("INFO", f"Video {metadata['insta_id']} added to upload queue.")
        else:
            log_message("ERROR", f"Failed to process {download_path}. Skipping.")


def trigger_upload_cycle(scheduled_time_str):
    """Step 2: Upload one video at the specified time slot."""
    global UPLOAD_COUNT_TODAY, UPLOAD_LOG, UPLOAD_QUEUE, AUTOMATION_PAUSED
    
    if AUTOMATION_PAUSED:
        log_message("WARN", "Automation is paused. Skipping upload.")
        return
        
    log_message("INFO", f"--- Starting UPLOAD CYCLE for {scheduled_time_str} ---")

    # Check if we've already hit the limit
    if UPLOAD_COUNT_TODAY >= int(ENV['MAX_DAILY']):
        log_message("WARN", "Max daily uploads reached. Skipping.")
        return

    video_path, metadata, insta_id = get_next_available_video()
    
    if video_path and metadata:
        # Calculate the actual scheduled time
        scheduled_utc, readable_time = calculate_scheduled_time(scheduled_time_str)
        
        # --- YouTube Upload ---
        yt_url = upload_video(video_path, metadata, scheduled_utc, ENV)

        if yt_url:
            # 3. Update log and cleanup
            UPLOAD_LOG[insta_id] = {
                "filename": os.path.basename(video_path),
                "timestamp": datetime.now().isoformat(),
                "youtube_url": yt_url,
                "scheduled_for": readable_time
            }
            save_uploaded(UPLOAD_LOG)
            UPLOAD_COUNT_TODAY += 1
            log_message("SUCCESS", f"Upload {UPLOAD_COUNT_TODAY}/3 succeeded. URL: {yt_url}")
            # send_telegram_notification(f"✅ Upload success at {readable_time}! Count: {UPLOAD_COUNT_TODAY}/3")
            # Optional: os.remove(video_path) to clean up processed files

        else:
            log_message("ERROR", "Upload failed. Logging attempt.")
            # send_telegram_notification(f"❌ Upload failed for {insta_id} at {scheduled_time_str}")
            
    else:
        log_message("WARN", "No new unique video found in /processed/ folder to upload.")
        # send_telegram_notification("⚠️ Upload skipped: No unique videos available.")


def reset_daily_count():
    """Resets the upload count at midnight."""
    global UPLOAD_COUNT_TODAY
    UPLOAD_COUNT_TODAY = 0
    log_message("INFO", "Daily upload count reset to 0.")


# --- Scheduling Setup ---

def setup_scheduler():
    """Sets up the daily schedule."""
    # Reset count every day at 00:01
    schedule.every().day.at("00:01").do(reset_daily_count)
    
    # Daily download and processing run (e.g., at 1 AM)
    schedule.every().day.at("01:00").do(download_and_process)

    # Scheduled uploads
    schedule.every().day.at("06:00").do(lambda: trigger_upload_cycle("06:00"))
    schedule.every().day.at("12:00").do(lambda: trigger_upload_cycle("12:00"))
    schedule.every().day.at("17:00").do(lambda: trigger_upload_cycle("17:00"))
    
    log_message("INFO", "Automation scheduler initialized.")


# --- Main Loop ---

if __name__ == '__main__':
    log_message("INFO", "Starting YouTube Shorts Automation System...")
    
    # Initialize scheduler
    setup_scheduler()
    
    # Initialize and run the Telegram bot in a separate thread/process (omitted here for brevity)
    # bot_thread = threading.Thread(target=run_telegram_bot)
    # bot_thread.start()
    
    # Run the initial download/process cycle to populate the queue
    download_and_process()
    
    while True:
        schedule.run_pending()
        time.sleep(1) # Check every second
