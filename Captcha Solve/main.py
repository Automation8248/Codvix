import os
import random
import ddddocr

def solve_captcha_ai():
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
        print(f"-> AI Engine Processing Image: [{target_image}]...\n")
        
        # ddddocr initialize karna (show_ad=False se extra logs hide ho jate hain)
        ocr = ddddocr.DdddOcr(show_ad=False)
        
        # Image ko bytes format mein read karna
        with open(image_path, 'rb') as f:
            img_bytes = f.read()
        
        # AI se text extract karna
        extracted_text = ocr.classification(img_bytes)
        
        print("====== EXTRACTED TEXT ======")
        if extracted_text:
            # Output ko uppercase mein convert kar rahe hain taki J5ZVF format mile
            print(extracted_text.upper())
        else:
            print("[Blank] Model ko koi text nahi mila.")
        print("============================")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    solve_captcha_ai()
