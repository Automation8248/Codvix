import os
import zipfile
import shutil
import gdown
import cloudinary
import cloudinary.uploader

# Cloudinary Setup (GitHub Secrets ya Env Variables se fetch karega)
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Drive File ID aur config
DRIVE_FILE_ID = "1Z1PEqT_dbsH_Gg1DwYqloeuKIEmBObQ5"
ZIP_FILENAME = "downloaded_images.zip"
EXTRACT_FOLDER = "extracted_images"
OUTPUT_FILE = "new.txt"

def main():
    # Step 1: Google Drive se ZIP file download karna
    drive_url = f"https://drive.google.com/uc?id={DRIVE_FILE_ID}"
    print(f"Downloading ZIP file from Google Drive (ID: {DRIVE_FILE_ID})...")
    
    # gdown public Drive links ko easily download kar leta hai
    gdown.download(drive_url, ZIP_FILENAME, quiet=False)
    
    if not os.path.exists(ZIP_FILENAME):
        print("Error: ZIP file download fail ho gayi.")
        return

    # Step 2: ZIP file ko unzip (extract) karna
    print("\nUnzipping the file...")
    os.makedirs(EXTRACT_FOLDER, exist_ok=True)
    with zipfile.ZipFile(ZIP_FILENAME, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_FOLDER)
        
    print("Unzip complete. Starting Cloudinary upload...\n")

    # Step 3: Images ko Cloudinary me upload karna aur link save karna
    uploaded_count = 0
    with open(OUTPUT_FILE, 'a') as file_out:
        # os.walk use karke agar zip ke andar subfolders hain, to unhe bhi scan karega
        for root, dirs, files in os.walk(EXTRACT_FOLDER):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                    file_path = os.path.join(root, file)
                    print(f"Uploading: {file} to Kavlio folder...")
                    
                    try:
                        upload_result = cloudinary.uploader.upload(
                            file_path,
                            folder="Kavlio"
                        )
                        
                        secure_url = upload_result.get('secure_url')
                        
                        # Save link to new.txt
                        file_out.write(secure_url + "\n")
                        print(f"Success: {secure_url}")
                        uploaded_count += 1
                        
                    except Exception as e:
                        print(f"Failed to upload {file}: {str(e)}")

    print(f"\nTask Complete! Total {uploaded_count} image links saved to {OUTPUT_FILE}.")

    # Step 4: Clean up (Downloaded ZIP aur extracted folder ko delete karna)
    print("Cleaning up temporary local files...")
    if os.path.exists(ZIP_FILENAME):
        os.remove(ZIP_FILENAME)
    if os.path.exists(EXTRACT_FOLDER):
        shutil.rmtree(EXTRACT_FOLDER)
    print("Cleanup done!")

if __name__ == "__main__":
    main()
