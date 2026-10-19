import os
import random
import cv2
import numpy as np
import pytesseract

def process_captcha_advanced():
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
        
        # 1. Image load karna
        img = cv2.imread(image_path)
        
        # 2. Image ko 3x bada (resize) karna (Tesseract bade text ko achhe se padhta hai)
        img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        
        # 3. Grayscale mein convert karna
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 4. Blur apply karna taki background noise (chhote dots) hat jayein
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 5. Thresholding (Text ko pure black aur background ko pure white karna)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 6. Morphological Operations (Agar text patla ya tuta hua hai toh usko fill karna)
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.dilate(thresh, kernel, iterations=1)
        thresh = cv2.erode(thresh, kernel, iterations=1)
        
        # 7. Tesseract Config (PSM 7: Treat image as a single text line)
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        # 8. Text Extract karna
        extracted_text = pytesseract.image_to_string(thresh, config=custom_config)
        final_text = extracted_text.strip()
        
        print("====== EXTRACTED TEXT ======")
        if final_text:
            print(final_text)
        else:
            print("[Blank] OCR ko koi clear text nahi mila. Image jyada distorted hai.")
        print("============================")
        
    except Exception as e:
        print(f"Image Analyze karte waqt error aayi: {e}")

if __name__ == "__main__":
    process_captcha_advanced()
