import os
import json
import random
import time
import requests
import concurrent.futures
from github import Github

# Configurations
GITHUB_TOKEN = os.getenv("GH_TOKEN") 
TARGET_REPO = "Automation8248/Codvix"
BASE_TARGET_PATH = "Pixhub/Social post"

MAIN_FOLDER = "PicSync/Topic"
TRACK_FILE = "PicSync/track.json"

# 50+ Random User Agents ka Pool
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.101 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 OPR/102.0.0.0",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (Linux; Android 10; SM-A505F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 OPR/92.0.0.0",
    "Mozilla/5.0 (X11; CrOS x86_64 14526.89.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.133 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Mozilla/5.0 (Linux; Android 11; POCO X3 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36 Edg/103.0.1264.71",
    "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; CPH2127) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0"
]

def load_tracked_folders():
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_tracked_folder(folder_name):
    tracked = load_tracked_folders()
    if folder_name not in tracked:
        tracked.append(folder_name)
        os.makedirs(os.path.dirname(TRACK_FILE), exist_ok=True)
        with open(TRACK_FILE, "w", encoding="utf-8") as file:
            json.dump(tracked, file, indent=4)

def get_random_untracked_folder(base_folder, tracked_folders):
    subfolders = [f.name for f in os.scandir(base_folder) if f.is_dir()]
    untracked_folders = [f for f in subfolders if f not in tracked_folders]
    if not untracked_folders:
        return None
    return random.choice(untracked_folders)

def get_existing_links_from_github(repo, file_path):
    try:
        file = repo.get_contents(file_path)
        content = file.decoded_content.decode("utf-8")
        existing_links = [line.strip() for line in content.split("\n") if line.strip()]
        return existing_links, file.sha
    except Exception:
        return [], None

def save_to_github(folder_name, new_links):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(TARGET_REPO)
    file_path = f"{BASE_TARGET_PATH}/{folder_name}/link.txt"
    
    print(f"Checking existing links at {file_path}...")
    existing_links, file_sha = get_existing_links_from_github(repo, file_path)
    
    existing_set = set(existing_links)
    unique_new_links = [link for link in new_links if link not in existing_set]
    
    if not unique_new_links:
        print("Koi naya unique link nahi mila. Sabhi links pehle se maujud hain.")
        return True
        
    print(f"{len(unique_new_links)} naye unique links mile. Saving to GitHub...")
    final_links = existing_links + unique_new_links
    content = "\n".join(final_links)
    
    try:
        if file_sha:
            repo.update_file(file_path, f"Update links for {folder_name}", content, file_sha)
            print(f"Success: {file_path} update ho gayi.")
        else:
            repo.create_file(file_path, f"Create links for {folder_name}", content)
            print(f"Success: Nayi file {file_path} create ho gayi.")
        return True
    except Exception as e:
        print(f"GitHub par save karte waqt error: {e}")
        return False

def fetch_links_for_topic(topic):
    """Ye function API call karega random User-Agent ke sath"""
    extracted_links = []
    # 50+ me se ek random user agent uthana
    ua = random.choice(USER_AGENTS)
    headers = {"User-Agent": ua}
    
    api_url = f"https://shreevibesbackend-production.up.railway.app/api/v1/search?q={topic}&count=100"
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            # JSON se 'results' list ko lena
            results = data.get("results", [])
            for item in results:
                # JSON me "large" key se image url nikalna (jo jpg/png/webp hai)
                link = item.get("large")
                if link:
                    extracted_links.append(link)
                    
            print(f"✅ Topic '{topic}' ke liye {len(extracted_links)} links mile (UA: {ua[:20]}...)")
        else:
            print(f"❌ API Error for '{topic}'. Status: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error in fetching '{topic}': {e}")
        
    # Rate limit handle karne ke liye halka delay, taaki block na ho
    time.sleep(random.uniform(1.0, 3.0)) 
    return extracted_links

def main():
    if not GITHUB_TOKEN:
        print("Error: GH_TOKEN set nahi hai.")
        return

    if not os.path.exists(MAIN_FOLDER):
        print(f"Error: '{MAIN_FOLDER}' folder nahi mila. Kripya GitHub par folder push karein.")
        return

    tracked_folders = load_tracked_folders()
    selected_folder = get_random_untracked_folder(MAIN_FOLDER, tracked_folders)
    
    if not selected_folder:
        print("Sabhi folders process ho chuke hain! (track.json me sabhi listed hain)")
        return
        
    print(f"Selected Folder: '{selected_folder}'")
    search_file_path = os.path.join(MAIN_FOLDER, selected_folder, "search.txt")
    
    if not os.path.exists(search_file_path):
        print(f"Error: {search_file_path} nahi mila.")
        return

    with open(search_file_path, "r", encoding="utf-8") as file:
        topics = [line.strip() for line in file if line.strip()]
        
    if not topics:
        print(f"{search_file_path} khali hai.")
        return

    all_collected_links = set()
    
    print(f"🚀 {len(topics)} topics mile hain. 5 Workers ke sath fast scraping chalu ki jaa rahi hai...\n")
    
    # 5 concurrent workers (5 user agents ek sath) kaam karenge yahan par
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Executor topics ko fast parallel threads me run karega
        futures = {executor.submit(fetch_links_for_topic, topic): topic for topic in topics}
        
        for future in concurrent.futures.as_completed(futures):
            topic_links = future.result()
            if topic_links:
                all_collected_links.update(topic_links)

    if all_collected_links:
        success = save_to_github(selected_folder, list(all_collected_links))
        if success:
            save_tracked_folder(selected_folder)
            print(f"🎯 '{selected_folder}' ko track.json me mark kar diya gaya hai.")
    else:
        print("Koi valid links fetch nahi hue.")

if __name__ == "__main__":
    main()
