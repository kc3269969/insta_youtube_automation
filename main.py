import schedule
import time
from downloader import download_new_reels
from editor import process_videos
from uploader import upload_scheduled_videos
from telegram_bot import run_bot, send_daily_status
from utils import load_config, is_paused, mark_upload_cycle

def job_cycle():
    if is_paused():
        print("Automation is paused.")
        return
    download_new_reels()
    process_videos()
    upload_scheduled_videos()
    mark_upload_cycle()
    send_daily_status()

def main():
    run_bot(background=True)
    config = load_config()
    # Schedule uploads at 6 AM, 12 PM, 5 PM
    schedule.every().day.at("06:00").do(job_cycle)
    schedule.every().day.at("12:00").do(job_cycle)
    schedule.every().day.at("17:00").do(job_cycle)
    print("Scheduler started.")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()