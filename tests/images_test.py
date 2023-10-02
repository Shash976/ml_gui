import os
to_check = [os.path.join(r"C:\Users\shash\Downloads\ITO-SE-ECL 1µM-10mM\0.09 mM", p) for p in os.listdir(r"C:\Users\shash\Downloads\ITO-SE-ECL 1µM-10mM\0.09 mM") if p.endswith((".jpg",".png",".jpeg"))]
import cv2, numpy as np

def calculateMean(image, hsv_image, lightness, min_pix=10000):
    min_range, max_range = [np.array([110,170, lightness]), np.array([130, 255,255])]
    mask = cv2.inRange(hsv_image, min_range, max_range)
    required_pixels = image[mask==255]
    mean = 0
    crop_cords = {}
    for required_size in range(10000, 4500, -250):
        if required_pixels.size >= required_size:
            mean = np.mean(required_pixels)
            y_cords, x_cords = np.where(mask==255)
            crop_cords["Max-X"] = np.max(x_cords)
            crop_cords["Max-Y"] = np.max(y_cords)
            crop_cords["Min-X"] = np.min(x_cords)
            crop_cords["Min-Y"] = np.min(y_cords)
            break
    return mean, required_pixels.size, crop_cords

further_testing = {}

for image_path in to_check:
    image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    hsv_image = cv2.cvtColor(image, 40)
    lightness_ranges = [210, 175,170, 160,140,80,55, 40, 20, 10]
    r = 0
    mean = 0
    area = 0
    while mean == 0 and r < len(lightness_ranges):
        mean, area, crop_cords = calculateMean(image, hsv_image,  lightness_ranges[r])
        r += 1
    if type(mean) not in [int,float, np.float16, np.float64] or mean == 0:
        further_testing[image_path] = [type(mean), mean]
    else:
        print(image_path, " -> ",mean)

print(further_testing)
            
