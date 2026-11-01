import os
from playwright.sync_api import sync_playwright

# Folder for screen recordings
os.makedirs("recordings", exist_ok=True)

def run_automation():
    with sync_playwright() as p:
        # Anti-detect browser setup arguments
        browser = p.chromium.launch(
            headless=False, 
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # Context setup with screen recording and custom user agent
        context = browser.new_context(
            record_video_dir="recordings/",
            record_video_size={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        total_pages = 5 # Aap isko apne hisab se badha sakte hain
        
        for page_num in range(1, total_pages + 1):
            url = f"https://pixabay.com/music/search/soft/?pagi={page_num}"
            print(f"Loading: {url}")
            page.goto(url)
            
            # Page load hone ke baad 3 seconds wait karega
            page.wait_for_timeout(3000)
            
            # Audio src aur download links target karna
            elements = page.locator("a, audio source").all()
            
            with open("music_links.txt", "a", encoding="utf-8") as f:
                for el in elements:
                    link = el.get_attribute("href") or el.get_attribute("src")
                    
                    if link and ("/download/" in link or link.endswith(".mp3")):
                        full_link = link if link.startswith("http") else f"https://pixabay.com{link}"
                        f.write(full_link + "\n")
                        print(f"Copied: {full_link}")

        # Browser close karne par screen recording automatically save ho jayegi
        context.close()
        browser.close()
        print("Automation complete. Links and video saved.")

if __name__ == "__main__":
    run_automation()
