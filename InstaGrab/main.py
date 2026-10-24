import os
import re
import time
import requests
import json

API_KEY = os.environ.get("ELITE_CLOUD_API_KEY")
WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")  # Naya secret variable
FILES_API_URL = "https://shreecloud.up.railway.app/api/v1/files"

TRACK_FILE = "track.json"
COUNTER_FILE = "counters.json"

def init_files():
    if not os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "w") as f:
            json.dump([], f)
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            json.dump({}, f)

def load_tracked_links():
    try:
        with open(TRACK_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_tracked_link(link):
    tracked = load_tracked_links()
    if link not in tracked:
        tracked.append(link)
        with open(TRACK_FILE, "w") as f:
            json.dump(tracked, f, indent=4)

def load_counters():
    try:
        with open(COUNTER_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def update_counter(username, count):
    counters = load_counters()
    counters[username] = count
    with open(COUNTER_FILE, "w") as f:
        json.dump(counters, f, indent=4)

def get_username(url):
    match = re.search(r'instagram\.com/([^/]+)/', url)
    return match.group(1) if match else "unknown_user"

def check_file_in_elite_cloud(filename):
    print(f"Checking Elite Cloud for file: {filename}...")
    if not API_KEY:
        print("Error: ELITE_CLOUD_API_KEY Missing!")
        return False
        
    headers = {"X-API-Key": API_KEY}
    try:
        response = requests.get(FILES_API_URL, headers=headers)
        if response.status_code == 200:
            # Agar generate kiya hua filename API response mein maujud hai
            if filename in response.text:
                return True
            else:
                return False
        else:
            print(f"Error checking files. Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"API Check Error: {e}")
        return False

def main():
    init_files()
    
    if not WEBHOOK_URL:
        print("Error: N8N_WEBHOOK_URL is not set in secrets!")
        return
        
    if not os.path.exists("link.txt"):
        print("link.txt not found!")
        return

    with open("link.txt", "r") as f:
        all_links = [line.strip() for line in f if line.strip()]

    tracked_links = load_tracked_links()
    links = [link for link in all_links if link not in tracked_links]
    
    if not links:
        print("No new links to process.")
        return

    # Select single target link
    target_link = links[0]
    username = get_username(target_link)
    
    counters = load_counters()
    current_count = counters.get(username, 0)
    new_count = current_count + 1
    
    video_filename = f"{username}.{new_count}.mp4"
    
    print(f"Target Link: {target_link}")
    print(f"Allocated Filename: {video_filename}")
    
    # 1. N8N Webhook par payload send karna
    webhook_payload = {
        "instagram_url": target_link,
        "filename": video_filename,
        "username": username
    }
    
    try:
        print("Sending task to N8N Webhook...")
        response = requests.post(WEBHOOK_URL, json=webhook_payload)
        if response.status_code in [200, 201]:
            print("Webhook triggered successfully.")
        else:
            print(f"Webhook failed with status: {response.status_code}, response: {response.text}")
            return
    except Exception as e:
        print(f"Failed to trigger webhook: {e}")
        return
        
    # 2. Wait for 5 minutes (300 seconds)
    print("Waiting for 5 minutes for N8N to process and upload...")
    time.sleep(300)
    
    # 3. Verify on Elite Cloud
    is_verified = check_file_in_elite_cloud(video_filename)
    
    # 4. JSON Update Logic
    if is_verified:
        print(f"✅ Verification Successful! '{video_filename}' found in Elite Cloud.")
        save_tracked_link(target_link)
        update_counter(username, new_count)
        print("track.json and counters.json updated.")
    else:
        print(f"❌ Verification Failed! '{video_filename}' was NOT found in Elite Cloud.")
        print("JSON files will NOT be updated. Script will retry this link on next run.")

if __name__ == "__main__":
    main()
