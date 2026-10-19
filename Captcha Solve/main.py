import os
import random
from PIL import Image
import pytesseract

def process_captcha_image():
    # 1. Script ka exact path nikalna (taki GitHub par path ki error na aaye)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'images')
    
    print("====== SYSTEM INFO ======")
    print(f"Script Directory: {script_dir}")
    print(f"Target Images Folder: {images_dir}")
    print("=========================\n")
    
    # 2. Agar GitHub par images folder upload nahi hua, toh crash hone se bachana
    if not os.path.exists(images_dir):
        print("Warning: 'images' folder nahi mila! Script automatically folder create kar rahi hai...")
        os.makedirs(images_dir)
        print("Folder create ho gaya hai. Lekin isme koi image nahi hai. Kripya GitHub par image upload karein.")
        return

    # 3. Images folder ke andar ki sabhi files ko list karna
    all_files = os.listdir(images_dir)
    print(f"Files found in 'images' folder: {all_files}\n")

    # 4. Sirf image files (.png, .jpg, .jpeg, .webp) filter karna (naam kuch bhi ho)
    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
    image_files = [f for f in all_files if f.lower().endswith(valid_extensions)]
    
    if not image_files:
        print("Error: 'images' folder mein koi image file nahi mili. Kripya ek .png, .jpg ya .webp file dalein.")
        return
        
    # 5. List mein se koi ek random image select karna
    target_image = random.choice(image_files)
    image_path = os.path.join(images_dir, target_image)
    
    try:
        print(f"-> Processing Image: [{target_image}]...\n")
        
        # 6. Image open karke OCR se text nikalna
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img)
        
        # 7. Final Output Print Karna
        print("====== EXTRACTED TEXT ======")
        if extracted_text.strip():
            print(extracted_text.strip())
        else:
            print("[Blank] OCR ko image mein koi clear text nahi mila.")
        print("============================")
        
    except Exception as e:
        print(f"Image Analyze karte waqt error aayi: {e}")

if __name__ == "__main__":
    process_captcha_image()
