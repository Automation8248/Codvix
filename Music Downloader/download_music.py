import os
import re
import time
import requests

# Set target directory for GitHub repo
TARGET_DIR = "Intresting Fact/music"
os.makedirs(TARGET_DIR, exist_ok=True)

def download_pixabay_music():
    print("Fetching soft piano music from Pixabay...")
    search_url = "https://pixabay.com/audio/search/soft%20piano/?order=None"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch Pixabay page: {e}")
        return

    # Extract mp3 CDN links from the page source
    mp3_links = re.findall(r'(https?://cdn\.pixabay\.com/audio/[^"\']+\.mp3)', response.text)
    unique_links = list(dict.fromkeys(mp3_links))
    print(f"Found {len(unique_links)} tracks.")
    
    downloaded_count = 0
    target_count = 20
    
    for link in unique_links:
        if downloaded_count >= target_count:
            break
            
        # Updated file name format: bg-music.1.mp3, bg-music.2.mp3
        file_name = f"bg-music.{downloaded_count + 1}.mp3"
        file_path = os.path.join(TARGET_DIR, file_name)
        
        # Skip if file already exists
        if os.path.exists(file_path):
            print(f"Already exists: {file_name}")
            downloaded_count += 1
            continue
            
        print(f"Downloading {file_name}...")
        try:
            audio_req = requests.get(link, headers=headers)
            if audio_req.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(audio_req.content)
                print(f"Success: {file_name}")
                downloaded_count += 1
                # 2-second delay to avoid rate-limiting
                time.sleep(2)
        except Exception as e:
            print(f"Error downloading {link}: {e}")

if __name__ == "__main__":
    download_pixabay_music()
