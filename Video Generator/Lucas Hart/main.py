import requests, os, random, json, time, base64
import PIL.Image

# PIL Fix for moviepy compatibility
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import ImageClip, TextClip, AudioFileClip, CompositeVideoClip

# --- ENVIRONMENT VARIABLES ---
BOT_TOKEN = os.environ.get('AUTOMATION_STORAGE_TOKEN') or os.environ.get('TELEGRAM_BOT_TOKEN')
GITHUB_TOKEN = os.environ.get('UNIVERSAL_TOKEN')
REPO_NAME = "Automation8248/Postza"

# Fixed Settings
FIXED_AUTHOR = "Lucas Hart"
DURATION = 5

# --- LOCAL PATHS ---
IMAGE_DIR = "images"
TRACK_FILE = "track.json"

# --- COOLING & RESET LOGIC ---
COOLING_DAYS = 6  # Image aur Music dono ke liye 6 din ka cooling
COOLING_SECONDS = COOLING_DAYS * 24 * 60 * 60
RENAME_CYCLE_DAYS = 90
RENAME_CYCLE_SECONDS = RENAME_CYCLE_DAYS * 24 * 60 * 60

# --- USER AGENTS ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

# --- TRACKING LOGIC (track.json) ---
def load_track():
    if os.path.exists(TRACK_FILE):
        try:
            with open(TRACK_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {
        "images": {}, 
        "audio_cooling": {}, 
        "telegram_file_ids": [],
        "video_counter": {"current_index": 1, "cycle_start": time.time()}
    }

def save_track(track_data):
    with open(TRACK_FILE, 'w') as f:
        json.dump(track_data, f, indent=4)

def get_next_video_filename(track_data):
    current_time = time.time()
    counter_data = track_data.get("video_counter", {"current_index": 1, "cycle_start": current_time})

    # 90 days reset logic
    if current_time - counter_data["cycle_start"] >= RENAME_CYCLE_SECONDS:
        print("🔄 90 Days completed! Resetting video counter to 1.")
        counter_data["cycle_start"] = current_time
        counter_data["current_index"] = 1

    index = counter_data["current_index"]
    counter_data["current_index"] = index + 1
    track_data["video_counter"] = counter_data
    
    return f"lucas.{index}.mp4"

# --- COOLING FILE PICKERS ---
def get_image_with_cooling(track_data):
    if not os.path.exists(IMAGE_DIR): 
        os.makedirs(IMAGE_DIR, exist_ok=True)
        return None
        
    all_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not all_files: return None

    current_time = time.time()
    available_files = []
    
    for f in all_files:
        last_used_time = track_data["images"].get(f, 0)
        if current_time - last_used_time >= COOLING_SECONDS:
            available_files.append(f)

    if available_files:
        selected_file = random.choice(available_files)
        track_data["images"][selected_file] = current_time
        print(f"✅ Selected Image: {selected_file} (Locked for {COOLING_DAYS} days)")
        return os.path.join(IMAGE_DIR, selected_file)
    
    return None

def get_audio_from_telegram_with_cooling(track_data):
    if not BOT_TOKEN:
        print("⚠️ Bot Token nahi hai, Telegram se audio nahi aayega.")
        return None
        
    telegram_files = track_data.get("telegram_file_ids", [])
    if not telegram_files:
        print("⚠️ track.json me koi telegram_file_ids nahi mile.")
        return None

    current_time = time.time()
    available_audios = []

    for item in telegram_files:
        file_id = item.get("file_id")
        last_used = track_data["audio_cooling"].get(file_id, 0)
        if current_time - last_used >= COOLING_SECONDS:
            available_audios.append(item)

    if not available_audios:
        print(f"⚠️ Warning: Saare Telegram Audios {COOLING_DAYS} din ke cooling me hain!")
        return None

    selected = random.choice(available_audios)
    file_id = selected["file_id"]
    print(f"✅ Selected Telegram Audio: {selected.get('filename', 'Unknown')} (Locked for {COOLING_DAYS} days)")

    try:
        res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}").json()
        if not res.get("ok"): return None
            
        file_path = res["result"]["file_path"]
        dl_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        
        audio_data = requests.get(dl_url).content
        local_audio_path = "temp_bg_music.mp3"
        
        with open(local_audio_path, "wb") as f:
            f.write(audio_data)

        track_data["audio_cooling"][file_id] = current_time
        return local_audio_path
        
    except Exception as e:
        print(f"❌ Audio Download Error: {e}")
        return None

# --- GITHUB UPLOAD LOGIC (API) ---
def push_to_github(local_file, repo_path, commit_message):
    print(f"🚀 Uploading {repo_path} to GitHub...")
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{repo_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Base64 encode the file content
    with open(local_file, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    # Check if file exists to get SHA (for updates)
    get_res = requests.get(url, headers=headers)
    sha = get_res.json().get("sha") if get_res.status_code == 200 else None

    data = {"message": commit_message, "content": content, "branch": "main"}
    if sha: data["sha"] = sha

    put_res = requests.put(url, headers=headers, json=data)
    if put_res.status_code in [200, 201]:
        print(f"✅ Successfully pushed to GitHub: {repo_path}")
        return True
    else:
        print(f"❌ GitHub Upload Failed: {put_res.json()}")
        return False

def append_caption_to_github(new_caption):
    repo_path = "Lucas Hart/caption.txt"
    print("📝 Saving caption to GitHub...")
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{repo_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    get_res = requests.get(url, headers=headers)
    sha = None
    existing_text = ""
    
    if get_res.status_code == 200:
        sha = get_res.json().get("sha")
        existing_text = base64.b64decode(get_res.json().get("content", "")).decode("utf-8")

    # Naya caption purane text ke niche add karna
    final_text = existing_text + f"\n\n{'-'*30}\n" + new_caption if existing_text else new_caption
    encoded_text = base64.b64encode(final_text.encode("utf-8")).decode("utf-8")

    data = {"message": "Add new caption for video", "content": encoded_text, "branch": "main"}
    if sha: data["sha"] = sha

    requests.put(url, headers=headers, json=data)
    print("✅ Caption updated on GitHub.")


# --- VIDEO CREATION LOGIC ---
def get_free_quote():
    try:
        res = requests.get("https://zenquotes.io/api/random", headers=get_headers(), timeout=10)
        return res.json()[0]['q']
    except: return "Your only limit is your mind."

def create_video(quote_text, track_data, output_path):
    bg_path = get_image_with_cooling(track_data)
    if not bg_path: 
        raise Exception("Images folder khali hai ya sabhi images abhi 6 din ke cooling me hain!")

    bg = ImageClip(bg_path).set_duration(DURATION).resize(height=1920).fl_image(lambda image: (image * 0.6).astype('uint8'))
    
    full_display_text = f"\"{quote_text}\"\n\n- {FIXED_AUTHOR}"
    txt = TextClip(full_display_text, fontsize=80, color='white', font='Arial-Bold', 
                   method='caption', size=(850, None)).set_duration(DURATION).set_position('center')
    
    audio_path = get_audio_from_telegram_with_cooling(track_data)
    audio = None
    if audio_path:
        try: audio = AudioFileClip(audio_path).subclip(0, DURATION)
        except Exception as e: print(f"Audio Error: {e}")
    
    final = CompositeVideoClip([bg, txt])
    if audio: final = final.set_audio(audio)
    
    final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    
    # Clips close (Taki background memory free ho jaye)
    bg.close()
    txt.close()
    final.close()
    if audio: audio.close()
    
    if audio_path and os.path.exists(audio_path):
        os.remove(audio_path) # Temp audio delete karna runner space bachane ke liye
        
    return output_path


# --- MAIN PIPELINE ---
try:
    if not GITHUB_TOKEN:
        raise Exception("UNIVERSAL_TOKEN set nahi hai! Action Secrets check karein.")

    track = load_track()
    
    print("Step 1: Fetching Quote...")
    quote = get_free_quote()
    
    print("Step 2: Creating Video & Setting up Cooling...")
    video_filename = get_next_video_filename(track)
    local_video_path = f"temp_{video_filename}"
    
    create_video(quote, track, local_video_path)
    save_track(track) # Save cooling details and counters to track.json
    
    print("Step 3: Pushing Video to GitHub...")
    github_video_path = f"Lucas Hart/video/{video_filename}"
    push_success = push_to_github(local_video_path, github_video_path, f"Upload video {video_filename}")

    if push_success:
        clean_title = f"Motivational Quote by {FIXED_AUTHOR}".replace('*', '')
        caption = f"🎬 {clean_title}\n\n✨ {quote}\n\n#viral #trending #foryou #viralvideo #explore #shorts"
        
        print("Step 4: Pushing Caption to GitHub...")
        append_caption_to_github(caption)
        
        # Space cleanup for local video
        if os.path.exists(local_video_path):
            os.remove(local_video_path)
            print("🗑️ Local temp video deleted to save Action runner space.")
            
        print("🎉 Full Workflow Successfully Completed!")
    else:
        print("❌ Video upload fail hone ki wajah se process stop kar di gayi.")

except Exception as e:
    print(f"❌ Fatal Error: {e}")
