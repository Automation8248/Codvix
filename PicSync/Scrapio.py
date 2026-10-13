import os
import json
import random
import time
import requests
from github import Github

# ================= Configurations =================
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
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
]

# ================= Helper Functions =================
def load_tracking():
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
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

def save_to_github(folder_path, new_links):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(TARGET_REPO)
    file_path = f"{BASE_TARGET_PATH}/{folder_path}/link.txt"
    
    existing_links, file_sha = get_existing_links_from_github(repo, file_path)
    
    existing_set = set(existing_links)
    unique_new_links = [link for link in new_links if link not in existing_set]
    
    if not unique_new_links:
        print(f"Koi naya link nahi mila '{folder_path}' ke liye.")
        return True
        
    print(f"[{folder_path}] -> {len(unique_new_links)} naye links GitHub par save ho rahe hain...")
    final_links = existing_links + unique_new_links
    content = "\n".join(final_links)
    
    try:
        if file_sha:
            repo.update_file(file_path, f"Update links for {folder_path}", content, file_sha)
        else:
            repo.create_file(file_path, f"Create links for {folder_path}", content)
        print(f"✅ Success: {file_path} update/create ho gayi.")
        return True
    except Exception as e:
        print(f"❌ GitHub par save karte waqt error ({folder_path}): {e}")
        return False

def fetch_links_for_topic(topic):
    extracted_links = []
    ua = random.choice(USER_AGENTS)
    headers = {"User-Agent": ua}
    
    api_url = f"https://shreevibesbackend-production.up.railway.app/api/v1/search?q={topic}&count=100"
    try:
        response = requests.get(api_url, headers=headers, timeout=60)
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
        
    return extracted_links

# ================= Main Execution =================
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

    # Check for in-progress folder
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

    processed_topics = tracking["folder_progress"].get(selected_folder, [])
    unprocessed_topics = [t for t in all_topics if t not in processed_topics]

    if not unprocessed_topics:
        print(f"Folder '{selected_folder}' ke sabhi topics ho chuke hain. Marking as completed.")
        tracking["completed_folders"].append(selected_folder)
        save_tracking(tracking)
        return

    # Sirf 10 topics process karega ek run mein
    topics_to_process = unprocessed_topics[:10]
    print(f"🚀 Is run me {len(topics_to_process)} topics process kiye jayenge (Bache hue: {len(unprocessed_topics) - len(topics_to_process)}).")

    # Links ko first word ke hisab se group karne ke liye dictionary
    grouped_links = {}
    
    for idx, topic in enumerate(topics_to_process, 1):
        topic_links = fetch_links_for_topic(topic)
        
        if topic_links:
            # YAHAN LOGIC HAI: "parrot photography" -> "Parrot"
            first_word = topic.split()[0].title() 
            
            if first_word not in grouped_links:
                grouped_links[first_word] = set()
            grouped_links[first_word].update(topic_links)
            
        if idx < len(topics_to_process):
            print("⏳ Agle topic ke liye 6 second ka wait kar rahe hain taaki server crash na ho...")
            time.sleep(6)

    # grouped_links me ab data is tarah hoga: {"Parrot": [links...], "Owl": [links...]}
    if grouped_links:
        for first_word, links_set in grouped_links.items():
            # Yahan target path banega (e.g., Birds/Parrot, Birds/Owl)
            target_subfolder_path = f"{selected_folder}/{first_word}"
            save_to_github(target_subfolder_path, list(links_set))
            
        # Tracker update karein
        processed_topics.extend(topics_to_process)
        tracking["folder_progress"][selected_folder] = processed_topics
        
        if len(processed_topics) >= len(all_topics):
            tracking["completed_folders"].append(selected_folder)
            print(f"🎯 Folder '{selected_folder}' ke 100% topics pure ho gaye!")
        
        save_tracking(tracking)
        print(f"Track.json me progress update kar di gayi hai.")
    else:
        print("Koi valid links fetch nahi hue.")

if __name__ == "__main__":
    main()
