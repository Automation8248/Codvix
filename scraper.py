from playwright.sync_api import sync_playwright
import os

def run(playwright):
    # Ensure directories exist for the downloads and screen recordings
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("videos", exist_ok=True)

    # Launch fake/headless browser
    browser = playwright.chromium.launch(headless=True)
    
    # Configure context to record screen and accept file downloads automatically
    context = browser.new_context(
        record_video_dir="videos/",
        record_video_size={"width": 1280, "height": 720},
        accept_downloads=True,
        viewport={"width": 1280, "height": 720}
    )
    
    page = context.new_page()
    print("Browser started. Screen recording initialized...")

    # Navigate to the provided Google Drive link
    url = "https://drive.google.com/drive/folders/1pnRfQod0LWTG1Lc5PgYDoESsMXtIYtxX"
    page.goto(url)
    
    # Wait for the folder grid to load fully
    page.wait_for_timeout(8000)
    
    # Optional: Simulate user scrolling to ensure all lazy-loaded images appear in the recording
    page.mouse.wheel(0, 1000)
    page.wait_for_timeout(3000)

    # Note: Google Drive heavily obfuscates its download buttons. 
    # To download automatically via UI, you can inject JS or use keyboard shortcuts (Ctrl+A -> Shift+D)
    page.keyboard.press("Control+A") # Select all files
    page.wait_for_timeout(1000)
    # page.keyboard.press("Shift+D") # Triggers download in some Drive configurations
    
    print("Waiting for any downloads and finishing recording...")
    page.wait_for_timeout(5000)

    # Closing the context automatically saves and finalizes the video file (.webm)
    context.close()
    browser.close()
    print("Automation complete. Video saved to /videos/")

with sync_playwright() as playwright:
    run(playwright)
