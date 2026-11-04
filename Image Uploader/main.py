import os
import requests
import cloudinary
import cloudinary.uploader

# Cloudinary Setup
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# GitHub Repo Details
REPO_OWNER = "Automation8248"
REPO_NAME = "Codvix"
BASE_FOLDER_PATH = "Pixhub/Sales post/emergency fund"

headers = {}
gh_token = os.getenv('GH_TOKEN')
if gh_token:
    headers['Authorization'] = f"token {gh_token}"

def get_all_images(path):
    """Recursively fetch all image files from the given GitHub folder path."""
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    response = requests.get(api_url, headers=headers)
    
    files_to_upload = []
    
    if response.status_code == 200:
        items = response.json()
        for item in items:
            if item['type'] == 'file' and item['name'].lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                files_to_upload.append(item)
            elif item['type'] == 'dir':
                print(f"Scanning subfolder: {item['path']}...")
                # Recursive call for subfolders
                files_to_upload.extend(get_all_images(item['path']))
    else:
        print(f"Error fetching {path}: {response.text}")
        
    return files_to_upload

def main():
    print("Fetching file list and scanning subfolders from GitHub...")
    all_images = get_all_images(BASE_FOLDER_PATH)
    print(f"Total images found: {len(all_images)}")
    
    output_file = "link.txt"
    history_file = "history.txt"
    
    # Load previously uploaded files to skip duplicates
    uploaded_history = set()
    if os.path.exists(history_file):
        with open(history_file, 'r') as h_file:
            uploaded_history = set(h_file.read().splitlines())
            
    uploaded_count = 0

    with open(output_file, 'a') as file_out, open(history_file, 'a') as hist_out:
        for file in all_images:
            file_path = file['path'] # Unique GitHub path
            
            # Duplicate Skip Check
            if file_path in uploaded_history:
                print(f"Skipping (Already uploaded): {file['name']}")
                continue
                
            download_url = file['download_url']
            print(f"Uploading: {file['name']} to Kavlio folder...")
            
            try:
                upload_result = cloudinary.uploader.upload(
                    download_url,
                    folder="Kavlio"
                )
                
                secure_url = upload_result.get('secure_url')
                
                # Save link and update history
                file_out.write(secure_url + "\n")
                hist_out.write(file_path + "\n")
                
                print(f"Success: {secure_url}")
                uploaded_count += 1
                uploaded_history.add(file_path)
                
            except Exception as e:
                print(f"Failed to upload {file['name']}: {str(e)}")
                    
    print(f"\nTask Complete! {uploaded_count} new images uploaded and saved.")

if __name__ == "__main__":
    main()
