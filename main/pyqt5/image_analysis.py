from cv2 import imread, cvtColor, inRange, VideoCapture
from processing import makeExcel, os, np, pd
from logging import basicConfig, INFO, WARNING, CRITICAL, ERROR, DEBUG, info, warning, error, critical, debug 
from PyQt5.QtGui import QImage, QPixmap
from PIL.Image import fromarray
import os

Y = "Concentration"
X = "Intensity"
DATA = pd.DataFrame(columns=[Y, X])
LUMINOL_RANGES = [210, 175,170, 160,140,80,55, 40]
basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=CRITICAL)

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

def processFolder(folder_path, progress_bar, progress_status_bar, status_label, image_placeholder, mean_label):
    subfolder_paths =  [os.path.join(folder_path, path) for path in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, path))]
    total_images = [os.path.join(sub_folder, image) for sub_folder in subfolder_paths if any(is_float(part) for part in os.path.basename(sub_folder).split(" ")) for image in os.listdir(sub_folder) if image.endswith((".jpg", ".png", ".jpeg", ".gif"))]
    for i, image in enumerate(total_images):
        data = processImage(progress_bar, progress_status_bar, status_label, image_placeholder, mean_label, total_images, i, image, "Luminol", DATA)
        if data:
            continue
        else:
            return
    makeExcel(path=os.path.join(folder_path, "data.xlsx"), data=data, sortby=Y)

def processImage(progress_bar, progress_status_bar, status_label, image_placeholder, mean_label, total_images, i, image, reagent="Luminol",data=DATA):
    try:
        conc=None
        for part in os.path.split(os.path.split(image)[0])[-1].split(" "):
            try:
                conc=float(part)
            except:
                continue
        if conc==None:
            return None
        status_label.setText("Processing....")
        status_label.setVisible(True)
        if image.endswith(".gif"):
            image_array = getFrame(image)
        else:
            image_array = imread(image)
        debug(f"is Mean works till line 25")                       
        mean, crop_cords = getMean(image_array, conc, data_frame=data, X=X, Y=Y, reagent="Luminol")
        debug(f"is Mean works till line 27")  
        mean_label.setVisible(True)
        mean_label.setText(f"Intensity: {round(mean,2)}")
        debug(f"{mean} is Mean works till line 29")   
        im = image_array[crop_cords["Min-Y"]-10:crop_cords["Max-Y"]+10, crop_cords["Min-X"]-10:crop_cords["Max-X"]]+10
        im = fromarray(np.uint8(cvtColor(im,4)))
        im.resize((200, (200*im.height//im.width)))
        im = np.array(im)
        im = cvtColor(im,4)
        image_placeholder.setPixmap(QPixmap(numpy_to_qt_image(im)))
        image_placeholder.setVisible(True)
        progress_bar.setValue(i*100//(len(total_images)-1))
        progress_status_bar.setText(f"{i+1} out of {len(total_images)} done")
        progress_status_bar.setVisible(True)
        progress_bar.setVisible(True)
        data.loc[len(data)] = [conc, mean]
        debug("----------------------------------")
        return data
    except Exception as e:
        error(f"Error - > {e}")
        status_label.setText(f"Error -> {e}")
        return None


def getMean(image,concentration, data_frame=DATA, X = X, Y=Y, reagent="Luminol"):
    if type(image) is str:
        if image.endswith(".gif"):
                image = getFrame(image)
        else:
            image = imread(image)
    mean = 0
    hsv_img = cvtColor(image, 40)
    debug("\t\t\t working... line 32")
    if reagent == "Luminol":
        lightness_ranges = LUMINOL_RANGES
    for lightness in lightness_ranges:
        mean, p_length, crop_cords = calculateMean(image, hsv_img, lightness)
        debug("\t\t\t working... line 35")
        if p_length < 10000:
            debug("\t\t\t working... line 37")
            continue 
        elif len(data_frame) > 2:
            prev_mean = data_frame[X].iloc[-1]
            req_range = 7 if data_frame[Y].iloc[-1] == concentration else 17
            debug("\t\t\t working... line 42")
            t_mean = mean
            t_lightness = lightness
            while abs(t_mean-prev_mean) > req_range:
                if t_mean > prev_mean:
                    t_lightness = lightness_ranges[lightness_ranges.index(t_lightness)+1]

                    debug("\t\t\t working... line 47")
                else:
                    t_lightness = lightness_ranges[lightness_ranges.index(t_lightness)-1]
                    debug("\t\t\t working... line 50")
                t_mean, _, crop_cords = calculateMean(image, hsv_img, t_lightness)
                info(f"\t\t\t working... line 53 t_mean is {t_mean} at lightness {t_lightness}")
            mean = t_mean
            debug("\t\t\t working... line 56")
            lightness = t_lightness
            debug("\t\t\t working... line 58")
            return mean, crop_cords
        else:
            debug("\t\t\t working... line 61")
            break
    return mean, crop_cords


def calculateMean(image, hsv_image, lightness, min_pix=0):
    min_range, max_range = [np.array([110,170, lightness]), np.array([120, 255,255])]
    mask = inRange(hsv_image, min_range, max_range)
    debug("\t\t\t working... line 69")
    required_pixels = image[mask==255]
    info(f"\t\t\t working... line 70; size of required pixels is {required_pixels.shape[0]} at lightness {lightness}")
    mean =0
    crop_cords = {}
    if required_pixels.shape[0] > min_pix:
        debug("\t\t\t working... line 72; calculated mean is ")
        mean = np.mean(required_pixels)
        y_cords, x_cords = np.where(mask==255)
        crop_cords["Max-X"] = np.max(x_cords)
        crop_cords["Max-Y"] = np.max(y_cords)
        crop_cords["Min-X"] = np.min(x_cords)
        crop_cords["Min-Y"] = np.min(y_cords)
        info(f"\t\t\t\t {mean} at line 75")
    return mean, required_pixels.shape[0], crop_cords

def is_float(x):
    try:
        n = float(x)
        return True
    except Exception as e:
        return False
    
def numpy_to_qt_image(image, swapped=True):
    height, width, channel = image.shape
    bytesPerLine = 3 * width
    if not swapped:
        return QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
    return QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()