import os
import requests
import zipfile

def download_rename_zip():
    # Public API endpoint for your repository images folder
    api_url = "https://github.com"
    
    print("Fetching file list from GitHub repository...")
    response = requests.get(api_url)
    
    if response.status_code != 200:
        print(f"Error fetching repo contents: {response.status_code}")
        return
        
    contents = response.json()
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
    
    # Filter for image assets
    image_files = [item for item in contents if item['type'] == 'file' and item['name'].lower().endswith(valid_extensions)]
    
    if not image_files:
        print("No valid images found in the folder!")
        return
        
    print(f"Found {len(image_files)} images. Starting processing...")
    
    zip_name = "all_images_renamed.zip"
    
    # Pack directly into a zip bundle
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for index, item in enumerate(image_files, start=1):
            file_url = item['download_url']
            original_name = item['name']
            ext = os.path.splitext(original_name).lower()
            
            # Formatting sequence: image.1.jpg, image.2.jpeg etc.
            new_name = f"image.{index}{ext}"
            
            print(f"Downloading [{index}/{len(image_files)}]: {new_name}")
            
            img_response = requests.get(file_url)
            if img_response.status_code == 200:
                zipf.writestr(new_name, img_response.content)
            else:
                print(f"Failed to fetch: {original_name}")
                
    print(f"Success! Zip archive created successfully: {zip_name}")

if __name__ == "__main__":
    download_rename_zip()
