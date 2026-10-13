import os
import requests

def download_file(url, save_dir="downloads"):
    # Agar downloads folder nahi hai toh naya bana dega
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    # URL se file ka naam nikalna (jaise document.pdf)
    filename = url.split("/")[-1] or "downloaded_file"
    save_path = os.path.join(save_dir, filename)
    
    print(f"Downloading {filename}...")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                
        print(f"Success! File saved at: {save_path}")
    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    # Yahan apni target website ki file ka direct URL daalein
    target_url = "https://download938.mediafire.com/sg0nzkk4p40gtmVHVZe5Qfpfxq8tg2QqEwutlRODJBaBn2LjnKVLQrrJSTWnd1bKJm8SWzKw4juieyq6DctrgA6X5W2iVQSSWSk8XQ07X8PMseKGXsVDWfdOpSGQJDpiEgnQml2bn9pQTgHXIfp-0Hz6Nlw25BNXPY16lRncxG_tYg/qqvfybpkoaobdw2/Instagram+Auto+Account+Creator+.py"
    
    download_file(target_url)
