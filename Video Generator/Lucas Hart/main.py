import os
import requests
import json
import random
import traceback
import re
import textwrap
from datetime import datetime
from github import Github
from moviepy.editor import ImageClip, AudioFileClip
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

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
    if not TELEGRAM_FAILD_TOKEN or not TELEGRAM_FAILD_ID:
        return
    error_text = (
        f"🚨 *Automation Failed!*\n\n"
        f"*Repo:* Codvix\n"
        f"*Folder:* Video Generator\n"
        f"*Account:* Lucas\n\n"
        f"*Error:*\n`{error_msg}`"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_FAILD_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_FAILD_ID, "message_thread_id": THREAD_ID, "text": error_text, "parse_mode": "Markdown"}
    try: requests.post(url, data=payload, timeout=10)
    except: pass

def get_headers():
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

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
    raise Exception("Failed to download audio file.")

def get_file_with_cooling(file_type, links_list, track_data):
    today = datetime.now().date()
    cooling_dict = track_data.setdefault(f"cooling_{file_type}", {})
    
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
    if not available_links: return None, track_data
        
    selected_link = random.choice(available_links)
    track_data[f"cooling_{file_type}"][selected_link] = today.strftime("%Y-%m-%d")
    return selected_link, track_data

def get_free_quote_only():
    try:
        res = requests.get("https://zenquotes.io/api/random", headers=get_headers(), timeout=10)
        return res.json()[0]['q']
    except: return "Your only limit is your mind."

def update_github_file(repo, path, content, message):
    try:
        file = repo.get_contents(path)
        repo.update_file(path, message, content, file.sha)
    except:
        repo.create_file(path, message, content)

def create_video_with_pillow(quote_text, bg_path, audio_path, output_filename):
    print("[DEBUG] Generating frame with Pillow (No ImageMagick needed)...")
    
    # 1. Download Font
    font_path = "font.ttf"
    if not os.path.exists(font_path):
        r = requests.get("https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Bold.ttf")
        with open(font_path, "wb") as f: f.write(r.content)

    # 2. Process Image (Crop 9:16 and Darken)
    img = Image.open(bg_path).convert("RGB")
    target_w, target_h = 1080, 1920
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h
    
    if img_ratio > target_ratio:
        new_w = int(img.height * target_ratio)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:
        new_h = int(img.width / target_ratio)
        top = (img.height - new_h) // 2
        img = img.crop((0, top, img.width, top + new_h))
        
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.5)

    # 3. Draw Text
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 75)
    
    wrapped_quote = textwrap.fill(f'"{quote_text}"', width=22)
    full_text = f"{wrapped_quote}\n\n{FIXED_AUTHOR}"
    
    bbox = draw.multiline_textbbox((0, 0), full_text, font=font, align="center")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (target_w - text_w) / 2
    y = (target_h - text_h) / 2
    
    draw.multiline_text((x, y), full_text, font=font, fill="white", align="center")
    
    # Save processed frame
    final_frame_path = "processed_bg.jpg"
    img.save(final_frame_path)

    # 4. Generate Video using MoviePy (Image + Audio)
    print(f"[DEBUG] Compiling Video {output_filename}...")
    clip = ImageClip(final_frame_path).set_duration(DURATION)
    
    if audio_path:
        try:
            audio = AudioFileClip(audio_path).subclip(0, min(DURATION, AudioFileClip(audio_path).duration))
            clip = clip.set_audio(audio)
        except Exception as e: print(f"Audio Edit Error: {e}")
            
    clip.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    
    # Clean temp images
    os.remove(final_frame_path)
    if os.path.exists(font_path): os.remove(font_path)

def main():
    try:
        if not GH_TOKEN: raise Exception("GH_TOKEN is not set.")
        g = Github(GH_TOKEN)
        
        track_repo = g.get_repo(TRACKING_REPO_NAME)
        target_repo = g.get_repo(TARGET_REPO_NAME)
        
        # Load Track
        try:
            track_file = track_repo.get_contents(TRACK_FILE_PATH)
            track_data = json.loads(track_file.decoded_content.decode('utf-8'))
        except:
            track_data = {"current_video": 1, "cooling_images": {}, "cooling_audios": {}}

        current_video_num = track_data.get("current_video", 1)
        if current_video_num > 90: current_video_num = 1
        video_filename = f"shorts.{current_video_num}.mp4"
        
        with open("images.txt", "r") as f: image_links = f.readlines()
        with open("bg_link.txt", "r") as f: audio_links = f.readlines()

        bg_link, track_data = get_file_with_cooling("images", image_links, track_data)
        if not bg_link: raise Exception("Images list khali hai ya sabhi images abhi 60 din ke cooling me hain!")
        bg_path = download_image_file(bg_link, "temp_bg.jpg")

        audio_link, track_data = get_file_with_cooling("audios", audio_links, track_data)
        audio_path = download_audio_file(audio_link, "temp_audio.mp3") if audio_link else None

        quote_text = get_free_quote_only()

        # CREATE VIDEO (PILLOW METHOD)
        create_video_with_pillow(quote_text, bg_path, audio_path, video_filename)

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
            
        # Track Update
        track_data["current_video"] = current_video_num + 1
        track_data["last_generated_video"] = video_filename
        track_data["last_used_image"] = bg_link
        if audio_link: track_data["last_used_audio"] = audio_link
            
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
