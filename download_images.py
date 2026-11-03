import os
import requests
import zipfile

def download_rename_zip():
    # Target repository folder endpoint
    api_url = "https://github.com"
    
    # Set headers to explicitly avoid HTTP 406 or request blocks
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Read the custom secret name GH_TOKEN from environment parameters
    gh_token = os.getenv("GH_TOKEN")
    if gh_token:
        headers["Authorization"] = f"token {gh_token}"
        print("Authenticated session initiated using GH_TOKEN.")
    else:
        print("Warning: Running without GH_TOKEN authentication.")

    print("Fetching file list from target GitHub repository...")
    response = requests.get(api_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching repo contents. Status Code: {response.status_code}")
        print(f"Server Raw Output Preview: {response.text[:200]}")
        return
        
    contents = response.json()
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
    
    # Filter for image assets
    image_files = [item for item in contents if item['type'] == 'file' and item['name'].lower().endswith(valid_extensions)]
    
    if not image_files:
        print("No valid images found in the target folder!")
        return
        
    print(f"Found {len(image_files)} images. Starting processing...")
    
    zip_name = "all_images_renamed.zip"
    
    # Direct streaming of raw download bytes into a zip bundle
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for index, item in enumerate(image_files, start=1):
            file_url = item['download_url']
            original_name = item['name']
            ext = os.path.splitext(original_name).lower()
            
            # Formatting sequence: image.1.jpg, image.2.jpeg etc.
            new_name = f"image.{index}{ext}"
            
            print(f"Downloading [{index}/{len(image_files)}]: {new_name}")
            
            img_response = requests.get(file_url, headers={"User-Agent": headers["User-Agent"]})
            if img_response.status_code == 200:
                zipf.writestr(new_name, img_response.content)
            else:
                print(f"Failed to fetch: {original_name}")
                
    print(f"\nSuccess! All images have been zipped into: {zip_name}")

if __name__ == "__main__":
    download_rename_zip()
