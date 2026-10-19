import os
import random
import cv2
import numpy as np
import pytesseract

def process_captcha_exact():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'images')
    
    if not os.path.exists(images_dir):
        print("Error: 'images' folder nahi mila.")
        return

    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
    image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(valid_extensions)]
    
    if not image_files:
        print("Error: 'images' folder mein koi image file nahi mili.")
        return
        
    target_image = random.choice(image_files)
    image_path = os.path.join(images_dir, target_image)
    
    try:
        print(f"-> Processing Image: [{target_image}]...\n")
        
        img = cv2.imread(image_path)
        
        # 1. Image ko 4x bada karna accuracy ke liye
        img = cv2.resize(img, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        
        # 2. Image ke charo taraf 30 pixels ka white border (padding) add karna
        # Isse Tesseract letters ko cut nahi karega
        img = cv2.copyMakeBorder(img, 30, 30, 30, 30, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        
        # 3. Grayscale convert
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 4. Median Blur (Noise clear karta hai bina text ki quality kharab kiye)
        blur = cv2.medianBlur(gray, 3)
        
        # 5. Adaptive Thresholding (Tilted aur faded letters ko perfect black banata hai)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
        
        # 6. Tesseract Config
        # --psm 11 ka matlab hai "Sparse text. Find as much text as possible in no particular order."
        custom_config = r'--oem 3 --psm 11 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        # Text extract karna
        extracted_text = pytesseract.image_to_string(thresh, config=custom_config)
        
        # Captcha mein spaces aur naye lines nahi hote, isliye unhe hila kar clean string banana
        final_text = extracted_text.replace(" ", "").replace("\n", "").strip()
        
        print("====== EXTRACTED TEXT ======")
        if final_text:
            print(final_text)
        else:
            print("[Blank] OCR ko clear text nahi mila.")
        print("============================")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_captcha_exact()
