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

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
]

def load_tracking():
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                # Purana list format ho toh naye dict format me badlo
                if isinstance(data, list):
                    return {"completed_folders": data, "folder_progress": {}}
                return data
            except:
                pass
    return {"completed_folders": [], "folder_progress": {}}

def save_tracking(data):
    os.makedirs(os.path.dirname(TRACK_FILE), exist_ok=True)
    with open(TRACK_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

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
    
    existing_links, file_sha = get_existing_links_from_github(repo, file_path)
    
    existing_set = set(existing_links)
    unique_new_links = [link for link in new_links if link not in existing_set]
    
    if not unique_new_links:
        print("Koi naya unique link nahi mila. Sabhi links pehle se maujud hain.")
        return True
        
    print(f"{len(unique_new_links)} naye unique links mile. GitHub par save ho raha hai...")
    final_links = existing_links + unique_new_links
    content = "\n".join(final_links)
    
    try:
        if file_sha:
            repo.update_file(file_path, f"Update links for {folder_name} (Batch Process)", content, file_sha)
        else:
            repo.create_file(file_path, f"Create links for {folder_name} (Batch Process)", content)
        print(f"Success: File GitHub par update/create ho gayi.")
        return True
    except Exception as e:
        print(f"GitHub par save karte waqt error: {e}")
        return False

def fetch_links_for_topic(topic):
    extracted_links = []
    ua = random.choice(USER_AGENTS)
    headers = {"User-Agent": ua}
    
    api_url = f"https://shreevibesbackend-production.up.railway.app/api/v1/search?q={topic}&count=100"
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("results", []):
                link = item.get("large")
                if link:
                    extracted_links.append(link)
            print(f"✅ Topic '{topic}' -> {len(extracted_links)} links mile.")
        else:
            print(f"❌ API Error for '{topic}'. Status: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error in fetching '{topic}': {e}")
        
    time.sleep(random.uniform(1.0, 3.0)) 
    return extracted_links

def main():
    if not GITHUB_TOKEN:
        print("Error: GH_TOKEN set nahi hai.")
        return

    if not os.path.exists(MAIN_FOLDER):
        print(f"Error: '{MAIN_FOLDER}' folder nahi mila. Kripya GitHub par folder push karein.")
        return

    tracking = load_tracking()
    
    all_folders = [f.name for f in os.scandir(MAIN_FOLDER) if f.is_dir()]
    uncompleted_folders = [f for f in all_folders if f not in tracking["completed_folders"]]
    
    if not uncompleted_folders:
        print("Sabhi folders aur unke topics process ho chuke hain!")
        return

    # Check agar koi folder pehle se in progress hai
    in_progress = [f for f in uncompleted_folders if f in tracking.get("folder_progress", {})]
    
    if in_progress:
        selected_folder = in_progress[0]
        print(f"Resuming Folder: '{selected_folder}'")
    else:
        selected_folder = random.choice(uncompleted_folders)
        print(f"New Folder Selected: '{selected_folder}'")

    search_file_path = os.path.join(MAIN_FOLDER, selected_folder, "search.txt")
    if not os.path.exists(search_file_path):
        print(f"Error: {search_file_path} nahi mila.")
        return

    with open(search_file_path, "r", encoding="utf-8") as file:
        all_topics = [line.strip() for line in file if line.strip()]
        
    if not all_topics:
        print(f"{search_file_path} khali hai.")
        return

    # Nikaalna ki kaun se topics ho gaye hain
    processed_topics = tracking["folder_progress"].get(selected_folder, [])
    unprocessed_topics = [t for t in all_topics if t not in processed_topics]

    if not unprocessed_topics:
        print(f"Folder '{selected_folder}' ke sabhi topics ho chuke hain. Marking as completed.")
        tracking["completed_folders"].append(selected_folder)
        save_tracking(tracking)
        return

    # Sirf 10 Topics select karna
    topics_to_process = unprocessed_topics[:10]
    print(f"🚀 Is run me {len(topics_to_process)} topics process kiye jayenge (Bache hue: {len(unprocessed_topics) - len(topics_to_process)}).")

    all_collected_links = set()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_links_for_topic, topic): topic for topic in topics_to_process}
        for future in concurrent.futures.as_completed(futures):
            topic_links = future.result()
            if topic_links:
                all_collected_links.update(topic_links)

    if all_collected_links:
        success = save_to_github(selected_folder, list(all_collected_links))
        if success:
            # Track.json update karna
            processed_topics.extend(topics_to_process)
            tracking["folder_progress"][selected_folder] = processed_topics
            
            # Agar sabhi topics ho gaye toh folder completed mark karo
            if len(processed_topics) >= len(all_topics):
                tracking["completed_folders"].append(selected_folder)
                print(f"🎯 Folder '{selected_folder}' ke 100% topics pure ho gaye!")
            
            save_tracking(tracking)
            print(f"Track.json me progress update kar di gayi hai.")
    else:
        print("Koi valid links fetch nahi hue.")

if __name__ == "__main__":
    main()
