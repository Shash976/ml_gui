from cv2 import VideoCapture, imdecode
import numpy as np
from sys import platform
import subprocess
import os

def getFrame(gif_path):
    gif = VideoCapture(gif_path)
    frames = []
    ret, frame = gif.read()
    while ret:
        ret, frame = gif.read()
        if not ret:
            break
        frames.append(frame)
    frames = np.array(frames)
    maxFrame = np.max(frames, axis=0)
    return maxFrame
def is_float(x):
    try:
        n = float(x)
        return True
    except Exception as e:
        return False
    
def crop_image(image_array: np.ndarray, crop_cords: dict, pad=10):
    """Crops the image given by its coordinates.

    Args:
        image_array: Image in array form
        crop_cords: Coordinaties of minimum and maximum points of the image
        pad: Padding required (Extra image data to be left out) Default value is 10
    
    Returns:
        cropped_image: Image cropped
    """
    # Handle corner cases where the crop region is outside of the image bounds.
    min_y = max(crop_cords["Min-Y"] - pad, 0)
    max_y = min(crop_cords["Max-Y"] + pad, image_array.shape[0])

    min_x = max(crop_cords["Min-X"] - pad, 0)
    max_x = min(crop_cords["Max-X"] + pad, image_array.shape[1])

    # Crop the image array.
    return image_array[min_y:max_y, min_x:max_x]

def get_image_array(image):
    return getFrame(image) if isinstance(image, str) and image.endswith(".gif") else imdecode(np.fromfile(image, dtype=np.uint8), -1) if isinstance(image, str) else image

def open_window(path):
    if any([platform.startswith(system) for system in ["os","darwin","linux"]]):
        subprocess.call(["open", path])
    elif "win" in platform:
        os.startfile(path)