import os
import random
from playwright.sync_api import sync_playwright

def run(playwright):
    # Folders banayen download aur video ke liye
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("videos", exist_ok=True)

    # Headless browser aur screen recording set karein
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        record_video_dir="videos/",
        record_video_size={"width": 1280, "height": 720},
        accept_downloads=True,
        viewport={"width": 1280, "height": 720}
    )
    page = context.new_page()

    # Download pakadne ka function
    def handle_download(download):
        file_path = os.path.join("downloads", download.suggested_filename)
        print(f"File save ho rahi hai: {file_path}")
        download.save_as(file_path)

    page.on("download", handle_download)
    print("Browser start ho gaya. Screen recording chal rahi hai...")
    
    # Drive link par jayen
    url = "https://drive.google.com/drive/folders/1pnRfQod0LWTG1Lc5PgYDoESsMXtIYtxX"
    page.goto(url)
    
    # Drive ki files (Grid ya List view) load hone ka wait karein
    print("Page load ho raha hai, files render hone ka wait kar rahe hain...")
    page.wait_for_selector('div[role="gridcell"], div[role="row"]', timeout=15000)
    page.wait_for_timeout(3000) # Animations aur lazy-loading set hone ke liye thoda extra time
    
    # Page par jitni bhi files hain unki list nikalein
    files = page.locator('div[role="gridcell"], div[role="row"]').all()
    
    if not files:
        print("Koi files nahi mili. Link ya network check karein.")
        context.close()
        browser.close()
        return
        
    print(f"Total {len(files)} files/folders mile.")
    
    # 1. Randomly kisi ek file ko select karein
    random_file = random.choice(files)
    
    # 2. File ko screen par focus me laayein aur Double-Click karein
    print("Random file select kar li gayi hai, ab double-click kar raha hai...")
    random_file.scroll_into_view_if_needed()
    random_file.dblclick()
    
    # 3. Image preview open hone ka wait karein
    print("Image preview open hone ka wait kar raha hai...")
    page.wait_for_timeout(5000) 
    
    # 4. Preview overlay me se Download button dhoond kar click karein
    print("Preview open ho gaya, ab file download kar raha hai...")
    try:
        with page.expect_download(timeout=30000) as download_info:
            # Drive preview me download icon ka aria-label "Download" hota hai
            download_btn = page.locator('[aria-label="Download"]').first
            if download_btn.is_visible():
                download_btn.click()
            else:
                # Agar button nahi mila toh keyboard shortcut use karega
                page.keyboard.press("Shift+D")
                
        print("Download successfully complete aur save ho gaya!")
    except Exception as e:
        print(f"Download trigger karne me error aaya: {e}")

    # Aakhiri screen recording properly save hone ke liye wait karein
    page.wait_for_timeout(4000)

    # Close karte hi background video 'videos/' folder me save ho jayegi
    context.close()
    browser.close()
    print("Automation pura hua. Zip file ready ho rahi hai.")

with sync_playwright() as playwright:
    run(playwright)
