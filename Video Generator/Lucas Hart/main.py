import os
import requests
import json
import random
import traceback
import re
from datetime import datetime
from github import Github
from moviepy.editor import ImageClip, TextClip, AudioFileClip, CompositeVideoClip

# ================= Configuration =================
DURATION = 10
FIXED_AUTHOR = "Lucas Hart"

# Dual Repository Setup
TRACKING_REPO_NAME = "Automation8248/Codvix"  # Track.json yahan rahega
TARGET_REPO_NAME = "Automation8248/Postza"    # Video aur caption.txt yahan jayega

# Environment Variables
GH_TOKEN = os.environ.get("GH_TOKEN")
TELEGRAM_FAILD_TOKEN = os.environ.get("TELEGRAM_FAILD_TOKEN")
TELEGRAM_FAILD_ID = os.environ.get("TELEGRAM_FAILD_ID")
THREAD_ID = 8  # Fixed Thread ID for Telegram Alerts

# GitHub Paths
TRACK_FILE_PATH = "Video Generator/Lucas Hart/track.json"
CAPTION_FILE_PATH = "Lucas Hart/caption.txt"
VIDEO_FOLDER_PATH = "Lucas Hart/video"
# =================================================

def send_telegram_error(error_msg):
    """Sends an error alert to the specific Telegram Thread."""
    if not TELEGRAM_FAILD_TOKEN or not TELEGRAM_FAILD_ID:
        print("Telegram tokens are missing. Cannot send alert.")
        return
    
    error_text = (
        f"🚨 *Automation Failed!*\n\n"
        f"*Repo:* Codvix\n"
        f"*Folder:* Video Generator\n"
        f"*Account:* Lucas\n\n"
        f"*Error:*\n`{error_msg}`"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_FAILD_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_FAILD_ID,
        "message_thread_id": THREAD_ID,
        "text": error_text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Telegram alert failed: {e}")

def get_headers():
    """Returns standard browser headers for requests to avoid blocking."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

def download_image_file(link, output_path):
    file_id_match = re.search(r'id=([a-zA-Z0-9_-]+)', link) or re.search(r'/d/([a-zA-Z0-9_-]+)', link)
    url = f"https://drive.google.com/uc?id={file_id_match.group(1)}" if file_id_match else link
    res = requests.get(url, headers=get_headers(), allow_redirects=True)
    if res.status_code == 200:
        with open(output_path, "wb") as f: f.write(res.content)
        return output_path
    raise Exception(f"Failed to download image. Status code: {res.status_code}")

def download_audio_file(link, output_path):
    res = requests.get(link, headers=get_headers(), allow_redirects=True)
    if res.status_code == 200:
        with open(output_path, "wb") as f: f.write(res.content)
        return output_path
    raise Exception("Failed to download direct audio file.")

def get_file_with_cooling(file_type, folder_name, history):
    """Filters by 60-day cooling, downloads the file, updates tracking, and returns local path."""
    today = datetime.now().date()
    cooling_dict = history.setdefault(f"cooling_{file_type}", {})
    
    # Read links based on file_type
    if file_type == "images":
        with open("images.txt", "r") as f: links_list = f.readlines()
    else:
        with open("bg_link.txt", "r") as f: links_list = f.readlines()
        
    available_links = []
    for link in links_list:
        link = link.strip()
        if not link: continue
        
        last_used_str = cooling_dict.get(link)
        if last_used_str:
            last_used_date = datetime.strptime(last_used_str, "%Y-%m-%d").date()
            if (today - last_used_date).days < 60:
                continue
        available_links.append(link)
        
    print(f"[DEBUG] {file_type.capitalize()} available after 60-day cooling: {len(available_links)}")
    if not available_links: return None
        
    selected_link = random.choice(available_links)
    history[f"cooling_{file_type}"][selected_link] = today.strftime("%Y-%m-%d")
    
    # Download and update explicit tracking
    if file_type == "images":
        history["last_used_image"] = selected_link
        return download_image_file(selected_link, "temp_bg.jpg")
    else:
        history["last_used_audio"] = selected_link
        return download_audio_file(selected_link, "temp_audio.mp3")

# --- USER'S EXACT API & VIDEO LOGIC ---
def get_free_quote_only():
    try:
        res = requests.get("https://zenquotes.io/api/random", headers=get_headers(), timeout=10)
        return res.json()[0]['q']
    except: return "Your only limit is your mind."

def create_video(quote_text, history):
    bg_path = get_file_with_cooling("images", "images", history)
    if not bg_path: 
        raise Exception("Images folder khali hai ya sabhi images abhi 60 din ke cooling me hain. Kuch nayi images add karein!")

    bg = ImageClip(bg_path).set_duration(DURATION).resize(height=1920).fl_image(lambda image: (image * 0.6).astype('uint8'))
    
    full_display_text = f"\"{quote_text}\"\n\n{FIXED_AUTHOR}"
    txt = TextClip(full_display_text, fontsize=80, color='white', font='Arial-Bold', 
                   method='caption', size=(850, None)).set_duration(DURATION).set_position('center')
    
    audio_path = get_file_with_cooling("ringtones", "ringtones", history)
    audio = None
    if audio_path:
        try: 
            audio = AudioFileClip(audio_path).subclip(0, DURATION)
        except Exception as e: 
            print(f"Audio Load Error: {e}")
    else:
        print("Bina audio ke video ban rahi hai (Ringtones cooling me hain ya folder khali hai).")
    
    final = CompositeVideoClip([bg, txt])
    if audio: final = final.set_audio(audio)
    
    final.write_videofile("final_short.mp4", fps=24, codec="libx264", audio_codec="aac")
    return "final_short.mp4"
# ---------------------------------------

def update_github_file(repo, path, content, message):
    try:
        file = repo.get_contents(path)
        repo.update_file(path, message, content, file.sha)
    except:
        repo.create_file(path, message, content)

def main():
    try:
        if not GH_TOKEN: raise Exception("GH_TOKEN is not set.")
        g = Github(GH_TOKEN)
        
        track_repo = g.get_repo(TRACKING_REPO_NAME)
        target_repo = g.get_repo(TARGET_REPO_NAME)
        
        # Load History
        try:
            track_file = track_repo.get_contents(TRACK_FILE_PATH)
            track_data = json.loads(track_file.decoded_content.decode('utf-8'))
        except:
            track_data = {"current_video": 1, "cooling_images": {}, "cooling_ringtones": {}}

        # Determine Loop Name
        current_video_num = track_data.get("current_video", 1)
        if current_video_num > 90: current_video_num = 1
        video_filename = f"shorts.{current_video_num}.mp4"
        
        # Quote Fetch
        quote_text = get_free_quote_only()

        # Generate Video using your exact logic
        print(f"[DEBUG] Compiling Video {video_filename}...")
        generated_video_name = create_video(quote_text, track_data)
        os.rename(generated_video_name, video_filename)

        # Upload Video
        print(f"[DEBUG] Uploading {video_filename} to {TARGET_REPO_NAME}...")
        with open(video_filename, "rb") as f:
            update_github_file(target_repo, f"{VIDEO_FOLDER_PATH}/{video_filename}", f.read(), f"Upload {video_filename}")
        
        # Upload Caption
        try:
            q_file = target_repo.get_contents(CAPTION_FILE_PATH)
            new_quotes = q_file.decoded_content.decode('utf-8') + f"\n{quote_text}"
            target_repo.update_file(CAPTION_FILE_PATH, f"Added caption for {video_filename}", new_quotes, q_file.sha)
        except:
            target_repo.create_file(CAPTION_FILE_PATH, "Created caption.txt", quote_text)
            
        # Update JSON Track
        track_data["current_video"] = current_video_num + 1
        track_data["last_generated_video"] = video_filename
        update_github_file(track_repo, TRACK_FILE_PATH, json.dumps(track_data, indent=4), f"Update track.json post {video_filename}")

        print(f"Success: {video_filename} generated and uploaded.")

        # Cleanup locally
        if os.path.exists("temp_bg.jpg"): os.remove("temp_bg.jpg")
        if os.path.exists("temp_audio.mp3"): os.remove("temp_audio.mp3")
        if os.path.exists(video_filename): os.remove(video_filename)

    except Exception as e:
        print(traceback.format_exc())
        send_telegram_error(str(e))

if __name__ == "__main__":
    main()
