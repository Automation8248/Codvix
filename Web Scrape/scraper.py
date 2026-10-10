import os
import time
import random
import glob
import shutil
import pyperclip
from seleniumbase import SB

def smooth_scroll(sb, direction="down"):
    """Bot-detection se bachne ke liye insaano jaisa dheere-dheere scroll karna."""
    if direction == "down":
        for i in range(1, 8):
            sb.execute_script(f"window.scrollBy(0, {random.randint(150, 300)});")
            time.sleep(random.uniform(0.2, 0.5))
    else:
        for i in range(1, 8):
            sb.execute_script(f"window.scrollBy(0, {-random.randint(150, 300)});")
            time.sleep(random.uniform(0.2, 0.5))
    time.sleep(1)

def scrape_welib():
    # Saare zaroori folders create karna
    os.makedirs("Books/Download Book", exist_ok=True)
    os.makedirs("Screenshots", exist_ok=True)

    # search.txt se topic padhna
    try:
        with open("search.txt", "r", encoding="utf-8") as f:
            topics = [line.strip() for line in f if line.strip()]
        search_query = random.choice(topics) if topics else "The Bible"
    except FileNotFoundError:
        search_query = "The Bible"

    # File ka naam format karna (e.g., "The Bible" -> "the_bible")
    formatted_topic = search_query.lower().replace(" ", "_")
    print(f"Topic selected: {search_query} | File prefix: {formatted_topic}")

    # Aapka diya gaya logic (bina purane features remove kiye)
    with SB(uc=True, test=True, headless=False) as sb:
        url = "https://welib.st"
        
        try:
            print("1. Website par ja rahe hain (Cloudflare Bypass via CDP)...")
            sb.activate_cdp_mode(url)
            
            print("2. Bypass hone ke baad exact 10 second wait kar rahe hain...")
            sb.sleep(10) # 👉 AAPKA EXACT LOGIC YAHAN ADD KIYA GAYA HAI
            
            print("3. Human-like Scroll: Upar se niche, fir wapas upar...")
            smooth_scroll(sb, "down")
            sb.sleep(random.uniform(1.0, 2.0))
            smooth_scroll(sb, "up")
            sb.execute_script("window.scrollTo(0, 0);") # Ensure top position
            
            print("4. Search box dhoondh rahe hain (Title, author, DOI, ISBN)...")
            # CSS Selector jo placeholder me in words ko dhoondhega
            search_box_selector = "input[placeholder*='Title'], input[placeholder*='author'], input[placeholder*='DOI'], input[placeholder*='ISBN']"
            
            # Type as a human (delay between keystrokes)
            sb.type(search_box_selector, search_query + "\n", timeout=10)
            sb.sleep(random.uniform(4.0, 5.0))
            sb.save_screenshot("Screenshots/01_after_search.png")
            
            print("5. Search results ke baad thoda niche scroll...")
            sb.execute_script("window.scrollBy(0, 350);")
            sb.sleep(2)
            
            print("6. Pehli book select kar rahe hain...")
            sb.click("h3 a, .book-title a, article a", timeout=10) 
            sb.sleep(random.uniform(3.0, 4.0))
            
            # Agar click hone ke baad naya tab open hua ho, toh usme switch karna
            if len(sb.driver.window_handles) > 1:
                sb.switch_to_window(1)
            
            print("7. Thoda niche scroll karke 'PDF:' ke aage wala Download button dhoondhna...")
            sb.execute_script("window.scrollBy(0, 400);")
            sb.sleep(2)
            sb.save_screenshot("Screenshots/02_book_page.png")
            
            # XPath jo 'PDF:' text dhoondhta hai aur uske aas-paas ka button nikalta hai
            pdf_download_btn_xpath = "//*[contains(text(), 'PDF:')]/following-sibling::*//a | //*[contains(text(), 'PDF:')]/..//a[contains(@class, 'download') or contains(@href, 'download')]"
            sb.click(pdf_download_btn_xpath, timeout=10)
            
            print("8. 40 second wait kar rahe hain (Anti-bot / File Prep)...")
            sb.sleep(40)
            
            print("9. '(📚 Download Now)' button aur Copy icon par click karna...")
            sb.save_screenshot("Screenshots/03_ready_to_download.png")
            
            # Download Now button click
            download_now_xpath = "//*[contains(text(), 'Download Now') or contains(text(), '📚 Download Now')]"
            sb.click(download_now_xpath, timeout=10)
            
            # 7 second total wait hai. 2 second baad copy icon click karenge.
            sb.sleep(2)
            print("   -> Copy icon par click kar rahe hain...")
            copy_icon_xpath = f"{download_now_xpath}/following-sibling::*[1] | {download_now_xpath}/..//button[contains(@class, 'copy')]"
            sb.click(copy_icon_xpath, timeout=5)
            
            # Bacha hua 5 second wait (total 7 seconds)
            sb.sleep(5)
            
            # Clipboard se link nikal kar text file me save karna
            copied_link = pyperclip.paste()
            txt_file_path = f"Books/Download Book/{formatted_topic}.txt"
            with open(txt_file_path, "w", encoding="utf-8") as f:
                f.write(copied_link if copied_link else "Link copy nahi ho paya.")
            print(f"Copied link saved to: {txt_file_path}")
            
            # Downloaded file ko rename karke Books folder me daalna
            download_dir = "downloaded_files"
            if os.path.exists(download_dir):
                files = glob.glob(f"{download_dir}/*")
                time_waited = 0
                while any(f.endswith('.crdownload') for f in files) and time_waited < 30:
                    time.sleep(2)
                    time_waited += 2
                    files = glob.glob(f"{download_dir}/*")
                
                valid_files = [f for f in files if not f.endswith('.crdownload')]
                if valid_files:
                    latest_file = max(valid_files, key=os.path.getctime)
                    new_pdf_path = os.path.join("Books", f"{formatted_topic}.pdf")
                    shutil.move(latest_file, new_pdf_path)
                    print(f"Book successfully renamed and saved to: {new_pdf_path}")
                else:
                    print("Download complete nahi hua.")
            else:
                print("Download folder nahi bana. Shayad file download nahi hui.")

            print("Scraping and downloading successfully completed!")

        except Exception as e:
            print(f"Error aaya: {e}")
            sb.save_screenshot("Screenshots/ERROR_SCREEN.png")
            print("Error ka screenshot le liya gaya hai.")

if __name__ == "__main__":
    scrape_welib()
