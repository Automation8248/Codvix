#!/usr/bin/env python3
"""
Instavio - Instagram Video Downloader with Elite Cloud Upload
Compatible with Instaloader 4.15.3+
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime

import requests
from dotenv import load_dotenv
from instaloader import Instaloader, Profile, ProfileNotExistsException

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

ELITE_CLOUD_API = "https://shreecloud.up.railway.app/api/v1"
ELITE_CLOUD_FOLDER = "Elite Clip"

def ensure_instaloader():
    try:
        import instaloader
        logger.info(f"Instaloader version: {instaloader.__version__}")
        return True
    except Exception:
        logger.info("Installing instaloader...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "instaloader"])
        return True

def upload_to_elite_cloud(username: str, api_key: str):
    if not api_key:
        logger.warning("ELITE_CLOUD_API_KEY not set. Skipping cloud upload.")
        return

    headers = {"X-API-Key": api_key}
    folder_path = f"{ELITE_CLOUD_FOLDER}/{username}"

    target_dir = Path("downloads") / username
    files = []
    if target_dir.exists():
        for file in target_dir.iterdir():
            if file.is_file() and file.suffix.lower() in [".mp4", ".mkv", ".mov", ".webm"]:
                files.append(file)

    if not files:
        logger.warning("No downloaded videos found to upload.")
        return

    logger.info(f"Uploading {len(files)} videos to Elite Cloud folder: {folder_path}")

    for file_path in files:
        try:
            with open(file_path, "rb") as f:
                response = requests.post(
                    f"{ELITE_CLOUD_API}/upload",
                    headers=headers,
                    files={"file": (file_path.name, f)},
                    data={"path": folder_path},
                    timeout=300
                )
            if response.ok:
                logger.info(f"Uploaded: {file_path.name}")
            else:
                logger.error(f"Upload failed for {file_path.name}: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error uploading {file_path.name}: {e}")

def download_user_videos(username: str, api_key: str = None):
    ensure_instaloader()

    target_dir = Path("downloads") / username
    target_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading videos for user: @{username}")
    logger.info(f"Target folder: {target_dir}")

    loader = Instaloader(
        download_comments=False,
        download_geotags=False
    )

    try:
        profile = Profile.from_username(loader.context, username)
    except ProfileNotExistsException:
        logger.error(f"Profile not found: @{username}")
        return False

    downloaded = 0
    for post in profile.get_posts():
        if post.is_video:
            try:
                loader.download_post(post, target=str(target_dir))
                downloaded += 1
                logger.info(f"Downloaded video: {post.shortcode}")
            except Exception as e:
                logger.warning(f"Failed to download post {post.shortcode}: {e}")

    logger.info(f"Total downloaded: {downloaded}")

    if api_key:
        upload_to_elite_cloud(username, api_key)

    return True

def main():
    username = None
    if len(sys.argv) > 1:
        username = sys.argv[1].strip()
    else:
        username = input("Enter Instagram username: ").strip()

    if not username:
        logger.error("Username is required.")
        sys.exit(1)

    api_key = os.getenv("ELITE_CLOUD_API_KEY")
    success = download_user_videos(username, api_key)

    if success:
        logger.info("Execution completed successfully")
    else:
        logger.error("Execution failed")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
