import os
import time
import random
import subprocess
from seleniumbase import SB

os.makedirs("recordings", exist_ok=True)

def run_automation():
    video_file = f"recordings/recording_{int(time.time())}.mp4"
    display = os.environ.get('DISPLAY', ':99') # Xvfb display on GitHub Actions
    
    # Start FFmpeg screen recording in the background (Linux/Xvfb format)
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-f", "x11grab", "-video_size", "1280x720", 
        "-i", display, "-codec:v", "libx264", "-r", "30", video_file
    ]
    
    try:
        # Start recording
        recorder = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Screen recording started...")
    except FileNotFoundError:
        print("FFmpeg not installed. Skipping recording.")
        recorder = None

    # Launch SeleniumBase in UC (Undetected) mode
    with SB(uc=True, window_size="1280,720", headless=False) as sb:
        total_pages = 30
        
        for page_num in range(1, total_pages + 1):
            url = f"https://pixabay.com/music/search/soft/?pagi={page_num}"
            print(f"Loading Page {page_num}: {url}")
            
            # uc_open_with_reconnect helps bypass strict Cloudflare/anti-bot checks
            sb.uc_open_with_reconnect(url, reconnect_time=3)
            
            # Wait exactly 3 seconds after load
            sb.sleep(3)
            
            # Human-like jitter scrolling
            for _ in range(3):
                scroll_amount = random.randint(200, 600)
                sb.execute_script(f"window.scrollBy(0, {scroll_amount});")
                sb.sleep(random.uniform(0.5, 1.5))
            
            # Fast parsing using BeautifulSoup via SeleniumBase
            soup = sb.get_beautiful_soup()
            
            with open("music_links.txt", "a", encoding="utf-8") as f:
                for el in soup.find_all(['a', 'source']):
                    link = el.get('href') or el.get('src')
                    if link and ("/download/" in link or link.endswith(".mp3")):
                        full_link = link if link.startswith("http") else f"https://pixabay.com{link}"
                        f.write(full_link + "\n")
                        print(f"Copied: {full_link}")

    # Gracefully stop FFmpeg recording
    if recorder:
        recorder.terminate()
        recorder.wait()
        print(f"Automation complete. Video saved to {video_file}.")

if __name__ == "__main__":
    run_automation()
