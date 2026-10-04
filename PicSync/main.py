import os
import time
import requests
import json
import random
import concurrent.futures
from datetime import datetime

# --- Configuration ---
TARGET_REPO_DIR = "Postza" 
PHOTOS_DIR = os.path.join(TARGET_REPO_DIR, "RadhaSocialSync", "photos")

SEARCH_FILE = "search.txt"
HISTORY_FILE = "history.json"
TXT_HISTORY_FILE = "history.txt"
API_URL = "https://shreevibesbackend-production.up.railway.app/api/v1/search"
MAX_TOPICS_PER_DAY = 10
MAX_WORKERS = 5 # Ek sath 5 images download hongi

# 65+ Real User-Agents List
USER_AGENTS = [
    # Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Vivaldi/6.5.3206.50",
    # macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.3; rv:123.0) Gecko/20100101 Firefox/123.0",
    # Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    # iOS
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    # Android
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 14; Mobile; rv:123.0) Gecko/123.0 Firefox/123.0",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 Chrome/115.0.0.0 Mobile Safari/537.36"
    # Note: Maine space clean rakhne ke liye kuch duplicate agents hide kiye hain, par aap chahein to apna full 65+ list yahan chipka sakte hain.
]

# Global Session (Connection reuse karne ke liye fast hai)
session = requests.Session()

def get_random_header():
    return {"User-Agent": random.choice(USER_AGENTS)}

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
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

def save_urls_to_txt_batch(urls):
    """Multiple URLs ko ek sath text file me likhne ke liye"""
    if not urls:
        return
    with open(TXT_HISTORY_FILE, "a", encoding="utf-8") as f:
        for url in urls:
            f.write(url + "\n")

def get_topics():
    if not os.path.exists(SEARCH_FILE):
        print("search.txt file nahi mili!")
        return []
    with open(SEARCH_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def download_one_image(task):
    """Worker function jo ThreadPoolExecutor call karega"""
    url, filename = task
    file_path = os.path.join(PHOTOS_DIR, filename)
    try:
        # Timeout (connect, read) aur streaming enabled
        resp = session.get(url, headers=get_random_header(), timeout=(5, 15), stream=True)
        if resp.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True, url, filename
        return False, url, None
    except Exception as e:
        return False, url, None

def fetch_and_download():
    history = load_history()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    if history.get("last_run_date") != today_str:
        history["last_run_date"] = today_str
        history["topics_processed_today"] = 0

    topics = get_topics()
    pending_topics = [t for t in topics if t not in history["completed_topics"]]
    
    if not pending_topics:
        print("✅ Saare topics complete ho chuke hain! Automation will stop.")
        return

    os.makedirs(PHOTOS_DIR, exist_ok=True)
    counts_to_try = [100, 85, 50, 25]
    
    # Fast lookup ke liye Set ka use kiya hai
    downloaded_set = set(history["downloaded_urls"])

    for category in pending_topics:
        if history["topics_processed_today"] >= MAX_TOPICS_PER_DAY:
            print(f"🛑 Aaj ki {MAX_TOPICS_PER_DAY} topics ki limit puri ho gayi.")
            break

        print(f"\n--- Processing Topic: {category} ---")
        api_data = None
        
        # API Searching 
        for count in counts_to_try:
            print(f"Requesting '{category}' with count={count}...")
            try:
                params = {"q": category, "count": count}
                response = session.get(API_URL, headers=get_random_header(), params=params, timeout=(5, 20))
                if response.status_code == 200:
                    api_data = response.json()
                    print(f"Success! Found {api_data.get('count', 0)} images.")
                    break
            except Exception as e:
                print(f"API Error: {e}")
            time.sleep(1.5) # API limit safety ke liye bas thoda sa delay 
            
        if not api_data:
            print(f"❌ Sabhi attempts fail. Skipping '{category}'.")
            continue

        results = api_data.get("results", [])
        tasks = []
        
        # Sabse pehle saari valid URLs ka batch collect karenge
        for item in results:
            img_url = item.get("large")
            if not img_url or img_url in downloaded_set:
                continue
            
            ext = img_url.split('.')[-1].split('?')[0].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                ext = 'jpg'
            
            history["last_image_number"] += 1
            file_name = f"Image_{history['last_image_number']}.{ext}"
            
            # (URL, FileName) ka tuple task list me add karna
            tasks.append((img_url, file_name))
        
        if not tasks:
            print("Is topic me koi nayi images nahi mili.")
            history["completed_topics"].append(category)
            save_history(history)
            continue
            
        print(f"⏳ Downloading {len(tasks)} new images in parallel...")
        successful_urls = []
        
        # THREAD POOL EXECUTION (Speed Boost)
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(download_one_image, task): task for task in tasks}
            
            for future in concurrent.futures.as_completed(futures):
                success, url, filename = future.result()
                if success:
                    successful_urls.append(url)
                    downloaded_set.add(url)
                    print(f"✅ Saved: {filename}")
                else:
                    print(f"❌ Failed to download: {url}")

        # HAR TOPIC KE END ME BATCH DISK WRITE (Super Fast I/O)
        history["downloaded_urls"].extend(successful_urls)
        history["completed_topics"].append(category)
        history["topics_processed_today"] += 1
        
        save_history(history)
        save_urls_to_txt_batch(successful_urls)
        
        print(f"✅ Topic '{category}' completed! Saved {len(successful_urls)} images.")
        time.sleep(2) # Dusre topic par jane se pehle ek chhota sa gap

if __name__ == "__main__":
    fetch_and_download()
