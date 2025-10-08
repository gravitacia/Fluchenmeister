import cv2
import io
from PIL import Image

def get_camera_image_bytes():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None

    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)

    camera = io.BytesIO()
    img.save(camera, format='PNG')
    camera.seek(0)
    return camera
