import os
import random
from playwright.sync_api import sync_playwright, TimeoutError

def run(playwright):
    # 1. Folders banayen download aur video ke liye
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("videos", exist_ok=True)

    # 2. Headless browser aur screen recording set karein
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        record_video_dir="videos/",
        record_video_size={"width": 1280, "height": 720},
        accept_downloads=True,
        viewport={"width": 1280, "height": 720}
    )
    page = context.new_page()

    # 3. Download pakadne ka logic
    def handle_download(download):
        file_path = os.path.join("downloads", download.suggested_filename)
        print(f"File save ho rahi hai: {file_path}")
        download.save_as(file_path)

    page.on("download", handle_download)
    print("Browser start ho gaya. Screen recording chal rahi hai...")
    
    # Try block lagaya hai taaki error aane par bhi video save ho
    try:
        url = "https://drive.google.com/drive/folders/1pnRfQod0LWTG1Lc5PgYDoESsMXtIYtxX"
        page.goto(url)
        
        print("Page load ho raha hai, Google Drive UI render hone ka wait kar rahe hain (40 sec timeout)...")
        # GitHub action thoda slow hota hai, thoda raw wait denge
        page.wait_for_timeout(8000) 
        
        # Selector broad kiya hai aur timeout 40 seconds kiya hai
        page.wait_for_selector('div[data-id], div[role="gridcell"], div[role="row"]', timeout=40000)
        page.wait_for_timeout(3000) # Animations rukne ka wait
        
        # Un elements ko target karenge jinke pass data-id aur aria-label dono hai (ye Drive ki files hoti hain)
        files = page.locator('div[data-id][aria-label]').all()
        
        if not files:
            # Agar primary locator kaam na kare, toh fallback search chalayega
            print("Fallback selector use kar raha hai...")
            files = page.locator('div[data-id], div[role="gridcell"]').all()

        if not files:
            print("Koi files nahi mili. Script end ho rahi hai, video check karein.")
            return
            
        print(f"Total {len(files)} files/folders mile.")
        
        # 4. Randomly file select karke double-click karna
        random_file = random.choice(files)
        print("Random file select kar li gayi hai, ab double-click kar raha hai...")
        
        random_file.scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        random_file.dblclick()
        
        # 5. Image preview open hone ka wait
        print("Image preview open hone ka wait kar raha hai...")
        page.wait_for_timeout(6000) 
        
        # 6. Download button click
        print("Preview open ho gaya, ab file download kar raha hai...")
        try:
            with page.expect_download(timeout=30000) as download_info:
                # Top right corner ka download button
                download_btn = page.locator('[aria-label="Download"]').first
                if download_btn.is_visible():
                    download_btn.click()
                else:
                    # Backup mein keyboard shortcut
                    page.keyboard.press("Shift+D")
                    
            print("Download successfully complete aur save ho gaya!")
        except Exception as e:
            print(f"Download trigger karne me error aaya: {e}")

        # Thoda rukenge taaki aakhiri UI frame video me record ho jaye
        page.wait_for_timeout(4000)

    except TimeoutError:
        print("TimeoutError: Drive link load hone mein zyada time le raha hai.")
    except Exception as e:
        print(f"Unexpected Error aaya: {e}")
    finally:
        # Finally block hamesha run hota hai, chahe error aaye ya na aaye.
        # Isse aapki screen recording hamesha save hogi.
        print("Browser close kar raha hai taaki video file safely save ho jaye...")
        context.close()
        browser.close()
        print("Automation pura hua. Zip ready ho rahi hai.")

with sync_playwright() as playwright:
    run(playwright)
