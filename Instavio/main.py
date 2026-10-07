#!/usr/bin/env python3
"""
Instavio - Instagram Video Downloader with Elite Cloud Upload
Download all videos from an Instagram user profile and upload to Elite Cloud
SECURE VERSION - No hardcoded tokens
"""

import os
import sys
import subprocess
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Elite Cloud Configuration
ELITE_CLOUD_API = "https://shreecloud.up.railway.app/api/v1"
ELITE_CLOUD_FOLDER = "Elite Clip"


class EliteCloudUploader:
    """Handle uploads to Elite Cloud - SECURE VERSION"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Elite Cloud uploader
        
        Args:
            api_key (str): Elite Cloud API key (from env variable)
        """
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv('ELITE_CLOUD_API_KEY')
        
        if not self.api_key:
            logger.warning("⚠️  ELITE_CLOUD_API_KEY not found in environment variables")
            logger.warning("   Set it using: export ELITE_CLOUD_API_KEY='your_key_here'")
            logger.warning("   Or add to .env file")
            self.api_key = None
        else:
            # Log only first and last 4 characters for security
            masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}"
            logger.info(f"✓ Elite Cloud API Key loaded: {masked_key}")
        
        self.headers = {
            "X-API-Key": self.api_key
        } if self.api_key else {}
        
        self.base_url = ELITE_CLOUD_API
        self.folder_id = None
    
    def is_configured(self) -> bool:
        """Check if Elite Cloud is properly configured"""
        return bool(self.api_key)
    
    def create_or_get_folder(self, folder_name: str = ELITE_CLOUD_FOLDER) -> Optional[str]:
        """
        Create or get Elite Clip folder ID
        
        Args:
            folder_name (str): Folder name to create/get
            
        Returns:
            str: Folder ID or None if failed
        """
        if not self.is_configured():
            logger.error("✗ Elite Cloud not configured")
            return None
        
        try:
            logger.info(f"🗂️  Getting or creating folder: {folder_name}")
            
            # Get existing files/folders
            response = requests.get(
                f"{self.base_url}/files",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            files_data = response.json()
            
            # Check if folder exists
            if isinstance(files_data, dict) and 'files' in files_data:
                for item in files_data.get('files', []):
                    if item.get('name') == folder_name and item.get('type') == 'folder':
                        self.folder_id = item.get('id')
                        logger.info(f"✓ Found existing folder: {folder_name}")
                        return self.folder_id
            
            logger.info(f"✓ Folder will be created on first upload: {folder_name}")
            return folder_name
            
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to check folders: {str(e)}")
            return None
    
    def upload_video(self, file_path: Path, username: str) -> Optional[dict]:
        """
        Upload video to Elite Cloud
        
        Args:
            file_path (Path): Path to video file
            username (str): Instagram username for organization
            
        Returns:
            dict: Upload response data or None if failed
        """
        if not self.is_configured():
            logger.error("✗ Elite Cloud API key not configured")
            return None
        
        if not file_path.exists():
            logger.error(f"✗ File not found: {file_path}")
            return None
        
        try:
            file_size = file_path.stat().st_size / (1024 * 1024)  # Size in MB
            logger.info(f"📤 Uploading: {file_path.name} ({file_size:.2f} MB)")
            
            # Prepare file for upload
            files = {
                'file': open(file_path, 'rb')
            }
            
            # Use folder structure: Elite Clip/username/filename
            folder_path = f"{ELITE_CLOUD_FOLDER}/{username}"
            
            data = {
                'path': folder_path
            }
            
            response = requests.post(
                f"{self.base_url}/upload",
                headers=self.headers,
                files=files,
                data=data,
                timeout=300  # 5 minute timeout for large files
            )
            
            files['file'].close()
            
            if response.status_code in [200, 201]:
                upload_data = response.json()
                logger.info(f"✓ Upload successful: {file_path.name}")
                logger.info(f"  📋 File ID: {upload_data.get('id', 'N/A')}")
                return upload_data
            else:
                logger.error(f"✗ Upload failed: {response.status_code}")
                logger.error(f"  Response: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"✗ Upload timeout: {file_path.name}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Upload error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"✗ Unexpected error during upload: {str(e)}")
            return None
    
    def list_uploads(self, folder_path: str) -> Optional[List[dict]]:
        """
        List all files in a folder
        
        Args:
            folder_path (str): Folder path to list
            
        Returns:
            List of files or None if failed
        """
        if not self.is_configured():
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/files",
                headers=self.headers,
                params={'path': folder_path},
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('files', [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to list files: {str(e)}")
            return None


class InstavideoDownloader:
    """Download Instagram videos using Instaloader"""
    
    def __init__(self, username: str):
        """
        Initialize the downloader
        
        Args:
            username (str): Instagram username to download from
        """
        self.username = username
        self.download_dir = Path(f"downloads/{username}")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Elite Cloud uploader (will check for API key internally)
        self.uploader = EliteCloudUploader()
        
        self.downloaded_videos = []
        self.uploaded_videos = []
    
    def check_instaloader(self):
        """Check if instaloader is installed"""
        try:
            import instaloader
            logger.info(f"✓ Instaloader version: {instaloader.__version__}")
            return True
        except ImportError:
            logger.error("✗ Instaloader not installed")
            logger.info("Installing instaloader...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "instaloader"])
                return True
            except Exception as e:
                logger.error(f"Failed to install instaloader: {str(e)}")
                return False
    
    def download_videos(self) -> bool:
        """Download all videos from the Instagram user"""
        try:
            import instaloader
            
            logger.info(f"🎬 Starting download for user: @{self.username}")
            logger.info(f"📁 Download directory: {self.download_dir.absolute()}")
            
            # Create Instaloader instance
            loader = instaloader.Instaloader(
                download_video_only=True,
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
            
            video_count = 0
            for post in profile.get_posts():
                if post.is_video:
                    try:
                        loader.download_post(post, target=str(self.download_dir.parent))
                        
                        # Find downloaded video file
                        video_files = list(self.download_dir.glob(f"*{post.shortcode}*"))
                        if video_files:
                            for video_file in video_files:
                                if video_file.suffix.lower() in ['.mp4', '.mkv', '.mov']:
                                    self.downloaded_videos.append(video_file)
                                    logger.info(f"✓ Downloaded: {post.shortcode}")
                                    video_count += 1
                                    break
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to download {post.shortcode}: {str(e)}")
                        continue
            
            logger.info(f"\n✅ Local download complete!")
            logger.info(f"📈 Total videos downloaded: {video_count}")
            
            return video_count > 0
            
        except instaloader.ProfileNotExistsException:
            logger.error(f"✗ Profile @{self.username} not found")
            return False
        except Exception as e:
            logger.error(f"✗ Error during download: {str(e)}")
            return False
    
    def upload_to_elite_cloud(self) -> bool:
        """Upload downloaded videos to Elite Cloud"""
        if not self.uploader.is_configured():
            logger.warning("\n⚠️  Elite Cloud API key not configured")
            logger.warning("   Skipping cloud upload")
            logger.info("\n   To enable upload, set ELITE_CLOUD_API_KEY:")
            logger.info("   - Linux/Mac: export ELITE_CLOUD_API_KEY='your_key_here'")
            logger.info("   - Windows: set ELITE_CLOUD_API_KEY=your_key_here")
            logger.info("   - Or add to .env file: ELITE_CLOUD_API_KEY=your_key_here")
            return True
        
        if not self.downloaded_videos:
            logger.warning("⚠️  No videos to upload")
            return False
        
        logger.info(f"\n📤 Starting upload to Elite Cloud...")
        logger.info(f"🎬 Videos to upload: {len(self.downloaded_videos)}")
        
        # Create folder
        self.uploader.create_or_get_folder()
        
        for video_file in self.downloaded_videos:
            result = self.uploader.upload_video(video_file, self.username)
            if result:
                self.uploaded_videos.append({
                    'local_file': video_file.name,
                    'cloud_id': result.get('id'),
                    'cloud_name': result.get('name'),
                    'upload_time': datetime.now().isoformat()
                })
        
        logger.info(f"\n✅ Upload complete!")
        logger.info(f"📈 Total videos uploaded: {len(self.uploaded_videos)}")
        
        return len(self.uploaded_videos) > 0
    
    def print_summary(self):
        """Print execution summary"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 INSTAVIO EXECUTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"👤 Username: @{self.username}")
        logger.info(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"")
        logger.info(f"📥 LOCAL DOWNLOADS")
        logger.info(f"   Total videos: {len(self.downloaded_videos)}")
        logger.info(f"   Location: {self.download_dir.absolute()}")
        logger.info(f"")
        
        if self.uploaded_videos:
            logger.info(f"📤 ELITE CLOUD UPLOADS")
            logger.info(f"   Total uploaded: {len(self.uploaded_videos)}")
            logger.info(f"   Folder: {ELITE_CLOUD_FOLDER}/{self.username}")
            logger.info(f"")
            for i, video in enumerate(self.uploaded_videos, 1):
                logger.info(f"   {i}. {video['local_file']}")
                logger.info(f"      Cloud ID: {video['cloud_id']}")
        elif self.uploader.is_configured():
            logger.info(f"☁️  Cloud Upload: Disabled (no API key)")
        
        logger.info("=" * 60)
    
    def main(self):
        """Main execution method"""
        if not self.username:
            logger.error("Username not provided")
            return False
        
        logger.info("=" * 60)
        logger.info("🎥 INSTAVIO - Instagram Video Downloader")
        logger.info("=" * 60)
        logger.info("")
        
        # Check dependencies
        if not self.check_instaloader():
            return False
        
        logger.info("")
        
        # Download videos
        if not self.download_videos():
            logger.error("Failed to download videos")
            return False
        
        # Upload to Elite Cloud if configured
        if self.uploader.is_configured():
            self.upload_to_elite_cloud()
        
        # Print summary
        self.print_summary()
        
        return True


def main():
    """Entry point - SECURE VERSION"""
    logger.info("🔐 Loading configuration from environment variables...\n")
    
    # Get username from command line argument
    if len(sys.argv) < 2:
        username = input("📝 Enter Instagram username: ").strip()
    else:
        username = sys.argv[1].strip()
    
    if not username:
        logger.error("❌ Error: Username is required")
        sys.exit(1)
    
    downloader = InstavideoDownloader(username)
    success = downloader.main()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
