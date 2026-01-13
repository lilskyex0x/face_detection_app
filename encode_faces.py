import os
import cv2
import face_recognition
import pickle

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "face_dataset")
ENCODINGS_DIR = os.path.join(BASE_DIR, "encodings")
ENCODINGS_FILE = os.path.join(ENCODINGS_DIR, "face_encodings.pickle")

os.makedirs(ENCODINGS_DIR, exist_ok=True)

# -----------------------------
# Storage
# -----------------------------
known_encodings = []
known_names = []

print("[INFO] Starting face encoding process...")

# -----------------------------
# Loop through each person
# -----------------------------
for person_name in os.listdir(DATASET_DIR):
    person_path = os.path.join(DATASET_DIR, person_name)

    if not os.path.isdir(person_path):
        continue

    print(f"[INFO] Processing person: {person_name}")

    for image_name in os.listdir(person_path):
        image_path = os.path.join(person_path, image_name)

        # Load image
        image = cv2.imread(image_path)
        if image is None:
            continue

        # Convert BGR to RGB
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect face locations
        boxes = face_recognition.face_locations(rgb, model="hog")

        # Enforce one-face-per-image rule
        if len(boxes) != 1:
            continue

        # Compute encoding
        encoding = face_recognition.face_encodings(rgb, boxes)[0]

        known_encodings.append(encoding)
        known_names.append(person_name)

print("[INFO] Encoding complete")
print(f"[INFO] Total encodings: {len(known_encodings)}")

# -----------------------------
# Save encodings
# -----------------------------
data = {
    "encodings": known_encodings,
    "names": known_names
}

with open(ENCODINGS_FILE, "wb") as f:
    pickle.dump(data, f)

print(f"[INFO] Encodings saved to: {ENCODINGS_FILE}")
