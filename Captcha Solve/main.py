import os
import random
from PIL import Image
import pytesseract

def read_random_image_text():
    # Folder paths setup
    base_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(base_dir, 'images')
    
    # Check karna ki images folder hai ya nahi
    if not os.path.exists(images_dir):
        print("Error: 'images' folder nahi mila. Kripya 'images' folder banakar usme images dalein.")
        return

    # Folder se valid image files dhundna
    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
    image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(valid_extensions)]
    
    if not image_files:
        print("Error: 'images' folder mein koi image file nahi mili.")
        return
        
    # Randomly ek image select karna
    target_image = random.choice(image_files)
    image_path = os.path.join(images_dir, target_image)
    
    try:
        print(f"Randomly selected file: [{target_image}] ko analyze kiya ja raha hai...\n")
        
        # Image open karke text extract karna
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img)
        
        print("--- Output Result ---")
        if extracted_text.strip():
            print(extracted_text.strip())
        else:
            print("[Blank] Image mein clear text detect nahi hua ya text readable nahi hai.")
        print("---------------------")
        
    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    read_random_image_text()
