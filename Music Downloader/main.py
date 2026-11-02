import os
import requests
import json
import time

# Naye Token Names ke sath environment variables fetch karna
BOT_TOKEN = os.environ.get('AUTOMATION_STORAGE_TOKEN')
CHAT_ID = os.environ.get('AUTOMATION_CHAT_ID')

TOPIC_NAME = "Inspiration Background Music"
LOCAL_DIR = "Music Downloader"
HISTORY_FILE = "history.json"
LINKS_FILE = "link.txt"

# 1. Initialize History JSON
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'r') as f:
        history_data = json.load(f)
else:
    history_data = {
        "thread_id": None,
        "total_uploaded": 0,
        "processed_links": []
    }

def save_history():
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history_data, f, indent=4)

# 2. Local Folder Create Karna
os.makedirs(LOCAL_DIR, exist_ok=True)
print(f"Checked local directory: {LOCAL_DIR}")

# 3. Topic Check ya Create Karna
if not history_data.get("thread_id"):
    print(f"Topic '{TOPIC_NAME}' nahi mila. Naya create kar rahe hain...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/createForumTopic"
    res = requests.post(url, data={'chat_id': CHAT_ID, 'name': TOPIC_NAME}).json()
    
    if res.get('ok'):
        history_data['thread_id'] = res['result']['message_thread_id']
        save_history()
        print(f"Topic Created! THREAD_ID: {history_data['thread_id']}")
    else:
        print("Error creating topic:", res)
        exit(1)

thread_id = history_data['thread_id']

# 4. Links Read Karna
if not os.path.exists(LINKS_FILE):
    print("link.txt file nahi mili! Kripya GitHub me link.txt banayein.")
    exit(1)

with open(LINKS_FILE, 'r') as f:
    links = [line.strip() for line in f if line.strip()]

# 5. Download and Upload Logic
for link in links:
    if link in history_data['processed_links']:
        print(f"Skipped (Already Processed): {link}")
        continue
        
    history_data['total_uploaded'] += 1
    new_filename = f"Bg.music.{history_data['total_uploaded']}.mp3"
    local_filepath = os.path.join(LOCAL_DIR, new_filename)
    
    print(f"Downloading: {link} as {new_filename}...")
    try:
        r = requests.get(link, timeout=30)
        r.raise_for_status()
        
        with open(local_filepath, 'wb') as f:
            f.write(r.content)
            
        print(f"Uploading {new_filename} to Telegram...")
        upload_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
        
        with open(local_filepath, 'rb') as audio_file:
            payload = {
                'chat_id': CHAT_ID,
                'message_thread_id': thread_id,
                'caption': f'🎵 {new_filename}'
            }
            res = requests.post(upload_url, data=payload, files={'audio': audio_file}).json()
            
        if res.get('ok'):
            print(f"Success! {new_filename} uploaded to Topic.")
            history_data['processed_links'].append(link)
            save_history()
            os.remove(local_filepath)
            
            # Telegram API rate limit se bachne ke liye chota pause
            time.sleep(2) 
        else:
            print("Telegram Upload Failed:", res)
            history_data['total_uploaded'] -= 1
            
    except Exception as e:
        print(f"Error processing {link}: {e}")
        history_data['total_uploaded'] -= 1

print("Automation execution completed successfully!")
