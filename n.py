from cv2 import imread, cvtColor, inRange
from processing import makeExcel, os, np, pd

data = pd.DataFrame(columns=["Concentration", "Intensity"])
VAL_RANGES = [210, 175, 170, 160, 140, 125, 80, 55, 40]
def processFolder(folder_path):
    paths = [os.path.join(folder_path, path) for path in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, path))]
    for path in paths:
        try:
            concentration = float(os.path.split(path)[-1].split(" ")[0])
            for image_path in [os.path.join(path, image) for image in os.listdir(path) if image.endswith((".jpg", ".jpeg", ".png"))]:
                print("satarting with this imkage")
                mean, min_lightness = getMean(image_path, imread(image_path), concentration)
                print(f"Image name -> {image_path}")
                if mean is None:
                    print("MEAN NOT FOUND.")
                else:
                    print("THISB")
                    print(f"\t Mean is {mean}")
                    data.loc[len(data)] = [concentration, mean]                  
        except Exception as e:
            print(f"ERR -> {e}")
            continue
    makeExcel(path=os.path.join(folder_path, "data.xlsx"), data=data, sortby="Concentration")

def getMean(image_path, image, concentration):
    print(f"Working with {image_path}")
    mean = 0
    hsv_img = cvtColor(image, 40) 
    for min_lightness in VAL_RANGES:
        mean = calculate_intensity(image, hsv_img, min_lightness)
        if mean is not None:
            if len(data) > 2:
                prev_mean = data["Intensity"].iloc[-1]
                req_range = 20 if concentration != data["Concentration"].iloc[-1] else 15
                for t_lightness in VAL_RANGES:
                    test_mean = calculate_intensity(image, hsv_img, t_lightness)
                    if abs(test_mean-prev_mean) <= req_range or t_lightness == VAL_RANGES[-1]:
                        mean=test_mean
                        min_lightness = t_lightness
                        return mean, min_lightness
        else:
            print(f'\t mean not found at {min_lightness}')
            if min_lightness == VAL_RANGES[-1]:
                print("\tPROBLEM")
            continue
    print(f"\t Mean-> {mean} at {min_lightness}")
    return mean, min_lightness
        #ranges = [np.array([110, 170, min_lightness]), np.array([120, 255, 255])]
        #mask = inRange(hsv_img, ranges[0], ranges[1])
        #pixels = image[mask == 255]
        #if len(pixels) < 10000:
        #    continue
        #else:
        #    mean = np.mean(pixels)
        #    print(f"\t original mean is {mean} at {min_lightness}")
        #    t_lightness = min_lightness 
        #    test_mean = mean
        #    if len(data["Intensity"]) > 2:
        #        prev_mean = data["Intensity"][-1]
        #        if concentration != data["Concentration"][-1]:
        #            print("\t concentrations UNEQUAL")
        #            req_range = 20
        #        elif data["Concentration"][-1] == concentration:
        #            print("\t concentration are EQUAL")
        #            req_range = 10
        #        while abs(test_mean-prev_mean) > req_range:
        #            print(f"\t\t Lightness: {t_lightness}")
        #            t_light_index = VAL_RANGES.index(t_lightness)
        #            if t_light_index in {0, len(VAL_RANGES) - 1}:
        #                break
        #            elif test_mean > prev_mean and t_light_index < len(VAL_RANGES) - 1:
        #                t_lightness = VAL_RANGES[t_light_index + 1]
        #            elif test_mean < prev_mean and t_light_index > 0:
        #                t_lightness = VAL_RANGES[t_light_index - 1]
        #            test_mean = set_mean(image, t_lightness)
        #            print(f"\t\t Test Mean: {test_mean}")
        #    mean = test_mean
        #    min_lightness = t_lightness
        

def calculate_intensity(image, hsv_img,  min_lightness):
    min_range, max_range = [np.array([110,170, min_lightness]), np.array([120,255,255])]
    mask = inRange(hsv_img, min_range, max_range)
    pixels = image[mask==255]
    if len(pixels) < 10000:
        return None
    mean=np.mean(pixels)
    return mean

def set_mean(image, prev_light):
    n_ranges = [np.array([110, 170, prev_light]), np.array([120, 255, 255])]
    t_mask = inRange(cvtColor(image, 40), n_ranges[0], n_ranges[1])
    t_pixels = image[t_mask == 255]
    test_mean = np.mean(t_pixels)
    return test_mean
