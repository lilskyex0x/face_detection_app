import cv2
import os
import time
from datetime import datetime

# Configuration
DATASET_DIR = "face_dataset"
TOTAL_IMAGES = 10
CAPTURE_INTERVAL = 1

# ==================== CAPTURE FACES ====================

def capture_faces(person_name):
    print(f"\n=== Capturing faces for: {person_name} ===\n")
    
    # Load face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Open camera
    cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("ERROR: Cannot open camera")
        return False
    
    print("Camera opened successfully!")
    
    # Create folder
    person_dir = os.path.join(DATASET_DIR, person_name)
    os.makedirs(person_dir, exist_ok=True)
    
    # Warm up camera
    print("Warming up camera...")
    for _ in range(20):
        cap.read()
    
    print("Ready! Window will open now.\n")
    
    images_captured = 0
    last_capture_time = 0
    start_time = time.time()
    
    while images_captured < TOTAL_IMAGES:
        ret, frame = cap.read()
        if not ret:
            continue
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Draw rectangles for preview
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Preview window
        cv2.putText(frame, f"Captured: {images_captured}/{TOTAL_IMAGES}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow('Camera - Press Q to quit', frame)
        
        # Save every second
        current_time = time.time()
        if current_time - last_capture_time >= CAPTURE_INTERVAL:
            if len(faces) > 0:
                # Save ONLY the first detected face
                (x, y, w, h) = faces[0]
                face_crop = frame[y:y+h, x:x+w]

                filename = f"{person_name}_{images_captured+1}.jpg"
                filepath = os.path.join(person_dir, filename)

                cv2.imwrite(filepath, face_crop)
                images_captured += 1
                print(f"✓ Saved face {images_captured}/{TOTAL_IMAGES}")
            else:
                print("No face detected — skipping frame.")
            
            last_capture_time = current_time
        
        # Quit option
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        # Timeout after 15 seconds
        if time.time() - start_time > 15:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n✓ Complete! {images_captured} images saved in: {person_dir}/\n")
    return True

# ==================== PROCESS IMAGES ====================

def process_images(person_name):
    print(f"\n=== Processing images for: {person_name} ===\n")
    
    person_dir = os.path.join(DATASET_DIR, person_name)
    
    if not os.path.exists(person_dir):
        print(f"ERROR: No folder found for {person_name}")
        return
    
    # Load face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Get all images
    images = [f for f in os.listdir(person_dir) if f.endswith('.jpg')]
    
    if not images:
        print("No images found")
        return
    
    # Create output folder
    output_dir = os.path.join(DATASET_DIR, f"{person_name}_processed")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Processing {len(images)} images...\n")
    
    total_faces = 0
    
    for img_file in images:
        img_path = os.path.join(person_dir, img_file)
        img = cv2.imread(img_path)
        
        if img is None:
            continue
        
        # Preprocessing
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Draw rectangles and labels
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(img, person_name, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            total_faces += 1
        
        # Save processed image
        output_path = os.path.join(output_dir, f"processed_{img_file}")
        cv2.imwrite(output_path, img)
    
    print(f"✓ Done! Detected {total_faces} faces")
    print(f"✓ Processed images saved in: {output_dir}/\n")

# ==================== DISPLAY RESULTS ====================

def display_results(person_name):
    output_dir = os.path.join(DATASET_DIR, f"{person_name}_processed")
    
    if not os.path.exists(output_dir):
        print("No processed images found. Run option 2 first.")
        return
    
    images = [f for f in os.listdir(output_dir) if f.endswith('.jpg')]
    
    if not images:
        print("No images found")
        return
    
    print(f"\nShowing {len(images)} images (any key = next, Q = quit)\n")
    
    for img_file in images:
        img_path = os.path.join(output_dir, img_file)
        img = cv2.imread(img_path)
        
        if img is not None:
            cv2.imshow(f'Result: {img_file}', img)
            key = cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            if key == ord('q') or key == ord('Q'):
                break

# ==================== MAIN ====================

def main():
    print("\n" + "="*50)
    print("   FACE DETECTION SYSTEM")
    print("="*50)
    
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    while True:
        print("\n1. Capture face images")
        print("2. Process images with face detection")
        print("3. Display processed results")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            name = input("Enter person name: ").strip()
            if name:
                capture_faces(name)
            else:
                print("Invalid name")
        
        elif choice == '2':
            name = input("Enter person name: ").strip()
            if name:
                process_images(name)
            else:
                print("Invalid name")
        
        elif choice == '3':
            name = input("Enter person name: ").strip()
            if name:
                display_results(name)
            else:
                print("Invalid name")
        
        elif choice == '4':
            print("\nGoodbye!\n")
            break
        
        else:
            print("Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()