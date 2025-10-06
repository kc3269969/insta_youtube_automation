import os
import json
import logging
from datetime import datetime
from dotenv import dotenv_values
from telegram import Bot

# --- Configuration Constants ---
LOG_DIR = 'logs'
UPLOAD_TRACKER = 'uploaded.json'

# --- Environment and Directory Setup ---

def load_env():
    """Loads environment variables from the .env file."""
    try:
        env = dotenv_values(".env")
        if not env:
            raise FileNotFoundError("The .env file could not be loaded or is empty.")
        # Ensure required directories are in the environment dict
        env['DOWNLOAD_DIR'] = env.get('DOWNLOAD_DIR', 'downloads')
        env['PROCESS_DIR'] = env.get('PROCESS_DIR', 'processed')
        env['LOG_DIR'] = env.get('LOG_DIR', LOG_DIR)
        return env
    except Exception as e:
        print(f"FATAL ERROR: Failed to load environment variables: {e}")
        exit(1)

def init_dirs(env):
    """Creates the necessary project directories."""
    os.makedirs(env['DOWNLOAD_DIR'], exist_ok=True)
    os.makedirs(env['PROCESS_DIR'], exist_ok=True)
    os.makedirs(env['LOG_DIR'], exist_ok=True)
    print("Directories initialized: downloads/, processed/, logs/")

# --- Data Storage (uploaded.json) ---

def load_uploaded():
    """Loads the upload tracking data from uploaded.json."""
    if not os.path.exists(UPLOAD_TRACKER):
        return {}
    try:
        with open(UPLOAD_TRACKER, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"WARN: Could not read {UPLOAD_TRACKER}. Initializing new tracker. Error: {e}")
        return {}

def save_uploaded(data):
    """Saves the upload tracking data to uploaded.json."""
    try:
        with open(UPLOAD_TRACKER, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"ERROR: Failed to save data to {UPLOAD_TRACKER}. Error: {e}")

# --- Logging and Notifications ---

def log_message(level, message, env=None):
    """
    Generates a log message to the console and a daily log file.
    
    Args:
        level (str): Log level (e.g., 'INFO', 'WARN', 'ERROR', 'SUCCESS').
        message (str): The log message content.
        env (dict, optional): The environment variables for LOG_DIR.
    """
    if not env:
        # Load env if not provided (for standalone testing or early calls)
        env = dotenv_values(".env")
        env['LOG_DIR'] = env.get('LOG_DIR', LOG_DIR)
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level.upper()}] {message}"
    
    print(log_line) # Print to console
    
    # Write to daily log file
    log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
    log_path = os.path.join(env['LOG_DIR'], log_filename)
    
    try:
        with open(log_path, 'a') as f:
            f.write(log_line + '\n')
    except IOError as e:
        print(f"ERROR: Failed to write to log file. {e}")

def send_telegram_notification(message, env):
    """Sends a notification message via the Telegram bot."""
    if 'TELEGRAM_BOT_TOKEN' not in env or 'TELEGRAM_CHAT_ID' not in env:
        log_message("WARN", "Telegram credentials missing. Notification skipped.")
        return

    try:
        bot = Bot(token=env['TELEGRAM_BOT_TOKEN'])
        bot.send_message(chat_id=env['TELEGRAM_CHAT_ID'], text=message)
        log_message("INFO", "Telegram notification sent.")
    except Exception as e:
        log_message("ERROR", f"Failed to send Telegram notification: {e}")

# --- Example Usage (for testing utils.py) ---
if __name__ == '__main__':
    # 1. Load Env
    ENV = load_env()
    
    # 2. Init Dirs
    init_dirs(ENV)
    
    # 3. Logging Test
    log_message("INFO", "Utility test started.", ENV)
    log_message("SUCCESS", "Project directories successfully checked.", ENV)
    log_message("ERROR", "Simulated error during download.", ENV)
    
    # 4. Data Storage Test
    test_data = {
        "123456789": {
            "filename": "video1.mp4",
            "timestamp": datetime.now().isoformat(),
            "youtube_url": "https://youtu.be/test1"
        }
    }
    save_uploaded(test_data)
    log_message("INFO", "Test data saved to uploaded.json.", ENV)
    
    loaded_data = load_uploaded()
    log_message("INFO", f"Test data loaded. Keys: {list(loaded_data.keys())}", ENV)
    
    # 5. Telegram Test (Requires valid credentials in .env and bot setup)
    # send_telegram_notification("✅ System initialization test complete.", ENV)
