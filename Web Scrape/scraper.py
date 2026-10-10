from seleniumbase import SB

def scrape_welib():
    # uc=True (Undetected ChromeDriver) and test=True as requested
    # We set headless=False because Cloudflare bypass works best in a headed browser
    # GitHub Actions will run this inside a virtual display (Xvfb)
    with SB(uc=True, test=True, headless=False) as sb:
        url = "https://welib.st"
        
        print(f"Opening {url} and bypassing Cloudflare via CDP...")
        sb.activate_cdp_mode(url)
        
        # Wait 3 seconds upon opening
        sb.sleep(3)
        
        # Wait 5 seconds after the bypass phase is complete
        print("Waiting 5 seconds after bypass...")
        sb.sleep(5)
        
        # Additional action to prove it worked
        page_title = sb.get_page_title()
        print(f"Success! Page Title: {page_title}")
        
        # Taking a screenshot as backup evidence
        sb.save_screenshot("screenshot.png")

if __name__ == "__main__":
    scrape_welib()
