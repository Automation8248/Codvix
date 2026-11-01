import os
import random
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

os.makedirs("recordings", exist_ok=True)

def run_automation():
    with sync_playwright() as p:
        # Extra anti-detect browser arguments
        browser = p.chromium.launch(
            headless=False, 
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-sandbox",
                "--window-size=1280,720"
            ]
        )
        
        # Realistic context setup
        context = browser.new_context(
            record_video_dir="recordings/",
            record_video_size={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="en-US",
            timezone_id="Asia/Kolkata"
        )
        page = context.new_page()

        # Stealth plugin apply karna (Yeh sabse important hai anti-bot bypass ke liye)
        stealth_sync(page)

        total_pages = 5
        
        for page_num in range(1, total_pages + 1):
            url = f"https://pixabay.com/music/search/soft/?pagi={page_num}"
            print(f"Loading Page {page_num}: {url}")
            page.goto(url)
            
            # Page load hone ke baad 3 seconds ka wait
            page.wait_for_timeout(3000)
            
            # Human-like jitter scrolling logic (Natural scroll behavior mimic karne ke liye)
            for _ in range(3):
                page.mouse.wheel(0, random.randint(200, 600))
                page.wait_for_timeout(random.randint(500, 1500))
            
            # Audio src aur download links extract karna
            elements = page.locator("a, audio source").all()
            
            with open("music_links.txt", "a", encoding="utf-8") as f:
                for el in elements:
                    link = el.get_attribute("href") or el.get_attribute("src")
                    
                    if link and ("/download/" in link or link.endswith(".mp3")):
                        full_link = link if link.startswith("http") else f"https://pixabay.com{link}"
                        f.write(full_link + "\n")
                        print(f"Copied: {full_link}")

        # Browser close karne par stealth mode ke sath recording save ho jayegi
        context.close()
        browser.close()
        print("Automation complete. Links and video saved stealthily.")

if __name__ == "__main__":
    run_automation()
