import os
import time
import requests

# Target directory jahan files save hongi (GitHub repo path)
TARGET_DIR = "Intresting Fact/music"
os.makedirs(TARGET_DIR, exist_ok=True)

def download_pixabay_music():
    print("Fetching soft piano background music using Pixabay API...")
    
    # GitHub Secrets se PIXABAY_KEY fetch karna
    api_key = os.environ.get("PIXABAY_KEY")
    if not api_key:
        print("Error: PIXABAY_KEY environment variable is not set.")
        return

    # Pixabay Audio API Endpoint
    search_url = "https://pixabay.com/api/audio/"
    
    params = {
        "key": api_key,
        "q": "soft piano background music",
        "per_page": 20 # Kam se kam 20 results mangane ke liye
    }
    
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Failed to fetch from Pixabay API: {e}")
        return

    hits = data.get("hits", [])
    print(f"Found {len(hits)} tracks from API.")
    
    downloaded_count = 0
    target_count = 20
    
    for hit in hits:
        if downloaded_count >= target_count:
            break
            
        # API response mein audio url find karna
        audio_url = hit.get("preview_url") or hit.get("url") or hit.get("download_url")
        if not audio_url:
            continue
            
        # File name format: bg-music.1.mp3, bg-music.2.mp3...
        file_name = f"bg-music.{downloaded_count + 1}.mp3"
        file_path = os.path.join(TARGET_DIR, file_name)
        
        # Agar file pehle se exist karti hai toh skip karein
        if os.path.exists(file_path):
            print(f"Already exists: {file_name}")
            downloaded_count += 1
            continue
            
        print(f"Downloading {file_name}...")
        try:
            audio_req = requests.get(audio_url)
            if audio_req.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(audio_req.content)
                print(f"Success: {file_name}")
                downloaded_count += 1
                time.sleep(1) # API rate limit se bachne ke liye chhota delay
        except Exception as e:
            print(f"Error downloading {audio_url}: {e}")

if __name__ == "__main__":
    download_pixabay_music()
