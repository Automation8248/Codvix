import os
import zipfile
import shutil

def unzip_and_rename_images():
    # 'unzip_folder' ka path jahan script aur zip file hai
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Zip file dhoondna
    zip_files = [f for f in os.listdir(base_dir) if f.endswith('.zip')]
    
    if not zip_files:
        print("Error: Is folder mein koi .zip file nahi mili!")
        return
        
    zip_file_path = os.path.join(base_dir, zip_files[0])
    print(f"Zip file mili: {zip_files[0]}")
    
    # Repo ka main (root) folder path nikalna
    repo_root = os.path.dirname(base_dir)
    
    # Target folder ka path (GitHub repo ke hisaab se)
    target_folder = os.path.join(repo_root, "Pixhub", "Sales post", "emergency fund")
    
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"Target folder banaya gaya: {target_folder}")

    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        count = 1
        for file_info in zip_ref.infolist():
            filename = file_info.filename
            
            if filename.lower().endswith(valid_extensions):
                ext = os.path.splitext(filename)[1].lower()
                new_name = f"{count}{ext}"
                target_path = os.path.join(target_folder, new_name)
                
                with zip_ref.open(file_info) as source, open(target_path, "wb") as target:
                    shutil.copyfileobj(source, target)
                    
                print(f"Saved -> {new_name}")
                count += 1
                
    print("\n✅ Automation Complete!")

if __name__ == "__main__":
    unzip_and_rename_images()
