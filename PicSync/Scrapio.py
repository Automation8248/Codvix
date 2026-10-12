import os
import json
import random
import time
import requests
from github import Github

# Configurations
GITHUB_TOKEN = os.getenv("GH_TOKEN") 
TARGET_REPO = "Automation8248/Codvix"
BASE_TARGET_PATH = "Pixhub/Social post"

MAIN_FOLDER = "Topic"
TRACK_FILE = "PicSync/track.json"

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
    
    # Duplicates remove karna
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

def main():
    if not GITHUB_TOKEN:
        print("Error: GH_TOKEN set nahi hai.")
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
        print("search.txt khali hai.")
        return

    all_collected_links = set() 
    
    for topic in topics:
        print(f"Searching for: {topic}")
        api_url = f"https://shreevibesbackend-production.up.railway.app/api/v1/search?q={topic}&count=100"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            image_links = data.get("images", []) 
            all_collected_links.update(image_links)
        else:
            print(f"API Error. Status: {response.status_code}")
            
        time.sleep(2) 

    if all_collected_links:
        success = save_to_github(selected_folder, list(all_collected_links))
        if success:
            save_tracked_folder(selected_folder)
            print(f"'{selected_folder}' ko track.json me mark kar diya gaya hai.")
    else:
        print("Koi valid links fetch nahi hue.")

if __name__ == "__main__":
    main()
