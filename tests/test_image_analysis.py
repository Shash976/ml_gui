import cv2
import numpy as np
import os

folder_path = r"C:\Users\shash\Downloads\ITO SE ECL\ITO SE ECL\H2O2"
images = [os.path.join(folder_path, subfolder_path, image) for subfolder_path in os.listdir(folder_path) for image in os.listdir(os.path.join(folder_path, subfolder_path)) if image.endswith((".png",'.jpg','.jpeg'))]
for image_path in images:
    image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

def getMean(image_path, concentration):
    pass