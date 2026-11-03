import os
import random
from playwright.sync_api import sync_playwright

def run(playwright):
    # 1. Folders create karna jahan video aur downloaded files save hongi
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("videos", exist_ok=True)

    # 2. Fake (Headless) browser aur screen recording start karna
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        record_video_dir="videos/",
        record_video_size={"width": 1280, "height": 720},
        accept_downloads=True,
        viewport={"width": 1280, "height": 720}
    )
    page = context.new_page()

    # 3. Download handler: Jab file download hogi, toh use 'downloads' folder me save karega
    def handle_download(download):
        file_path = os.path.join("downloads", download.suggested_filename)
        print(f"File save ho rahi hai: {file_path}")
        download.save_as(file_path)

    page.on("download", handle_download)
    print("Browser start ho gaya. Screen recording aur script chalu hai...")
    
    # 4. Google Drive link par jana
    url = "https://drive.google.com/drive/folders/1pnRfQod0LWTG1Lc5PgYDoESsMXtIYtxX"
    page.goto(url)
    
    # Grid/Images puri tarah load hone ka wait karna
    page.wait_for_timeout(8000)

    # 5. Randomly kisi image ko select karna
    # Screen ke center me click karke Drive ke files area par focus lana
    page.mouse.click(640, 400)
    page.wait_for_timeout(1000)

    # Randomly 1 se 15 ke beech move karke kisi random image ko select karna
    random_moves = random.randint(1, 15)
    print(f"Randomly {random_moves} step aage badh kar file select kar raha hai...")
    
    for _ in range(random_moves):
        page.keyboard.press("ArrowRight")
        page.keyboard.press("ArrowDown") # Grid ya List view dono ke liye kaam karega
        page.wait_for_timeout(300)

    # 6. Selected random image ko download karna (Shift+D is Drive's download shortcut)
    print("Random image mil gayi, download trigger kar raha hai...")
    try:
        # Playwright ko batana ki download start hone wala hai
        with page.expect_download(timeout=30000) as download_info:
            page.keyboard.press("Shift+D")
        
        print("Download successfully 'downloads/' folder me aa gaya!")
    except Exception as e:
        print(f"Download me error aaya (shayad folder empty ho ya focus na hua ho): {e}")

    # Video me aakhiri actions save karne ke liye thoda rukna
    page.wait_for_timeout(4000)

    # Context close karte hi video automatically 'videos/' folder me save ho jayegi
    context.close()
    browser.close()
    print("Automation pura hua.")

with sync_playwright() as playwright:
    run(playwright)
