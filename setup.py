from setuptools import setup
import cv2
import os

opencv_data = cv2.data.haarcascades
haar_file = os.path.join(opencv_data, 'haarcascade_frontalface_default.xml')

APP = ['face_dataset_gui.py']
DATA_FILES = [
    ('haarcascades', [haar_file]),
]
OPTIONS = {
    'argv_emulation': False,
    'packages': ['numpy', 'cv2', 'tkinter'],
    'includes': ['cv2', 'tkinter'],
    'plist': {
        'CFBundleName': 'Face Detection',
        'NSCameraUsageDescription': 'This app needs camera access for face detection',
        'LSApplicationCategoryType': 'public.app-category.utilities',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)