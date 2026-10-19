import os
import random
import cv2  # OpenCV for image preprocessing
import pytesseract

def process_captcha_image():
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
        
        # 1. OpenCV se image ko load karna
        img = cv2.imread(image_path)
        
        # 2. Image ko Grayscale (Black & White) mein convert karna
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 3. Thresholding (Background ko pure white aur text ko pure black banana)
        # OTSU thresholding automatic best contrast nikal leta hai
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 4. Tesseract Configuration:
        # --psm 8 : Treat the image as a single word (Bahut zaroori Captcha ke liye)
        # -c tessedit_char_whitelist : OCR ko force karna ki wo sirf A-Z aur 0-9 hi guess kare
        custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        # 5. Extract Text
        extracted_text = pytesseract.image_to_string(thresh, config=custom_config)
        
        # Output clean karna
        final_text = extracted_text.strip()
        
        print("====== EXTRACTED TEXT ======")
        if final_text:
            print(final_text)
        else:
            print("[Blank] OCR ko image mein koi clear text nahi mila.")
        print("============================")
        
    except Exception as e:
        print(f"Image Analyze karte waqt error aayi: {e}")

if __name__ == "__main__":
    process_captcha_image()
