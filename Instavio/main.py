#!/usr/bin/env python3
"""
Instavio - Instagram Video Downloader
Download all videos from an Instagram user profile by username
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InstavideoDownloader:
    """Download Instagram videos using Instaloader"""
    
    def __init__(self, username):
        """
        Initialize the downloader
        
        Args:
            username (str): Instagram username to download from
        """
        self.username = username
        self.download_dir = Path(f"downloads/{username}")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def check_instaloader(self):
        """Check if instaloader is installed"""
        try:
            import instaloader
            logger.info(f"✓ Instaloader version: {instaloader.__version__}")
            return True
        except ImportError:
            logger.error("✗ Instaloader not installed")
            logger.info("Installing instaloader...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "instaloader"])
            return True
    
    def download_videos(self):
        """Download all videos from the Instagram user"""
        try:
            import instaloader
            
            logger.info(f"🎬 Starting download for user: @{self.username}")
            logger.info(f"📁 Download directory: {self.download_dir.absolute()}")
            
            # Create Instaloader instance
            loader = instaloader.Instaloader(
                download_video_only=True,  # Only download videos, not images
                download_comments=False,
                download_geotags=False,
                dirname_pattern=str(self.download_dir),
                filename_pattern="{date_utc}_{shortcode}"
            )
            
            logger.info(f"📥 Fetching profile...")
            profile = instaloader.Profile.from_username(loader.context, self.username)
            
            logger.info(f"👤 Profile: {profile.full_name or self.username}")
            logger.info(f"📊 Total posts: {profile.mediacount}")
            logger.info(f"⏱️  Processing videos...")
            
            # Download all posts (videos only due to download_video_only=True)
            video_count = 0
            for post in profile.get_posts():
                if post.is_video:
                    try:
                        loader.download_post(post, target=str(self.download_dir.parent))
                        video_count += 1
                        logger.info(f"✓ Downloaded: {post.shortcode}")
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to download {post.shortcode}: {str(e)}")
                        continue
            
            logger.info(f"\n✅ Download complete!")
            logger.info(f"📈 Total videos downloaded: {video_count}")
            logger.info(f"📂 Location: {self.download_dir.absolute()}")
            
            return True
            
        except instaloader.ProfileNotExistsException:
            logger.error(f"✗ Profile @{self.username} not found")
            return False
        except Exception as e:
            logger.error(f"✗ Error during download: {str(e)}")
            return False
    
    def main(self):
        """Main execution method"""
        if not self.username:
            logger.error("Username not provided")
            return False
        
        logger.info("=" * 50)
        logger.info("🎥 Instavio - Instagram Video Downloader")
        logger.info("=" * 50)
        
        # Check dependencies
        if not self.check_instaloader():
            return False
        
        # Download videos
        return self.download_videos()


def main():
    """Entry point"""
    # Get username from command line argument
    if len(sys.argv) < 2:
        username = input("Enter Instagram username: ").strip()
    else:
        username = sys.argv[1].strip()
    
    if not username:
        print("Error: Username is required")
        sys.exit(1)
    
    downloader = InstavideoDownloader(username)
    success = downloader.main()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
