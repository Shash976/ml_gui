from cv2 import imread, cvtColor, inRange
from processing import makeExcel, os, np, pd
from multiprocessing import Pool

y = "Concentration"
x = "Intensity"
data = pd.DataFrame(columns=[y, x])
VAL_RANGES = [210, 175,170, 160,140,80,55, 40]

def processFolder(folder_path):
    subfolder_paths =  [os.path.join(folder_path, path) for path in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, path))]
    for subfolder in subfolder_paths:
        singleFolder(subfolder)
    makeExcel(path=os.path.join(folder_path, "data.xlsx"), data=data, sortby=y)

def singleFolder(subfolder):
    try:
        concentration = float(os.path.split(subfolder)[-1].split(" ")[0])
        print(concentration)
        images = [os.path.join(subfolder, image_path) for image_path in os.listdir(subfolder) if image_path.endswith((".jpg", ".png", ".jpeg"))]
        for image_path in images:
            print("\t----------------------------------------------------------------------------------------")
            print(f"\t working with {os.path.split(image_path)[-1]}")
            image = imread(image_path)
            mean = getMean(image, concentration)
            print(f"\t\t Intensity: {mean}")
            data.loc[len(data)] = [concentration, mean]
    except Exception as e:
        print(f"Error, issue is {e}")

def getMean(image,concentration):
    mean = 0
    hsv_img = cvtColor(image, 40)
    print("\t\t\t working... line 32")
    for lightness in VAL_RANGES:
        mean, p_length = calculateMean(image, hsv_img, lightness)
        print("\t\t\t working... line 35")
        if p_length < 10000:
            print("\t\t\t working... line 37")
            continue 
        elif len(data) > 2:
            prev_mean = data[x].iloc[-1]
            req_range = 7 if data[y].iloc[-1] == concentration else 17
            print("\t\t\t working... line 42")
            t_mean = mean
            t_lightness = lightness
            while abs(t_mean-prev_mean) > req_range:
                if t_mean > prev_mean:
                    t_lightness = VAL_RANGES[VAL_RANGES.index(t_lightness)+1]

                    print("\t\t\t working... line 47")
                else:
                    t_lightness = VAL_RANGES[VAL_RANGES.index(t_lightness)-1]
                    print("\t\t\t working... line 50")
                t_mean, _ = calculateMean(image, hsv_img, t_lightness)
                print("\t\t\t working... line 53 t_mean is ", t_mean, " at lightness ", t_lightness)
            mean = t_mean
            print("\t\t\t working... line 56")
            lightness = t_lightness
            print("\t\t\t working... line 58")
            return mean
        else:
            print("\t\t\t working... line 61")
            break
    return mean


def calculateMean(image, hsv_image, lightness):
    min_range, max_range = [np.array([110,170, lightness]), np.array([120, 255,255])]
    mask = inRange(hsv_image, min_range, max_range)
    print("\t\t\t working... line 69")
    required_pixels = image[mask==255]
    print("\t\t\t working... line 70; size of required pixels is ", required_pixels.shape[0], " at lightness ", lightness)
    mean =0
    if required_pixels.shape[0] > 0:
        print("\t\t\t working... line 72; calculated mean is ")
        mean = np.mean(required_pixels)
        print(f"\t\t\t\t {mean} at line 75")
    return mean, required_pixels.shape[0]