import os
import zipfile
import shutil
import gdown

def download_and_process_zip():
    # 1. Drive file ka ID aur download URL
    file_id = '18CRZ18Yy2uov1-8lcDF0jPKYVVdzEo5f'
    download_url = f'https://drive.google.com/uc?id={file_id}'
    
    # Paths set karna
    base_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(base_dir)
    
    # Download ki jaane wali temporary zip file ka path
    zip_path = os.path.join(base_dir, 'temp_download.zip')
    
    # Target folder (jahan images save hongi)
    target_folder = os.path.join(repo_root, "Pixhub", "Sales post", "emergency fund")
    
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"Target folder banaya gaya: {target_folder}")

    # 2. Google Drive se zip file download karna
    print("Downloading zip file from Google Drive...")
    gdown.download(download_url, zip_path, quiet=False)
    
    if not os.path.exists(zip_path):
        print("Error: Download fail ho gaya ya link private hai!")
        return

    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
    
    # 3. Zip extract karna aur images rename karna
    print("Extracting and renaming images...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        count = 1
        for file_info in zip_ref.infolist():
            filename = file_info.filename
            
            if filename.lower().endswith(valid_extensions):
                ext = os.path.splitext(filename)[1].lower()
                new_name = f"{count}{ext}"  # short name (e.g., 1.jpg)
                target_path = os.path.join(target_folder, new_name)
                
                # Image save karna
                with zip_ref.open(file_info) as source, open(target_path, "wb") as target:
                    shutil.copyfileobj(source, target)
                    
                print(f"Saved -> {new_name}")
                count += 1
                
    # 4. Zip file ko delete karna (Clean up)
    os.remove(zip_path)
    print("Deleted temporary zip file.")
    print("\n✅ Automation Complete! Images saved and zip deleted.")

if __name__ == "__main__":
    download_and_process_zip()
