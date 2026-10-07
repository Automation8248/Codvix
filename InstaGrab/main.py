import os
import re
import random
import asyncio
import requests
import json
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

API_KEY = os.environ.get("ELITE_CLOUD_API_KEY")
UPLOAD_URL = "https://shreecloud.up.railway.app/api/v1/upload"

# 50+ Hardcoded Diverse User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A505F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; M2101K6G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0",
    "Mozilla/5.0 (Linux; Android 13; 2201117TG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/115.0.5790.130 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; V2049) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (Linux; Android 10; JNY-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0",
    "Mozilla/5.0 (Linux; Android 11; vivo 1904) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; rv:115.0) Gecko/20100101 Firefox/115.0"
]

TRACK_FILE = "track.json"

def load_tracked_links():
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_tracked_link(link):
    tracked = load_tracked_links()
    if link not in tracked:
        tracked.append(link)
        with open(TRACK_FILE, "w") as f:
            json.dump(tracked, f, indent=4)

# Yahan 6 to 10 seconds ka strict delay fix kiya gaya hai
async def human_delay():
    delay = random.uniform(6.0, 10.0)
    await asyncio.sleep(delay)

def get_username(url):
    match = re.search(r'instagram\.com/([^/]+)/', url)
    return match.group(1) if match else "unknown_user"

# Upload to ShreeCloud synchronously (runs in a separate thread so video recording doesn't freeze)
def upload_to_shreecloud_sync(file_path, username):
    if not API_KEY:
        return False, "API Key Missing"
    headers = {"X-API-Key": API_KEY}
    files = {'file': (os.path.basename(file_path), open(file_path, 'rb'), 'video/mp4')}
    data = {'folder': username}
    try:
        response = requests.post(UPLOAD_URL, headers=headers, files=files, data=data)
        if response.status_code == 200:
            return True, "Success"
        return False, f"Failed: {response.status_code}"
    except Exception as e:
        return False, str(e)

async def process_link(context, link, index):
    page = await context.new_page()
    await stealth_async(page)
    username = get_username(link)
    
    try:
        print(f"Tab {index + 1} processing link for {username}...")
        
        # Action 1: Goto Website
        await page.goto("https://igcomment.com/instagram-reel-downloader/", timeout=60000)
        await human_delay() # Delay 1
        
        # Action 2: Fake Scrolling
        await page.mouse.wheel(0, random.randint(300, 700))
        await human_delay() # Delay 2
        
        # Action 3: Random Mouse Movement
        await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
        await human_delay() # Delay 3
        
        # Action 4: Scrolling back up
        await page.mouse.wheel(0, -random.randint(200, 500))
        await human_delay() # Delay 4

        input_selector = "input[name='url'], input[type='text'], input[placeholder*='Instagram']" 
        await page.wait_for_selector(input_selector)
        
        # Action 5: Hover over input
        await page.hover(input_selector)
        await human_delay() # Delay 5
        
        # Action 6: Click input
        await page.click(input_selector)
        await human_delay() # Delay 6
        
        # Action 7: Type link slowly
        await page.fill(input_selector, link)
        await human_delay() # Delay 7
        
        # Action 8: Move mouse to submit button
        submit_btn = "button[type='submit'], button:has-text('Download')"
        await page.hover(submit_btn)
        await human_delay() # Delay 8
        
        # Action 9: Click submit
        await page.click(submit_btn)
        await human_delay() # Delay 9
        
        # Action 10: Wait for processing
        await human_delay() # Delay 10

        download_btn = "a[download], a:has-text('Download Video')"
        await page.wait_for_selector(download_btn, timeout=30000)
        
        # Action 11: Hover over Download button
        await page.hover(download_btn)
        await human_delay() # Delay 11
        
        # Action 12: Click Download and catch event
        async with page.expect_download() as download_info:
            await page.click(download_btn)
        
        await human_delay() # Delay 12
        download = await download_info.value
        
        os.makedirs(f"downloads/{username}", exist_ok=True)
        file_path = f"downloads/{username}/video_{random.randint(1000,9999)}.mp4"
        
        await download.save_as(file_path)
        
        # Action 13: Delay after save
        await human_delay() # Delay 13
        
        # ============================================================
        # VISUAL RECORDING OF UPLOAD PROCESS (Injecting UI on webpage)
        # ============================================================
        ui_script_start = """
        () => {
            let el = document.createElement('div');
            el.id = 'upload-status-overlay';
            el.style.cssText = 'position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); z-index:999999; background:rgba(0,0,0,0.9); color:white; padding:40px; border-radius:15px; font-size:30px; text-align:center; box-shadow: 0 0 20px rgba(255,255,255,0.5); font-family:sans-serif; width: 80%;';
            el.innerHTML = '⏳ <b>System Status:</b> Uploading to ShreeCloud<br><span style="font-size:20px; color:yellow; margin-top:10px; display:block;">Please wait... Uploading in backend.</span>';
            document.body.appendChild(el);
        }
        """
        await page.evaluate(ui_script_start)
        await human_delay() # Delay 14 (Lets the recording clearly show the "Uploading" message)
        
        # Run upload in background thread so Playwright event loop keeps recording frames
        success, msg = await asyncio.to_thread(upload_to_shreecloud_sync, file_path, username)
        
        # Action 15: Post Upload Delay
        await human_delay() # Delay 15
        
        # Update UI with Success/Failure Result
        if success:
            ui_script_end = """() => { document.getElementById('upload-status-overlay').innerHTML = '✅ <b>System Status:</b> Upload Successful!<br><span style="font-size:20px; color:lime; margin-top:10px; display:block;">Video saved to folder: %s</span>'; }""" % username
        else:
            ui_script_end = """() => { document.getElementById('upload-status-overlay').innerHTML = '❌ <b>System Status:</b> Upload Failed!<br><span style="font-size:20px; color:red; margin-top:10px; display:block;">Error: %s</span>'; }""" % msg
            
        await page.evaluate(ui_script_end)
        
        # Action 16: Let the success message stay on screen for the video
        await human_delay() # Delay 16
        
        # Action 17: Final scroll or movement before closing
        await page.mouse.wheel(0, 500)
        await human_delay() # Delay 17
        
        if success:
            save_tracked_link(link)

    except Exception as e:
        print(f"Error processing link {link}: {e}")
    finally:
        # Action 18: Delay before context closes
        await human_delay() # Delay 18
        await page.close()
        # Action 19: Final pause
        await human_delay() # Delay 19

async def main():
    if not os.path.exists("link.txt"):
        print("link.txt not found!")
        return

    with open("link.txt", "r") as f:
        all_links = [line.strip() for line in f if line.strip()]

    tracked_links = load_tracked_links()
    links = [link for link in all_links if link not in tracked_links]
    
    if not links:
        print("No new links to process. All links in link.txt are already downloaded.")
        return

    batch_size = 20
    is_manual_run = os.environ.get("IS_MANUAL_RUN") == "true"
    record_dir = "recordings/" if is_manual_run else None

    if is_manual_run:
        print("Manual Trigger detected. Screen recording is ON.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for i in range(0, len(links), batch_size):
            batch_links = links[i:i+batch_size]
            contexts = []
            
            for _ in range(len(batch_links)):
                context = await browser.new_context(
                    user_agent=random.choice(USER_AGENTS), 
                    viewport={"width": random.randint(1280, 1920), "height": random.randint(720, 1080)},
                    record_video_dir=record_dir
                )
                contexts.append(context)

            for index, link in enumerate(batch_links):
                # Action 20: Pre-tab delay
                await human_delay() # Delay 20
                await process_link(contexts[index], link, index)
            
            for context in contexts:
                await context.close()
            
            print(f"Batch {i//batch_size + 1} Completed.")
            await human_delay() # Batch completion delay
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
