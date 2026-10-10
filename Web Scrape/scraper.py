import os
import time
import random
import glob
import shutil
from seleniumbase import SB

def scrape_welib():
    # Folders create karna agar wo nahi hain
    os.makedirs("Books", exist_ok=True)
    os.makedirs("Screenshots", exist_ok=True)

    # search.txt se topics read karna
    try:
        with open("search.txt", "r", encoding="utf-8") as f:
            topics = [line.strip() for line in f if line.strip()]
        search_query = random.choice(topics) if topics else "technology"
    except FileNotFoundError:
        print("search.txt nahi mila, default topic search kar rahe hain.")
        search_query = "technology"

    print(f"Topic selected for search: {search_query}")

    with SB(uc=True, test=True, headless=False) as sb:
        url = "https://welib.st"
        
        print("1. Website open kar rahe hain...")
        sb.activate_cdp_mode(url)
        sb.sleep(3) # Wait 3 seconds
        sb.save_screenshot("Screenshots/01_cloudflare_checking.png")
        
        print("2. Cloudflare bypass ke baad 5 second wait kar rahe hain...")
        sb.sleep(5)
        sb.save_screenshot("Screenshots/02_website_loaded.png")
        
        print("3. Upar-niche scroll kar rahe hain...")
        sb.execute_script("window.scrollTo(0, 800);") # Niche scroll
        sb.sleep(1)
        sb.execute_script("window.scrollTo(0, 0);")   # Upar scroll
        sb.sleep(2)
        sb.save_screenshot("Screenshots/03_after_scroll.png")
        
        print("4. Search bar mein type kar rahe hain...")
        # ⚠️ IMPORTANT: Niche diye gaye selector ('input[type="text"]') ko website ke actual search bar selector se replace karein
        search_input_selector = "input[type='text']" 
        sb.type(search_input_selector, search_query + "\n") # \n se Enter press hoga
        sb.sleep(5)
        sb.save_screenshot("Screenshots/04_search_results.png")
        
        print("5. Pehli book select kar rahe hain...")
        # ⚠️ IMPORTANT: Is selector ko book ke actual link/title selector se replace karein
        first_book_selector = "h3 a" 
        sb.click(first_book_selector)
        sb.sleep(5)
        sb.save_screenshot("Screenshots/05_book_page.png")
        
        print("6. Book download kar rahe hain...")
        # ⚠️ IMPORTANT: Download button ka actual selector yahan dalein
        download_button_selector = "a.download-btn" 
        sb.click(download_button_selector)
        
        # Download complete hone ka wait (adjust time as needed)
        print("Downloading in progress... waiting 15 seconds")
        sb.sleep(15)
        sb.save_screenshot("Screenshots/06_after_download.png")
        
        # Downloaded file ko 'Books' folder mein move karna
        # SeleniumBase default downloads ko 'downloaded_files' folder mein rakhta hai
        download_dir = "downloaded_files"
        if os.path.exists(download_dir):
            files = glob.glob(f"{download_dir}/*")
            for file in files:
                shutil.move(file, os.path.join("Books", os.path.basename(file)))
            print("Book successfully 'Books' folder mein save ho gayi.")
        else:
            print("Download folder nahi mila. Shayad download fail ho gaya ya alag location par save hua.")

if __name__ == "__main__":
    scrape_welib()
