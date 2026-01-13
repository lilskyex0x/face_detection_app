import sys
import cv2
import pickle
import os
import csv
from datetime import datetime

import face_recognition
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel,
    QPushButton, QVBoxLayout, QWidget,
    QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap


# ---------------- CONFIG ----------------

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

ENCODINGS_PATH = resource_path("encodings/face_encodings.pickle")
ATTENDANCE_DIR = resource_path("attendance")

CAMERA_INDEX = 0
RESIZE_SCALE = 0.5
DISPLAY_WIDTH = 960
DISPLAY_HEIGHT = 540

FRAME_SKIP = 5   # 🔴 CRITICAL for macOS stability

os.makedirs(ATTENDANCE_DIR, exist_ok=True)
today = datetime.now().strftime("%Y-%m-%d")
attendance_file = os.path.join(
    ATTENDANCE_DIR, f"attendance_{today}.csv"
)

# ---------------------------------------


class FaceAttendanceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Attendance System")
        self.resize(1000, 750)

        # Load encodings
        with open(ENCODINGS_PATH, "rb") as f:
            data = pickle.load(f)
        self.known_encodings = data["encodings"]
        self.known_names = data["names"]

        self.marked_names = set()
        self.frame_count = 0

        # ---------- UI ----------
        self.video_label = QLabel()
        self.video_label.setFixedSize(DISPLAY_WIDTH, DISPLAY_HEIGHT)
        self.video_label.setStyleSheet("background-color: black;")

        self.status_label = QLabel("Status: Idle")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px;")

        self.start_btn = QPushButton("Start Camera")
        self.start_btn.clicked.connect(self.start_camera)

        self.stop_btn = QPushButton("Stop Camera")
        self.stop_btn.clicked.connect(self.stop_camera)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Date", "Time"]
        )

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # ---------- Camera ----------
        self.cap = None
        self.running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    # ---------- CAMERA CONTROL ----------
    def start_camera(self):
        if self.running:
            return

        self.status_label.setText("Status: Opening camera...")

        self.cap = cv2.VideoCapture(
            CAMERA_INDEX,
            cv2.CAP_AVFOUNDATION
        )

        if not self.cap.isOpened():
            self.status_label.setText("Status: Camera access denied")
            self.cap = None
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.running = True
        self.frame_count = 0
        self.timer.start(30)

        self.status_label.setText("Status: Camera running")

    def stop_camera(self):
        self.timer.stop()
        self.running = False

        if self.cap:
            self.cap.release()
            self.cap = None

        self.video_label.clear()
        self.status_label.setText("Status: Camera stopped")

    # ---------- MAIN LOOP ----------
    def update_frame(self):
        if not self.running or self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.stop_camera()
            return

        self.frame_count += 1

        # 🔴 Only run face recognition every N frames
        if self.frame_count % FRAME_SKIP == 0:
            small = cv2.resize(
                frame, (0, 0),
                fx=RESIZE_SCALE,
                fy=RESIZE_SCALE
            )

            rgb_small = cv2.cvtColor(
                small, cv2.COLOR_BGR2RGB
            )

            locations = face_recognition.face_locations(rgb_small)
            encodings = face_recognition.face_encodings(
                rgb_small, locations
            )

            for enc, (top, right, bottom, left) in zip(encodings, locations):
                matches = face_recognition.compare_faces(
                    self.known_encodings, enc
                )

                name = "Unknown"

                if True in matches:
                    idx = matches.index(True)
                    name = self.known_names[idx]

                    if name not in self.marked_names:
                        self.mark_attendance(name)
                        self.marked_names.add(name)

                # Scale back
                top = int(top / RESIZE_SCALE)
                right = int(right / RESIZE_SCALE)
                bottom = int(bottom / RESIZE_SCALE)
                left = int(left / RESIZE_SCALE)

                cv2.rectangle(
                    frame, (left, top),
                    (right, bottom), (0, 255, 0), 2
                )

                cv2.putText(
                    frame, name,
                    (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0), 2
                )

        self.display_frame(frame)

    # ---------- DISPLAY ----------
    def display_frame(self, frame):
        frame = cv2.resize(
            frame,
            (DISPLAY_WIDTH, DISPLAY_HEIGHT),
            interpolation=cv2.INTER_LINEAR
        )

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape

        img = QImage(
            rgb.data,
            w,
            h,
            ch * w,
            QImage.Format_RGB888
        )

        self.video_label.setPixmap(
            QPixmap.fromImage(img)
        )

    # ---------- ATTENDANCE ----------
    def mark_attendance(self, name):
        now = datetime.now()
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(today))
        self.table.setItem(
            row, 2,
            QTableWidgetItem(now.strftime("%H:%M:%S"))
        )

        write_header = not os.path.exists(attendance_file)
        with open(attendance_file, "a", newline="") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["Name", "Date", "Time"])
            writer.writerow(
                [name, today, now.strftime("%H:%M:%S")]
            )


# ---------- RUN ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceAttendanceApp()
    window.show()
    sys.exit(app.exec_())
