import os
from playwright.sync_api import sync_playwright, TimeoutError

def run(playwright):
    # 1. Folders banayen jahan txt file aur video save hongi
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("videos", exist_ok=True)

    # 2. Browser aur screen recording setup
    browser = playwright.chromium.launch(headless=True)
    
    # Context me clipboard access permissions di gayi hain taaki copy link kaam kare
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
        
        print("Drive link open ho raha hai, wait kar rahe hain...")
        page.wait_for_timeout(8000)
        
        # Files load hone ka wait karein
        page.wait_for_selector('div[data-id], div[role="gridcell"]', timeout=40000)
        page.wait_for_timeout(3000) 
        
        files = page.locator('div[data-id][aria-label]').all()
        if not files:
            files = page.locator('div[data-id], div[role="gridcell"]').all()

        if not files:
            print("Koi files nahi mili. Script check karein.")
            return
            
        print(f"Total {len(files)} files/folders mile.")
        
        # 3. Ctrl + A (Sabhi files ko select karna)
        print("First file par click karke focus laa raha hai...")
        files[0].click()
        page.wait_for_timeout(1000)
        
        print("Ctrl+A daba raha hai...")
        page.keyboard.press("Control+A")
        page.wait_for_timeout(2000) # Select hone ka wait
        
        # 4. Right Click karna
        print("Right click kar raha hai...")
        files[0].click(button="right")
        page.wait_for_timeout(2000) # Menu khulne ka wait
        
        # 5. Share > Copy link dhundhna aur click karna
        print("Menu mein 'Copy link' ya 'Share' dhundh raha hai...")
        
        copy_link_btn = page.locator('div[role="menuitem"]:has-text("Copy link")').first
        share_btn = page.locator('div[role="menuitem"]:has-text("Share")').first
        
        if copy_link_btn.is_visible():
            print("'Copy link' option mil gaya, click kar raha hai...")
            copy_link_btn.click()
        elif share_btn.is_visible():
            print("'Share' option mila, hover karke 'Copy link' nikal raha hai...")
            share_btn.hover()
            page.wait_for_timeout(1000)
            sub_copy = page.locator('div[role="menuitem"]:has-text("Copy link")').first
            if sub_copy.is_visible():
                sub_copy.click()
            else:
                share_btn.click()
        else:
            print("Menu nahi mila, direct Ctrl+C backup option use kar raha hai...")
            page.keyboard.press("Control+C")
            
        page.wait_for_timeout(3000) # Link copy hone ke liye time
        
        # 6. Clipboard se links nikalna (Headless Hack)
        print("Clipboard se links nikal raha hai...")
        copied_text = ""
        
        try:
            # Playwright ka direct clipboard API use karte hain
            copied_text = page.evaluate("navigator.clipboard.readText()")
        except:
            pass
            
        if not copied_text.strip():
            # Agar API fail ho jaye (headless hone ki wajah se), toh Textarea inject karke Ctrl+V karenge
            print("API fail hui, Ctrl+V method try kar raha hai...")
            page.evaluate('''() => {
                const textarea = document.createElement('textarea');
                textarea.id = 'clipboard-hack';
                document.body.appendChild(textarea);
                textarea.focus();
            }''')
            page.keyboard.press("Control+V")
            page.wait_for_timeout(1000)
            copied_text = page.locator('#clipboard-hack').input_value()
        
        # 7. images.txt me save karna
        txt_path = os.path.join("downloads", "images.txt")
        if copied_text.strip():
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(copied_text)
            print(f"Badiya! Saare links copy ho gaye aur '{txt_path}' me save ho gaye.")
        else:
            print("Koi link copy nahi hui. Video check karein.")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("Error: Link copy nahi ho paayi, kripya video recording check karein.")

        page.wait_for_timeout(4000)

    except TimeoutError:
        print("TimeoutError: Load hone mein zyada time le raha hai.")
    except Exception as e:
        print(f"Unexpected Error aaya: {e}")
    finally:
        print("Browser close kar raha hai taaki video file safely save ho jaye...")
        context.close()
        browser.close()
        print("Automation pura hua. Zip me images.txt aur video mil jayegi.")

with sync_playwright() as playwright:
    run(playwright)
