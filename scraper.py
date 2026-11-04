import os
from playwright.sync_api import sync_playwright

def run(playwright):
    # 1. Folders banayen
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("videos", exist_ok=True)

    # 2. Browser aur screen recording setup
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        record_video_dir="videos/",
        record_video_size={"width": 1280, "height": 720},
        viewport={"width": 1280, "height": 720},
        permissions=['clipboard-read', 'clipboard-write']
    )
    page = context.new_page()

    print("Browser start ho gaya. Screen recording chal rahi hai...")
    
    try:
        url = "https://drive.google.com/drive/folders/1pnRfQod0LWTG1Lc5PgYDoESsMXtIYtxX"
        page.goto(url)
        print("Drive link open ho raha hai, load hone ka wait kar rahe hain...")
        page.wait_for_timeout(8000) 
        
        # Files aane ka wait
        page.wait_for_selector('div[data-id], div[role="gridcell"]', timeout=40000)
        page.wait_for_timeout(3000)
        
        files = page.locator('div[data-id][aria-label]').all()
        if not files:
            files = page.locator('div[data-id], div[role="gridcell"]').all()

        if not files:
            print("Koi files nahi mili. Script check karein.")
            return
            
        print(f"Total {len(files)} files/folders mile.")
        
        # STEP 1: Pehli file ka exact (X, Y) position (box) nikalna
        box = files[0].bounding_box()
        if not box:
            print("File screen par visible nahi hai.")
            return
            
        x_center = box["x"] + box["width"] / 2
        y_center = box["y"] + box["height"] / 2

        # STEP 2: Manually Mouse hila kar Left Click karna (Focus ke liye)
        print("Mouse ko pehli file par le ja raha hai aur Left click kar raha hai...")
        page.mouse.move(x_center, y_center)
        page.mouse.click(x_center, y_center, button="left")
        page.wait_for_timeout(1500)
        
        # STEP 3: Manually Keyboard se Ctrl+A dabana (Select All)
        print("Keyboard se 'Ctrl+A' daba raha hai...")
        page.keyboard.press("Control+A")
        page.wait_for_timeout(2000)
        
        # STEP 4: Manually Mouse se usi location par Right Click karna
        print("Mouse se wahi par Right Click kar raha hai...")
        page.mouse.click(x_center, y_center, button="right")
        page.wait_for_timeout(2000) # Menu khulne ka wait
        
        # STEP 5: Menu me 'Copy link' par click karna
        print("Menu mein 'Copy link' dhundh kar click kar raha hai...")
        copy_link_btn = page.locator('div[role="menuitem"]:has-text("Copy link")').first
        share_btn = page.locator('div[role="menuitem"]:has-text("Share")').first
        
        if copy_link_btn.is_visible():
            copy_link_btn.click()
        elif share_btn.is_visible():
            share_btn.hover()
            page.wait_for_timeout(1000)
            sub_copy = page.locator('div[role="menuitem"]:has-text("Copy link")').first
            if sub_copy.is_visible():
                sub_copy.click()
            else:
                share_btn.click()
        else:
            print("Menu nahi mila, backup Ctrl+C daba raha hai...")
            page.keyboard.press("Control+C")
            
        print("Link copy hone ka wait kar raha hai...")
        page.wait_for_timeout(4000) 
        
        # STEP 6: Clipboard se text manually 'Ctrl+V' karke nikalna
        print("Screen par invisible text box banakar 'Ctrl+V' daba raha hai...")
        page.evaluate('''() => {
            const textarea = document.createElement('textarea');
            textarea.id = 'clipboard-hack';
            textarea.style.position = 'fixed';
            textarea.style.top = '0';
            textarea.style.left = '0';
            document.body.appendChild(textarea);
            textarea.focus();
        }''')
        page.wait_for_timeout(500)
        page.keyboard.press("Control+V")
        page.wait_for_timeout(1000)
        
        copied_text = page.locator('#clipboard-hack').input_value()
        
        # STEP 7: txt file me save karna
        txt_path = os.path.join("downloads", "images.txt")
        if copied_text.strip():
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(copied_text)
            print(f"Success! Saare links '{txt_path}' me save ho gaye.")
        else:
            print("Error: Link copy nahi hui. Kripya video recording check karein.")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("Error: Link copy nahi hui.")

        # Video record end hone ke liye wait
        page.wait_for_timeout(4000)

    except Exception as e:
        print(f"Unexpected Error aaya: {e}")
    finally:
        print("Browser close kar raha hai taaki video file safely save ho jaye...")
        context.close()
        browser.close()
        print("Automation pura hua!")

with sync_playwright() as playwright:
    run(playwright)
