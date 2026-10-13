import os
import requests

def download_file(url):
    # Script ki current directory (FileVex) ka pata lagana
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # FileVex ke andar 'downloads' folder ka rasta set karna
    save_dir = os.path.join(base_dir, "downloads")
    
    # Agar downloads folder nahi hai toh bana dena
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    # URL se file ka aakhiri naam nikalna
    filename = url.split("/")[-1] or "downloaded_file"
    save_path = os.path.join(save_dir, filename)
    
    print(f"Downloading: {filename}")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                
        print(f"Success! File yahan save ho gayi hai: {save_path}")
    except Exception as e:
        print(f"Download fail ho gaya: {e}")

if __name__ == "__main__":
    # Apni file ka URL yahan daalein
    target_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    
    download_file(target_url)
