import time
import subprocess
import signal
from seleniumbase import SB

def scrape_welib():
    # Xvfb me browser open hoga
    with SB(uc=True, test=True, headless=False) as sb:
        url = "https://welib.st"
        
        print(f"Opening {url} and bypassing Cloudflare via CDP...")
        sb.activate_cdp_mode(url)
        
        # Cloudflare bypass hone ke liye 8 seconds ka wait
        print("Waiting 8 seconds for Cloudflare bypass to complete...")
        sb.sleep(8) 
        
        # ==========================================
        # 🎥 RECORDING START (Bypass hone ke baad)
        # ==========================================
        print("Bypass Complete! Starting WEBM Screen Recording now...")
        
        # FFmpeg command ko Python list me set kiya
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-video_size", "1920x1080", "-framerate", "30",
            "-f", "x11grab", "-i", ":99.0", "-c:v", "libvpx-vp9",
            "-crf", "30", "-b:v", "0", "-deadline", "realtime", "recording.webm"
        ]
        
        # Background me FFmpeg run karna shuru kar diya
        ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        sb.sleep(2) # Recording properly start hone ke liye 2 sec de do
        
        # Yahan aap apna Scraping ka main kaam kar sakte hain
        page_title = sb.get_page_title()
        print(f"Success! Page Title: {page_title}")
        
        # Kuch der website par ruko taaki video me kuch dikhe
        sb.sleep(5) 
        
        # Screenshot le lo
        sb.save_screenshot("screenshot.png")
        print("Screenshot saved.")
        
        # ==========================================
        # 🛑 RECORDING STOP
        # ==========================================
        print("Scraping done. Stopping screen recording...")
        ffmpeg_process.send_signal(signal.SIGINT) # FFmpeg ko safely stop command bhejna
        ffmpeg_process.wait(timeout=10) # Video mp4/webm pack hone tak thoda wait karna

if __name__ == "__main__":
    scrape_welib()
