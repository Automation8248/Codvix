import os
import shutil
import zipfile

def process_local_images():
    # Images folder ka path workflow environment ke hisab se set kiya hai
    source_dir = "images"
    
    if not os.path.exists(source_dir):
        print(f"Error: '{source_dir}' directory nahi mili! Ek baar check karein.")
        return

    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
    
    # Folder ke andar ki saari files read karein
    files = os.listdir(source_dir)
    
    # Sirf valid images ko filter karein
    image_files = [f for f in files if f.lower().endswith(valid_extensions)]
    
    if not image_files:
        print("Folder ke andar koi valid images nahi mili!")
        return

    print(f"Total {len(image_files)} images mili hain. Renaming aur Zipping shuru ho rahi hai...")

    zip_name = "all_images_renamed.zip"
    
    # Seedhe zip bundle ke andar write karein bina original files ko delete kiye
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for index, filename in enumerate(sorted(image_files), start=1):
            ext = os.path.splitext(filename).lower()
            
            # Aapke requirement ke mutabik rename format: image.1.jpg, image.2.jpeg
            new_name = f"image.{index}{ext}"
            
            file_path = os.path.join(source_dir, filename)
            print(f"Packing [{index}/{len(image_files)}]: {filename} -> {new_name}")
            
            # File ko zip bundle mein new_name ke sath map karein
            zipf.write(file_path, new_name)
            
    print(f"Success! Zip archive perfectly ready ho chuka hai: {zip_name}")

if __name__ == "__main__":
    process_local_images()
