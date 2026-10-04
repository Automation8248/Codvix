import os
import time
import requests
import json
import random
from datetime import datetime

# --- Configuration ---
TARGET_REPO_DIR = "Postza" 
PHOTOS_DIR = os.path.join(TARGET_REPO_DIR, "RadhaSocialSync", "photos")

SEARCH_FILE = "search.txt"
HISTORY_FILE = "history.json"
API_URL = "https://shreevibesbackend-production.up.railway.app/api/v1/search"
MAX_TOPICS_PER_DAY = 10

# 50+ Real User-Agents List
USER_AGENTS = [
    # Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    
    # macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",

    # Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (X11; Linux i686; rv:118.0) Gecko/20100101 Firefox/118.0",
    
    # iOS (iPhone/iPad)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    
    # Android
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.193 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.193 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.111 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.153 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.193 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 13; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0",
    "Mozilla/5.0 (Android 12; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0",
    "Mozilla/5.0 (Android 11; Mobile; rv:119.0) Gecko/119.0 Firefox/119.0",
    
    # Others / Edge / Opera
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Vivaldi/6.5.3206.50",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Vivaldi/6.4.3160.42"
]

def get_random_header():
    """Returns headers with a random User-Agent"""
    return {"User-Agent": random.choice(USER_AGENTS)}

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history.json: {e}")
            
    return {
        "downloaded_urls": [],
        "completed_topics": [],
        "last_run_date": "",
        "topics_processed_today": 0,
        "last_image_number": 0
    }

def save_history(data):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_topics():
    if not os.path.exists(SEARCH_FILE):
        print("search.txt file nahi mili!")
        return []
    with open(SEARCH_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in file.readlines() if line.strip()]

def fetch_and_download():
    history = load_history()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    if history.get("last_run_date") != today_str:
        history["last_run_date"] = today_str
        history["topics_processed_today"] = 0

    topics = get_topics()
    pending_topics = [t for t in topics if t not in history["completed_topics"]]
    
    if not pending_topics:
        print("✅ Saare search topics complete ho chuke hain! Automation will now stop.")
        return

    os.makedirs(PHOTOS_DIR, exist_ok=True)
    counts_to_try = [100, 85, 50, 25]

    for category in pending_topics:
        if history["topics_processed_today"] >= MAX_TOPICS_PER_DAY:
            print(f"🛑 Aaj ki 10 topics ki limit puri ho gayi. Baki kal process honge.")
            break

        print(f"\n--- Processing Topic: {category} ---")
        api_data = None
        
        for count in counts_to_try:
            print(f"Requesting '{category}' with count={count}...")
            try:
                params = {"query": category, "count": count}
                # Random header use kiya
                response = requests.get(API_URL, headers=get_random_header(), params=params)
                if response.status_code == 200:
                    api_data = response.json()
                    print(f"Success! Found {api_data.get('count', 0)} images.")
                    break
            except Exception as e:
                print(f"API Error: {e}")
            time.sleep(2)
            
        if not api_data:
            print(f"❌ Sabhi attempts fail. Skipping '{category}'.")
            continue

        results = api_data.get("results", [])
        downloaded_in_topic = 0

        for item in results:
            img_url = item.get("large")
            if not img_url or img_url in history["downloaded_urls"]:
                continue

            time.sleep(2.5)
            
            try:
                ext = img_url.split('.')[-1].split('?')[0].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                    ext = 'jpg'
                
                history["last_image_number"] += 1
                file_name = f"Image_{history['last_image_number']}.{ext}"
                file_path = os.path.join(PHOTOS_DIR, file_name)
                
                # Image download ke waqt bhi random header
                img_response = requests.get(img_url, headers=get_random_header())
                if img_response.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(img_response.content)
                        
                    print(f"Saved: {file_name}")
                    history["downloaded_urls"].append(img_url)
                    downloaded_in_topic += 1
                    
                    save_history(history)
            except Exception as e:
                print(f"Image download error: {e}")

        history["completed_topics"].append(category)
        history["topics_processed_today"] += 1
        save_history(history)
        print(f"✅ Topic '{category}' completed and saved to history.")

if __name__ == "__main__":
    fetch_and_download()
