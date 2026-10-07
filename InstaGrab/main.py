import os
import re
import random
import asyncio
import requests
import json
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

# Secure API Key fetching from environment (GitHub Secrets)
API_KEY = os.environ.get("ELITE_CLOUD_API_KEY")
UPLOAD_URL = "https://shreecloud.up.railway.app/api/v1/upload"

# 50+ Hardcoded Diverse User-Agents (Windows, Mac, Linux, Android, iOS)
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

async def human_delay(min_sec, max_sec):
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)

def get_username(url):
    match = re.search(r'instagram\.com/([^/]+)/', url)
    return match.group(1) if match else "unknown_user"

def upload_to_shreecloud(file_path, username):
    if not API_KEY:
        print("Error: ELITE_CLOUD_API_KEY environment variable is not set!")
        return False
        
    print(f"[{username}] Uploading to ShreeCloud...")
    headers = {"X-API-Key": API_KEY}
    files = {'file': (os.path.basename(file_path), open(file_path, 'rb'), 'video/mp4')}
    data = {'folder': username}
    
    try:
        response = requests.post(UPLOAD_URL, headers=headers, files=files, data=data)
        if response.status_code == 200:
            print(f"[{username}] Upload Success!")
            return True
        else:
            print(f"[{username}] Upload Failed. Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[{username}] Upload Error: {e}")
        return False

async def process_link(context, link, index):
    page = await context.new_page()
    await stealth_async(page)
    username = get_username(link)
    
    try:
        print(f"Tab {index + 1} processing link for {username}...")
        
        await page.goto("https://igcomment.com/instagram-reel-downloader/", timeout=60000)
        await human_delay(3.0, 5.0)
        
        await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
        await human_delay(0.5, 1.5)

        input_selector = "input[name='url'], input[type='text'], input[placeholder*='Instagram']" 
        await page.wait_for_selector(input_selector)
        await page.click(input_selector)
        await human_delay(1.0, 2.0)
        
        await page.fill(input_selector, link)
        await human_delay(2.0, 4.0)
        
        submit_btn = "button[type='submit'], button:has-text('Download')"
        await page.click(submit_btn)
        
        await human_delay(3.0, 4.0)

        download_btn = "a[download], a:has-text('Download Video')"
        await page.wait_for_selector(download_btn, timeout=30000)
        
        async with page.expect_download() as download_info:
            await page.click(download_btn)
            
        download = await download_info.value
        
        os.makedirs(f"downloads/{username}", exist_ok=True)
        file_path = f"downloads/{username}/video_{random.randint(1000,9999)}.mp4"
        
        await download.save_as(file_path)
        await human_delay(1.5, 3.5)
        
        upload_success = upload_to_shreecloud(file_path, username)
        
        # Track file updated only on successful upload
        if upload_success:
            save_tracked_link(link)

    except Exception as e:
        print(f"Error processing link {link}: {e}")
    finally:
        await page.close()
        await human_delay(1.0, 3.0)

async def main():
    if not os.path.exists("link.txt"):
        print("link.txt not found!")
        return

    with open("link.txt", "r") as f:
        all_links = [line.strip() for line in f if line.strip()]

    # Filter out already tracked (downloaded) links
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
                    user_agent=random.choice(USER_AGENTS), # 50+ Hardcoded List me se ek pick karega
                    viewport={"width": random.randint(1280, 1920), "height": random.randint(720, 1080)},
                    record_video_dir=record_dir
                )
                contexts.append(context)

            for index, link in enumerate(batch_links):
                await human_delay(2.0, 5.0) 
                await process_link(contexts[index], link, index)
            
            for context in contexts:
                await context.close()
            
            print(f"Batch {i//batch_size + 1} Completed.")
            await human_delay(10.0, 20.0)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
