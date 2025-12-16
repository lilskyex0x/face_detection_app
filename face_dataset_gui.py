import cv2
import os
import time
import tkinter as tk
from tkinter import simpledialog, messagebox
import sys

# Configuration
# Always save to the project's face_dataset folder
if getattr(sys, 'frozen', False):
    # Running as compiled app - use the project folder
    project_dir = os.path.expanduser("~/PycharmProjects/face_detection_project")
    DATASET_DIR = os.path.join(project_dir, "face_dataset")
else:
    # Running as script
    DATASET_DIR = os.path.join(os.path.dirname(__file__), "face_dataset")

TOTAL_IMAGES = 10
CAPTURE_INTERVAL = 1


class FaceDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Detection System")
        self.root.geometry("400x300")

        # Title
        title = tk.Label(root, text="FACE DETECTION SYSTEM",
                         font=("Arial", 16, "bold"))
        title.pack(pady=20)

        # Buttons
        btn1 = tk.Button(root, text="1. Capture Face Images",
                         command=self.capture_menu, width=30, height=2)
        btn1.pack(pady=10)

        btn2 = tk.Button(root, text="2. Process Images",
                         command=self.process_menu, width=30, height=2)
        btn2.pack(pady=10)

        btn3 = tk.Button(root, text="3. Display Results",
                         command=self.display_menu, width=30, height=2)
        btn3.pack(pady=10)

        btn4 = tk.Button(root, text="4. Exit",
                         command=root.quit, width=30, height=2)
        btn4.pack(pady=10)

        os.makedirs(DATASET_DIR, exist_ok=True)

    def capture_menu(self):
        name = simpledialog.askstring("Input", "Enter person name:")
        if name:
            # Hide the main window during capture
            self.root.withdraw()
            self.capture_faces(name)
            # Show the main window again
            self.root.deiconify()

    def process_menu(self):
        name = simpledialog.askstring("Input", "Enter person name:")
        if name:
            self.process_images(name)

    def display_menu(self):
        name = simpledialog.askstring("Input", "Enter person name:")
        if name:
            self.display_results(name)

    def capture_faces(self, person_name):
        print(f"\n=== Capturing faces for: {person_name} ===\n")

        # Load face detector
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Try different camera indices
        cap = None
        for camera_index in [1, 0, 2]:
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                print(f"Camera opened on index {camera_index}")
                break
            cap.release()

        if not cap or not cap.isOpened():
            messagebox.showerror("Error", "Cannot open camera")
            return

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

        window_name = 'Camera - Press Q to quit'

        while images_captured < TOTAL_IMAGES:
            ret, frame = cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            # Draw rectangles
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Preview
            cv2.putText(frame, f"Captured: {images_captured}/{TOTAL_IMAGES}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow(window_name, frame)

            # Save every second
            current_time = time.time()
            if current_time - last_capture_time >= CAPTURE_INTERVAL:
                if len(faces) > 0:
                    (x, y, w, h) = faces[0]
                    face_crop = frame[y:y + h, x:x + w]
                    filename = f"{person_name}_{images_captured + 1}.jpg"
                    filepath = os.path.join(person_dir, filename)
                    cv2.imwrite(filepath, face_crop)
                    images_captured += 1
                    print(f"✓ Saved face {images_captured}/{TOTAL_IMAGES}")
                else:
                    print("No face detected — skipping frame.")
                last_capture_time = current_time

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if time.time() - start_time > 30:
                break

        cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)  # Extra waitKey to ensure window closes

        messagebox.showinfo("Complete",
                            f"{images_captured} images saved in: {person_dir}/")
        print(f"\n✓ Complete! {images_captured} images saved\n")

    def process_images(self, person_name):
        print(f"\n=== Processing images for: {person_name} ===\n")

        person_dir = os.path.join(DATASET_DIR, person_name)

        if not os.path.exists(person_dir):
            messagebox.showerror("Error", f"No folder found for {person_name}")
            return

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        images = [f for f in os.listdir(person_dir) if f.endswith('.jpg')]

        if not images:
            messagebox.showwarning("Warning", "No images found")
            return

        output_dir = os.path.join(DATASET_DIR, f"{person_name}_processed")
        os.makedirs(output_dir, exist_ok=True)

        print(f"Processing {len(images)} images...\n")
        total_faces = 0

        for img_file in images:
            img_path = os.path.join(person_dir, img_file)
            img = cv2.imread(img_path)

            if img is None:
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img, person_name, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                total_faces += 1

            output_path = os.path.join(output_dir, f"processed_{img_file}")
            cv2.imwrite(output_path, img)

        messagebox.showinfo("Complete",
                            f"Detected {total_faces} faces\nSaved in: {output_dir}/")
        print(f"✓ Done! Detected {total_faces} faces\n")

    def display_results(self, person_name):
        output_dir = os.path.join(DATASET_DIR, f"{person_name}_processed")

        if not os.path.exists(output_dir):
            messagebox.showwarning("Warning",
                                   "No processed images found. Run option 2 first.")
            return

        images = [f for f in os.listdir(output_dir) if f.endswith('.jpg')]

        if not images:
            messagebox.showwarning("Warning", "No images found")
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


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceDetectionApp(root)
    root.mainloop()