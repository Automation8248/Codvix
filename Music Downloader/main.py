import os
import requests
import json
import time

# Tokens fetch karna
BOT_TOKEN = os.environ.get('AUTOMATION_STORAGE_TOKEN')
CHAT_ID = os.environ.get('AUTOMATION_CHAT_ID')  # Isme -1003943566179 hona chahiye
THREAD_ID = 2  # Link se mila exact Topic ID

LOCAL_DIR = "temp_audio"
HISTORY_FILE = "history.json"
LINKS_FILE = "link.txt"

# 1. Initialize History JSON
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'r') as f:
        history_data = json.load(f)
else:
    history_data = {
        "total_uploaded": 0,
        "processed_links": []
    }

def save_history():
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history_data, f, indent=4)

# 2. Local Folder Create Karna
os.makedirs(LOCAL_DIR, exist_ok=True)
print(f"Checked local directory: {LOCAL_DIR}")

# 3. Links Read Karna
if not os.path.exists(LINKS_FILE):
    print("link.txt file nahi mili! Kripya check karein.")
    exit(1)

with open(LINKS_FILE, 'r') as f:
    links = [line.strip() for line in f if line.strip()]

# 4. Download and Upload Logic
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
            
        print(f"Uploading {new_filename} to Topic {THREAD_ID}...")
        upload_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
        
        with open(local_filepath, 'rb') as audio_file:
            payload = {
                'chat_id': CHAT_ID,
                'message_thread_id': THREAD_ID, # Direct aapke topic me jayega
                'caption': f'🎵 {new_filename}'
            }
            res = requests.post(upload_url, data=payload, files={'audio': audio_file}).json()
            
        if res.get('ok'):
            print(f"Success! {new_filename} uploaded.")
            history_data['processed_links'].append(link)
            save_history()
            os.remove(local_filepath)
            
            time.sleep(2) # Rate limit bachav
        else:
            print("Telegram Upload Failed:", res)
            history_data['total_uploaded'] -= 1
            
    except Exception as e:
        print(f"Error processing {link}: {e}")
        history_data['total_uploaded'] -= 1

print("Automation completed!")
