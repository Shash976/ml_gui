from cv2 import imread, cvtColor, inRange
from processing import makeExcel, os, np, pd
from multiprocessing import Pool

y = "Concentration"
x = "Intensity"
data = pd.DataFrame(columns=[y, x])
VAL_RANGES = [210, 175,170, 160,140,80,55, 40]

def processFolder(folder_path):
    paths = [os.path.join(folder_path, path) for path in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, path))]
    for path in paths:
        try:
            concentration = float(os.path.split(path)[-1].split(" ")[0])
            for image_path in [os.path.join(path, image) for image in os.listdir(path) if image.endswith((".jpg", ".jpeg", ".png"))]:
                mean, min_lightness = getMean(image_path, concentration)
                data["Intensity"].append(concentration)
                data["Concentration"].append(mean)
        except Exception as e:
            continue
    makeExcel(os.path.join(folder_path, "data.xlsx"), data, "Intensity")

def getMean(image_path, concentration):
    image = imread(image_path)
    print(f"Working with {image_path}")
    mean = 0
    hsv_img = cvtColor(image, 40)  # Use cv2.COLOR_BGR2HSV instead of 40
    val_ranges = [210, 175, 170, 160, 140, 125, 80, 55, 40, 20]
    for min_lightness in val_ranges:
        ranges = [np.array([110, 170, min_lightness]), np.array([120, 255, 255])]
        mask = inRange(hsv_img, ranges[0], ranges[1])
        pixels = image[mask == 255]
        rows, cols = np.where(mask == 255)

        if len(rows) < 10000:
            continue
        else:
            pixels = image[rows, cols]
            mean = np.mean(pixels)
            print(f"\t original mean is {mean} at {min_lightness}")

            prev_mean = data["Concentration"][-1]
            if concentration != data["Intensity"][-1]:
                print("\t concentrations UNEQUAL")
            elif data["Intensity"][-1] == concentration:
                print("\t concentration are EQUAL")
            t_lightness = min_lightness
            test_mean = mean
            while np.round(test_mean, 2) not in np.arange(np.round(prev_mean, 2) - 10, np.round(prev_mean, 2) + 10, 0.01):
                print(f"\t\t Lightness: {t_lightness}")
                t_light_index = val_ranges.index(t_lightness)
                if t_light_index in {0, len(val_ranges) - 1}:
                    break
                elif test_mean > prev_mean and t_light_index < len(val_ranges) - 1:
                    t_lightness = val_ranges[t_light_index + 1]
                elif test_mean < prev_mean and t_light_index > 0:
                    t_lightness = val_ranges[t_light_index - 1]
                test_mean = set_mean(image, t_lightness)
                print(f"\t\t Test Mean: {test_mean}")
            mean = test_mean
            min_lightness = t_lightness
        return mean, min_lightness

def set_mean(image, prev_light):
    n_ranges = [np.array([110, 170, prev_light]), np.array([120, 255, 255])]
    t_mask = inRange(cvtColor(image, 40), n_ranges[0], n_ranges[1])
    t_pixels = image[t_mask == 255]
    test_mean = np.mean(t_pixels)
    return test_mean
