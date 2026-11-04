import os
import requests
import cloudinary
import cloudinary.uploader

# Cloudinary Setup (Environment Variables se credentials fetch karega)
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# GitHub Repo Details
REPO_OWNER = "Automation8248"
REPO_NAME = "Codvix"
FOLDER_PATH = "Pixhub/Sales post/emergency fund"

# GitHub API URL file fetch karne ke liye
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FOLDER_PATH}"

# Agar GitHub API limit reach ho jaye, to GH_TOKEN use karega (GitHub actions ke liye zaroori)
headers = {}
gh_token = os.getenv('GH_TOKEN')
if gh_token:
    headers['Authorization'] = f"token {gh_token}"

def main():
    print("Fetching file list from GitHub...")
    response = requests.get(GITHUB_API_URL, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching GitHub contents: {response.text}")
        return

    files = response.json()
    output_file = "link.txt"
    
    uploaded_count = 0

    with open(output_file, 'a') as file_out:
        for file in files:
            # Sirf image files ko process kare
            if file['type'] == 'file' and file['name'].lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                download_url = file['download_url']
                print(f"Uploading: {file['name']}")
                
                try:
                    # GitHub direct download URL se Cloudinary me upload
                    upload_result = cloudinary.uploader.upload(
                        download_url,
                        folder="emergency_fund_images" # Cloudinary me is folder me save hoga
                    )
                    
                    secure_url = upload_result.get('secure_url')
                    
                    # Text file me direct link save kare
                    file_out.write(secure_url + "\n")
                    print(f"Success: {secure_url}")
                    uploaded_count += 1
                    
                except Exception as e:
                    print(f"Failed to upload {file['name']}: {str(e)}")
                    
    print(f"\nTask Complete! {uploaded_count} image links saved to {output_file}.")

if __name__ == "__main__":
    main()
