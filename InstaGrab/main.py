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

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.0.0",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"
    # Baaki User-Agents (aapne jo upar copy kiye the, wo yahan same rahenge, maine size chota rakhne ke liye yahan example diye hain)
]

TRACK_FILE = "track.json"

def init_track_file():
    if not os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, "w") as f:
            json.dump([], f)

def load_tracked_links():
    try:
        with open(TRACK_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_tracked_link(link):
    tracked = load_tracked_links()
    if link not in tracked:
        tracked.append(link)
        with open(TRACK_FILE, "w") as f:
            json.dump(tracked, f, indent=4)

async def human_delay():
    delay = random.uniform(6.0, 10.0)
    await asyncio.sleep(delay)

# Specific 6.8 to 7+ seconds delay function as requested
async def specific_wait_delay():
    delay = random.uniform(6.8, 7.5)
    print(f"Waiting for {delay:.2f} seconds before checking for video...")
    await asyncio.sleep(delay)

def get_username(url):
    match = re.search(r'instagram\.com/([^/]+)/', url)
    return match.group(1) if match else "unknown_user"

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

async def process_link(context, link):
    page = await context.new_page()
    await stealth_async(page)
    username = get_username(link)
    
    try:
        print(f"Processing single link for username: {username}")
        
        # New Website URL
        await page.goto("https://videodropper.app/", timeout=60000)
        await human_delay() 
        
        await page.mouse.wheel(0, random.randint(300, 700))
        await human_delay()
        
        await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
        await human_delay() 
        
        await page.mouse.wheel(0, -random.randint(200, 500))
        await human_delay() 

        # Broad selector for "Paste Instagram link here" input box
        input_selector = "input[placeholder*='aste'], input[name='url'], input[type='text'], input[type='url']" 
        await page.wait_for_selector(input_selector)
        
        await page.hover(input_selector)
        await human_delay() 
        
        await page.click(input_selector)
        await human_delay()
        
        # URL Paste karna
        print("Pasting URL...")
        await page.fill(input_selector, link)
        
        # Submit/Download fetch button dhund kar click karna
        fetch_btn = "button[type='submit'], button:has-text('Download')"
        await page.hover(fetch_btn)
        await human_delay() 
        await page.click(fetch_btn)
        
        # === Aapki request ke mutabiq 6.8 se 7 second ka specific delay ===
        await specific_wait_delay() 

        # Video aane ke baad Final Download button dhundna
        download_btn = "a[download], a:has-text('Download Video'), a.button, button:has-text('Download')"
        await page.wait_for_selector(download_btn, timeout=45000)
        
        await page.hover(download_btn)
        await human_delay()
        
        print("Video visible! Starting download...")
        async with page.expect_download() as download_info:
            await page.click(download_btn)
        
        await human_delay()
        download = await download_info.value
        
        os.makedirs(f"downloads/{username}", exist_ok=True)
        file_path = f"downloads/{username}/video_{random.randint(1000,9999)}.mp4"
        
        await download.save_as(file_path)
        await human_delay()
        
        # VISUAL RECORDING OF UPLOAD PROCESS
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
        await human_delay() 
        
        success, msg = await asyncio.to_thread(upload_to_shreecloud_sync, file_path, username)
        
        await human_delay() 
        
        if success:
            ui_script_end = """() => { document.getElementById('upload-status-overlay').innerHTML = '✅ <b>System Status:</b> Upload Successful!<br><span style="font-size:20px; color:lime; margin-top:10px; display:block;">Video saved to folder: %s</span>'; }""" % username
        else:
            ui_script_end = """() => { document.getElementById('upload-status-overlay').innerHTML = '❌ <b>System Status:</b> Upload Failed!<br><span style="font-size:20px; color:red; margin-top:10px; display:block;">Error: %s</span>'; }""" % msg
            
        await page.evaluate(ui_script_end)
        await human_delay() 
        await page.mouse.wheel(0, 500)
        await human_delay() 
        
        if success:
            save_tracked_link(link)

    except Exception as e:
        print(f"Error processing link {link}: {e}")
    finally:
        await human_delay()
        await page.close()
        await human_delay()

async def main():
    # Make sure track.json exists at start so git doesn't crash later
    init_track_file()

    if not os.path.exists("link.txt"):
        print("link.txt not found!")
        return

    with open("link.txt", "r") as f:
        all_links = [line.strip() for line in f if line.strip()]

    tracked_links = load_tracked_links()
    links = [link for link in all_links if link not in tracked_links]
    
    if not links:
        print("No new links to process.")
        return

    target_link = links[0]
    print(f"Target link selected for this run: {target_link}")

    is_manual_run = os.environ.get("IS_MANUAL_RUN") == "true"
    record_dir = "recordings/" if is_manual_run else None

    if is_manual_run:
        print("Manual Trigger detected. Screen recording is ON.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        random_agent = random.choice(USER_AGENTS)
        print(f"Randomly selected User-Agent: {random_agent}")

        context = await browser.new_context(
            user_agent=random_agent, 
            viewport={"width": random.randint(1280, 1920), "height": random.randint(720, 1080)},
            record_video_dir=record_dir
        )

        await human_delay()
        await process_link(context, target_link)
        
        await context.close()
        await browser.close()
        print("Run Complete.")

if __name__ == "__main__":
    asyncio.run(main())
