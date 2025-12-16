# Face Detection System

A desktop application for capturing, processing, and analyzing facial images using OpenCV and Python.

## Features

- **Face Capture**: Automatically detect and capture face images from webcam
- **Image Processing**: Process captured images with face detection overlay
- **Results Display**: View processed images with detected faces highlighted
- **User-friendly GUI**: Simple Tkinter-based interface for easy navigation

## Requirements

- Python 3.x
- OpenCV (cv2)
- NumPy
- Tkinter (usually comes with Python)
- py2app (for Mac app packaging)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/lilskyex0x/face_detection_app.git
cd face_detection_app
```

2. Install required packages:
```bash
pip3 install opencv-python numpy py2app
```

## Usage

### Running as Python Script

**Terminal Version:**
```bash
python3 face_dataset.py
```

**GUI Version:**
```bash
python3 face_dataset_gui.py
```

### Running as Mac Application

1. Build the app:
```bash
python3 setup.py py2app
```

2. The app will be created in the `dist/` folder
3. Double-click `Face Detection.app` to run

## How to Use

1. **Capture Face Images**
   - Enter a person's name
   - Position yourself in front of the camera
   - The system will automatically capture 10 face images
   - Press 'Q' to quit early if needed

2. **Process Images**
   - Enter the same person's name
   - The system will detect faces and add green rectangles with labels
   - Processed images are saved in a separate folder

3. **Display Results**
   - Enter the person's name to view processed images
   - Press any key to view the next image
   - Press 'Q' to quit viewing

## Project Structure
```
face_detection_project/
├── face_dataset.py          # Original terminal-based script
├── face_dataset_gui.py      # GUI version with Tkinter
├── setup.py                 # py2app configuration
├── face_dataset/            # Captured and processed images
│   ├── person_name/         # Raw captured images
│   └── person_name_processed/  # Processed images with detection
├── build/                   # Build artifacts (ignored)
└── dist/                    # Compiled app (ignored)
```

## Configuration

You can modify these settings in the script:

- `TOTAL_IMAGES`: Number of images to capture (default: 10)
- `CAPTURE_INTERVAL`: Time between captures in seconds (default: 1)
- `DATASET_DIR`: Directory where images are saved

## Camera Permissions

On macOS, you need to grant camera access:
1. Go to **System Settings → Privacy & Security → Camera**
2. Enable access for the Face Detection app or Terminal

## Troubleshooting

**Camera won't open:**
- Check camera permissions in System Settings
- Close other apps using the camera (FaceTime, Zoom, etc.)
- Try different camera indices in the code (0, 1, or 2)

**Images not saving:**
- Check file permissions in the project directory
- Ensure the `face_dataset` folder exists

**App won't build:**
- Make sure all dependencies are installed
- Try: `pip3 install --upgrade py2app setuptools`

## Technologies Used

- **OpenCV**: Face detection using Haar Cascades
- **Python**: Core programming language
- **Tkinter**: GUI framework
- **py2app**: Mac application packaging

## License

MIT License - feel free to use and modify for your projects

## Author

Aung Pyae Khant

## Acknowledgments

- OpenCV for the Haar Cascade face detection model
- Python community for excellent libraries