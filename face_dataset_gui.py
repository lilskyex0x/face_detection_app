import cv2
import os
import time
import tkinter as tk
from tkinter import messagebox
import sys

# Configuration
if getattr(sys, 'frozen', False):
    project_dir = os.path.expanduser("~/PycharmProjects/face_detection_project")
    DATASET_DIR = os.path.join(project_dir, "face_dataset")
else:
    DATASET_DIR = os.path.join(os.path.dirname(__file__), "face_dataset")

TOTAL_IMAGES = 20
CAPTURE_INTERVAL = 1


class CameraSelectionDialog:
    """Dialog to select which camera to use"""

    def __init__(self, parent, available_cameras):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Camera")
        self.dialog.geometry("400x300")

        # Make dialog modal and bring to front
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.lift()
        self.dialog.focus_force()

        # Prompt label
        label = tk.Label(self.dialog, text="Select which camera to use:",
                         font=("Arial", 12, "bold"))
        label.pack(pady=20)

        # Camera selection variable
        self.selected = tk.IntVar(value=available_cameras[0] if available_cameras else 0)

        # Radio buttons for each camera
        for idx in available_cameras:
            rb = tk.Radiobutton(self.dialog,
                                text=f"Camera {idx} (Built-in)" if idx == 0 else f"Camera {idx} (External/iPhone)",
                                variable=self.selected,
                                value=idx,
                                font=("Arial", 11))
            rb.pack(pady=5, anchor=tk.W, padx=50)

        # Buttons frame
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=20)

        ok_btn = tk.Button(btn_frame, text="Use This Camera", command=self.on_ok,
                           width=15, bg="#4CAF50", fg="white", font=("Arial", 11))
        ok_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(btn_frame, text="Cancel", command=self.on_cancel,
                               width=10, font=("Arial", 11))
        cancel_btn.pack(side=tk.LEFT, padx=5)

        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

        # Wait for dialog to close
        parent.wait_window(self.dialog)

    def on_ok(self):
        self.result = self.selected.get()
        self.dialog.destroy()

    def on_cancel(self):
        self.result = None
        self.dialog.destroy()


class NameDialog:
    """Custom dialog for name input that works on macOS"""

    def __init__(self, parent, title, prompt):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)

        # Try to force light appearance on macOS
        try:
            # This works on macOS to override dark mode
            self.dialog.tk.call('tk', 'useinputmethods', '-displayof', self.dialog, True)
        except:
            pass

        # Larger window for better visibility
        self.dialog.geometry("450x220")
        self.dialog.minsize(450, 220)

        # Set light background
        self.dialog.configure(bg='white')

        # Make dialog modal and bring to front
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.lift()
        self.dialog.focus_force()

        # Add some padding at top
        top_spacer = tk.Frame(self.dialog, bg='white', height=30)
        top_spacer.pack()

        # Prompt label with better styling
        label = tk.Label(self.dialog, text=prompt,
                         font=("Helvetica", 14, "bold"),
                         bg='white', fg='#333333')
        label.pack(pady=15)

        # Container frame for entry
        entry_container = tk.Frame(self.dialog, bg='white')
        entry_container.pack(pady=10, padx=40, fill=tk.X)

        # Create a visible border frame
        border_frame = tk.Frame(entry_container,
                                bg='#2196F3',  # Blue border
                                bd=0,
                                highlightthickness=2,
                                highlightbackground='#2196F3',
                                highlightcolor='#2196F3')
        border_frame.pack(fill=tk.BOTH, expand=True)

        # Entry field with maximum visibility settings
        self.entry = tk.Entry(border_frame,
                              font=("Helvetica", 15),
                              bg='#FFFFFF',  # White background
                              fg='#000000',  # Black text
                              insertbackground='#2196F3',  # Blue cursor
                              selectbackground='#2196F3',  # Selection color
                              selectforeground='#FFFFFF',  # Selected text color
                              relief=tk.FLAT,
                              bd=8)
        self.entry.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Add placeholder behavior
        self.entry.insert(0, "Type name here...")
        self.entry.config(fg='#999999')

        def on_focus_in(event):
            if self.entry.get() == "Type name here...":
                self.entry.delete(0, tk.END)
                self.entry.config(fg='#000000')

        def on_focus_out(event):
            if not self.entry.get():
                self.entry.insert(0, "Type name here...")
                self.entry.config(fg='#999999')

        self.entry.bind('<FocusIn>', on_focus_in)
        self.entry.bind('<FocusOut>', on_focus_out)
        self.entry.bind('<Return>', lambda e: self.on_ok())

        # Buttons frame
        btn_frame = tk.Frame(self.dialog, bg='white')
        btn_frame.pack(pady=20)

        # Styled buttons
        ok_btn = tk.Button(btn_frame, text="✓ OK", command=self.on_ok,
                           width=15, height=2,
                           bg="#4CAF50", fg="white",
                           font=("Helvetica", 13, "bold"),
                           activebackground="#45a049",
                           activeforeground="white",
                           relief=tk.FLAT,
                           cursor="hand2")
        ok_btn.pack(side=tk.LEFT, padx=8)

        cancel_btn = tk.Button(btn_frame, text="✕ Cancel", command=self.on_cancel,
                               width=15, height=2,
                               bg="#f44336", fg="white",
                               font=("Helvetica", 13, "bold"),
                               activebackground="#da190b",
                               activeforeground="white",
                               relief=tk.FLAT,
                               cursor="hand2")
        cancel_btn.pack(side=tk.LEFT, padx=8)

        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

        # Delayed focus to ensure entry is ready
        self.dialog.after(100, lambda: self.entry.focus_set())
        self.dialog.after(150, lambda: self.entry.icursor(tk.END))

        # Wait for dialog to close
        parent.wait_window(self.dialog)

    def on_ok(self):
        text = self.entry.get()
        # Remove placeholder text if present
        if text == "Type name here...":
            self.result = ""
        else:
            self.result = text
        self.dialog.destroy()

    def on_cancel(self):
        self.result = None
        self.dialog.destroy()


class FaceDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Detection System")
        self.root.geometry("400x350")

        # Bring window to front
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)

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

        # Add test camera button
        btn_test = tk.Button(root, text="TEST CAMERA (Debug)",
                             command=self.test_camera, width=30, height=2,
                             bg="yellow")
        btn_test.pack(pady=10)

        btn4 = tk.Button(root, text="4. Exit",
                         command=root.quit, width=30, height=2)
        btn4.pack(pady=10)

        os.makedirs(DATASET_DIR, exist_ok=True)

        print("\n" + "=" * 50)
        print("FACE DETECTION SYSTEM STARTED")
        print("=" * 50)
        print(f"Dataset directory: {DATASET_DIR}")
        print(f"OpenCV version: {cv2.__version__}")
        print("=" * 50 + "\n")

    def test_camera(self):
        """Test camera connectivity - DEBUG FUNCTION"""
        print("\n" + "=" * 50)
        print("TESTING CAMERA CONNECTIVITY")
        print("=" * 50)

        found_cameras = []
        camera_info = []

        for camera_index in range(5):  # Test indices 0-4
            print(f"\nTrying camera index {camera_index}...")
            cap = cv2.VideoCapture(camera_index)

            if cap.isOpened():
                print(f"  ✓ Camera index {camera_index} opened")

                # Try to read a frame
                time.sleep(0.5)
                ret, frame = cap.read()

                if ret and frame is not None:
                    print(f"  ✓ Successfully read frame from camera {camera_index}")
                    print(f"  Frame shape: {frame.shape}")
                    found_cameras.append(camera_index)

                    # Determine camera type
                    if camera_index == 0:
                        cam_type = "Built-in MacBook Camera"
                    else:
                        cam_type = "External/iPhone Camera (Continuity)"

                    camera_info.append(f"Camera {camera_index}: {cam_type}")

                    # Show a test window
                    cv2.imshow(f'Camera {camera_index} - {cam_type}', frame)
                    cv2.waitKey(1500)  # Show for 1.5 seconds
                    cv2.destroyAllWindows()
                    for _ in range(5):
                        cv2.waitKey(1)
                else:
                    print(f"  ✗ Camera {camera_index} opened but couldn't read frame")

                cap.release()
            else:
                print(f"  ✗ Could not open camera index {camera_index}")

        print("\n" + "=" * 50)
        if found_cameras:
            info_msg = (
                    f"✓ Found {len(found_cameras)} working camera(s)!\n\n" +
                    "\n".join(camera_info) +
                    "\n\nCamera 0 is usually your built-in MacBook camera.\n"
                    "Higher indices are external cameras or iPhone (Continuity Camera)."
            )
            messagebox.showinfo("Camera Test Results", info_msg)
            print(f"Found cameras: {found_cameras}")
        else:
            messagebox.showerror("Camera Test Failed",
                                 "✗ No working camera found!\n\n"
                                 "Possible issues:\n"
                                 "1. Camera permissions not granted\n"
                                 "2. Another app is using the camera\n"
                                 "3. Camera driver issues\n\n"
                                 "Check System Preferences → Security & Privacy → Camera")
        print("=" * 50 + "\n")

    def capture_menu(self):
        print("\n" + ">" * 50)
        print("CAPTURE FACE IMAGES")
        print(">" * 50)
        print("\n>>> Please enter the person's name in the TERMINAL/CONSOLE window")
        print(">>> (Look for the window where you started this program)\n")

        # Get input from terminal instead of GUI
        try:
            name = input("Enter person name: ").strip()
            print(f"\n>>> You entered: '{name}'")
        except Exception as e:
            print(f">>> ERROR getting input: {e}")
            messagebox.showerror("Error", "Failed to get input. Please check the terminal/console window.")
            return

        if name:
            print(f">>> Starting capture for: {name}")
            # Hide the main window during capture
            self.root.withdraw()
            print(">>> Main window hidden, starting capture...")

            try:
                self.capture_faces(name)
                print(">>> Capture completed!")
            except Exception as e:
                print(f">>> ERROR in capture_faces: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            finally:
                print(">>> Showing main window again...")
                self.root.deiconify()
                self.root.lift()
        else:
            print(">>> No name entered")
            messagebox.showwarning("Warning", "Please enter a name!")

        print(">" * 50)
        print("CAPTURE MENU COMPLETE")
        print(">" * 50 + "\n")

    def process_menu(self):
        print("\n>>> Please enter the person's name in the TERMINAL/CONSOLE window\n")
        try:
            name = input("Enter person name to process: ").strip()
        except Exception as e:
            messagebox.showerror("Error", "Failed to get input. Check terminal.")
            return

        if name:
            self.process_images(name)
        else:
            messagebox.showwarning("Warning", "Please enter a name!")

    def display_menu(self):
        print("\n>>> Please enter the person's name in the TERMINAL/CONSOLE window\n")
        try:
            name = input("Enter person name to display: ").strip()
        except Exception as e:
            messagebox.showerror("Error", "Failed to get input. Check terminal.")
            return

        if name:
            self.display_results(name)
        else:
            messagebox.showwarning("Warning", "Please enter a name!")

    def capture_faces(self, person_name):
        print(f"\n{'=' * 50}")
        print(f"CAPTURING FACES FOR: {person_name}")
        print(f"{'=' * 50}\n")

        # Load face detector
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        print(f"Loading cascade from: {cascade_path}")

        face_cascade = cv2.CascadeClassifier(cascade_path)

        if face_cascade.empty():
            error_msg = "Could not load face cascade classifier"
            print(f"ERROR: {error_msg}")
            messagebox.showerror("Error", error_msg)
            return

        print("✓ Face cascade loaded successfully\n")

        # First, detect all available cameras
        print("Detecting available cameras...")
        available_cameras = []
        for camera_index in [0, 1, 2, 3, 4]:
            test_cap = cv2.VideoCapture(camera_index)
            if test_cap.isOpened():
                time.sleep(0.3)
                ret, _ = test_cap.read()
                if ret:
                    available_cameras.append(camera_index)
                    print(f"  ✓ Camera {camera_index} available")
            test_cap.release()

        if not available_cameras:
            error_msg = "No cameras detected!"
            print(f"ERROR: {error_msg}")
            messagebox.showerror("Camera Error", error_msg)
            return

        print(f"\nFound {len(available_cameras)} camera(s): {available_cameras}")

        # If multiple cameras, let user choose
        selected_camera = None
        if len(available_cameras) > 1:
            print("Multiple cameras detected - showing selection dialog...")
            camera_dialog = CameraSelectionDialog(self.root, available_cameras)
            selected_camera = camera_dialog.result

            if selected_camera is None:
                print("User cancelled camera selection")
                return
        else:
            selected_camera = available_cameras[0]

        print(f"\nUsing camera index: {selected_camera}")

        # Open selected camera
        cap = cv2.VideoCapture(selected_camera)

        if not cap.isOpened():
            error_msg = f"Failed to open camera {selected_camera}"
            print(f"ERROR: {error_msg}")
            messagebox.showerror("Camera Error", error_msg)
            return

        time.sleep(0.5)
        ret, test_frame = cap.read()
        if not ret:
            error_msg = f"Camera {selected_camera} opened but cannot read frames"
            print(f"ERROR: {error_msg}")
            cap.release()
            messagebox.showerror("Camera Error", error_msg)
            return

        print(f"✓ Camera {selected_camera} opened successfully!")

        # Create folder
        person_dir = os.path.join(DATASET_DIR, person_name)
        os.makedirs(person_dir, exist_ok=True)
        print(f"Saving images to: {person_dir}\n")

        # Warm up camera
        print("Warming up camera...")
        for i in range(30):
            cap.read()
            if i % 10 == 0:
                print(f"  Warming up... {i}/30")
            time.sleep(0.05)

        print("\n✓ Camera ready!")
        print("✓ Opening camera window...\n")
        print("Instructions:")
        print("  - Position your face in the frame")
        print("  - Camera will capture 10 images automatically")
        print("  - Press 'Q' to quit early\n")

        images_captured = 0
        last_capture_time = 0
        start_time = time.time()

        window_name = 'Face Capture - Press Q to quit'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        frame_count = 0
        while images_captured < TOTAL_IMAGES:
            ret, frame = cap.read()
            frame_count += 1

            if not ret or frame is None:
                print(f"WARNING: Failed to read frame {frame_count}")
                continue

            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            # Draw rectangles
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "Face Detected", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Status display
            status_text = f"Captured: {images_captured}/{TOTAL_IMAGES}"
            cv2.putText(frame, status_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            if len(faces) == 0:
                cv2.putText(frame, "No face detected",
                            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

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
                    print(f"✓ Captured image {images_captured}/{TOTAL_IMAGES} - saved as {filename}")
                else:
                    print(f"⚠ No face detected at frame {frame_count} - waiting...")
                last_capture_time = current_time

            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("\n>>> User pressed Q - cancelling capture")
                break

            # Timeout after 60 seconds
            if time.time() - start_time > 60:
                print("\n>>> Timeout (60 seconds) reached")
                break

        print("\nCleaning up camera...")
        cap.release()
        cv2.destroyAllWindows()

        # Multiple waitKey calls to ensure window closes on macOS
        for _ in range(10):
            cv2.waitKey(1)

        print(f"\n{'=' * 50}")
        if images_captured > 0:
            success_msg = (
                f"✓ Success!\n\n"
                f"Captured {images_captured} images\n\n"
                f"Saved to:\n{person_dir}/"
            )
            messagebox.showinfo("Capture Complete", success_msg)
            print(f"✓ CAPTURE COMPLETE: {images_captured} images saved")
        else:
            warning_msg = "No images were captured.\n\nPlease try again."
            messagebox.showwarning("Warning", warning_msg)
            print("⚠ WARNING: No images captured")
        print(f"{'=' * 50}\n")

    def process_images(self, person_name):
        print(f"\n=== Processing images for: {person_name} ===\n")

        person_dir = os.path.join(DATASET_DIR, person_name)

        if not os.path.exists(person_dir):
            messagebox.showerror("Error",
                                 f"No folder found for '{person_name}'\n\n"
                                 f"Please capture images first (Option 1)")
            return

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        images = [f for f in os.listdir(person_dir) if f.endswith('.jpg')]

        if not images:
            messagebox.showwarning("Warning",
                                   f"No images found in {person_name} folder")
            return

        output_dir = os.path.join(DATASET_DIR, f"{person_name}_processed")
        os.makedirs(output_dir, exist_ok=True)

        print(f"Processing {len(images)} images...\n")
        total_faces = 0

        for img_file in images:
            img_path = os.path.join(person_dir, img_file)
            img = cv2.imread(img_path)

            if img is None:
                print(f"⚠ Could not read {img_file}")
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
            print(f"✓ Processed {img_file} - found {len(faces)} face(s)")

        messagebox.showinfo("Complete",
                            f"✓ Processing complete!\n\n"
                            f"Detected {total_faces} faces in {len(images)} images\n\n"
                            f"Saved in: {output_dir}/")
        print(f"\n✓ Done! Detected {total_faces} faces total\n")

    def display_results(self, person_name):
        output_dir = os.path.join(DATASET_DIR, f"{person_name}_processed")

        if not os.path.exists(output_dir):
            messagebox.showwarning("Warning",
                                   f"No processed images found for '{person_name}'.\n\n"
                                   f"Please run option 2 (Process Images) first.")
            return

        images = [f for f in os.listdir(output_dir) if f.endswith('.jpg')]

        if not images:
            messagebox.showwarning("Warning", "No images found in processed folder")
            return

        print(f"\nShowing {len(images)} processed images")
        print("Press any key to see next image, Q to quit\n")

        for i, img_file in enumerate(images, 1):
            img_path = os.path.join(output_dir, img_file)
            img = cv2.imread(img_path)

            if img is not None:
                display_img = img.copy()
                cv2.putText(display_img, f"Image {i}/{len(images)}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

                window_name = f'Result: {img_file}'
                cv2.imshow(window_name, display_img)
                print(f"Showing {i}/{len(images)}: {img_file}")

                key = cv2.waitKey(0)
                cv2.destroyAllWindows()

                for _ in range(5):
                    cv2.waitKey(1)

                if key == ord('q') or key == ord('Q'):
                    print("Display cancelled by user")
                    break

        print("✓ Display complete\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceDetectionApp(root)
    root.mainloop()