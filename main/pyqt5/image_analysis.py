from cv2 import cvtColor, inRange, VideoCapture, imdecode
from processing import makeExcel, os, np, pd
from logging import basicConfig, INFO, WARNING, CRITICAL, ERROR, DEBUG, info, warning, error, critical, debug 
from PyQt5.QtGui import QImage, QPixmap
from PIL.Image import fromarray
import os

Y = "Concentration"
X = "Intensity"
DATA = pd.DataFrame(columns=[Y, X])
LUMINOL_RANGES = [210, 175,170, 160,140,80,55, 40]
basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=ERROR)

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
            image_array = imdecode(np.fromfile(image, dtype=np.uint8), -1)
        debug(f"is Mean works till line 25")                       
        mean, crop_cords = getMean(image, conc, data_frame=data, X=X, Y=Y, reagent="Luminol")
        debug(f"is Mean works till line 27")  
        mean_label.setVisible(True)
        mean_label.setText(f"Intensity: {round(mean,2)} | File : {image}")
        debug(f"{mean} is Mean works till line 29")   
        im = image_array[crop_cords["Min-Y"]-10:crop_cords["Max-Y"]+10, crop_cords["Min-X"]-10:crop_cords["Max-X"]+10]
        debug("61", im)
        im = fromarray(np.uint8(cvtColor(im,4)))
        debug("63", im, type(im))
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
        error(f"{image} Error - > {e}")
        status_label.setText(f"{image} Error -> {e}")
        return None

def getMean(image,concentration, data_frame=DATA, X = X, Y=Y, reagent="Luminol"):
    image_name = image
    image = getFrame(image) if isinstance(image, str) and image.endswith(".gif") else imdecode(np.fromfile(image, dtype=np.uint8), -1) if isinstance(image, str) else image
    hsv_img = cvtColor(image, 40)
    lightness_ranges = LUMINOL_RANGES if reagent == "Luminol" else []
    mean, image_area, crop_cords = getPlainMean(image)
    if len(data_frame) > 2:
        req_range = 5 if data_frame[Y].iloc[-1] == concentration else 20 if concentration-data_frame[Y].iloc[-1] >=0.25 else 8
        prev_conc_data = data_frame[data_frame[Y]==data_frame[Y].iloc[-1]]
        mean_of_prev_means = round(prev_conc_data[X].mean()) 
        if data_frame[Y].iloc[-1] == concentration and len(data_frame[data_frame[Y]==data_frame[Y].iloc[-1]]) == 1:
            mean_of_prev_means = (data_frame[data_frame[Y]==data_frame[Y].iloc[-2]][X].max() + data_frame[X].iloc[-1])/2 
            debug(f"Prev Mean changed to {mean_of_prev_means} by -> {data_frame[data_frame[Y]==data_frame[Y].iloc[-2]][X].max()} + {data_frame[X].iloc[-1]} / 2 ")
        max_of_prev_means = round(prev_conc_data[X].max()) 
        t_mean = mean
        t_crop_cords = crop_cords
        t_means = []
        t_means_residuals = []
        t_crop_cords_list = []
        debug(f"{image_name} Initial Mean: {mean}")
        debug(f"\t Mean to compare to: {mean_of_prev_means if data_frame[Y].iloc[-1] == concentration else max_of_prev_means}")
        for lightness_index in range(len(lightness_ranges)):
            t_mean, _, t_crop_cords  = calculateMean(image, hsv_img, lightness_ranges[lightness_index])
            t_mean = round(t_mean)
            debug(f"\t\t {t_mean} at {lightness_ranges[lightness_index]}")
            lightness_index += 1
            t_means.append(t_mean)
            t_means_residuals.append(t_mean-max_of_prev_means if data_frame[Y].iloc[-1] < concentration else abs(t_mean-mean_of_prev_means))
            t_crop_cords_list.append(t_crop_cords)
            if data_frame[Y].iloc[-1] == concentration and abs(t_mean-mean_of_prev_means) <= req_range:
                debug(f"\t\t\t Conectration == EQUAL. {abs(t_mean-mean_of_prev_means)} is in the range")
                break
            elif data_frame[Y].iloc[-1] < concentration and t_mean-max_of_prev_means <= req_range and t_mean-max_of_prev_means >= 2:
                debug(f"\t\t\t Conectration != UNEQUAL. {t_mean-max_of_prev_means} is in the range")
                break
        if data_frame[Y].iloc[-1] == concentration and abs(t_mean-mean_of_prev_means) > req_range:
            t_mean = t_means[t_means_residuals.index(min(t_means_residuals))]    
            debug(f"\tNew t_mean ({'equal' if data_frame[Y].iloc[-1] == concentration else 'UNEQUAL'} conc): {t_mean}")
        else:
            if data_frame[Y].iloc[-1] < concentration and abs(t_mean-max_of_prev_means) > req_range or t_mean-max_of_prev_means < 0:
                if len([i for i in t_means_residuals if i >= 0]) == 0:
                    try:
                        t_mean = max(t_means)
                        debug("\t\t\t\t t_mean through max")
                    except:
                        pass
                else:
                    t_mean = t_means[t_means_residuals.index(min([i for i in t_means_residuals if i >= 0]))]
                    debug(f"\t\t\t\t t_mean through min. {t_means[t_means_residuals.index(min([i for i in t_means_residuals if i >= 0]))]} {t_means_residuals.index(min([i for i in t_means_residuals if i >= 0]))} {t_means_residuals} {min([i for i in t_means_residuals if i >= 0])} {[i for i in t_means_residuals if i >= 0]} {t_means}")
                debug(f"\tNew t_mean UNEQUAL conc: {t_mean}")
        t_crop_cords = t_crop_cords_list[t_means.index(t_mean)] if t_mean > 0 else max(t_means) if max(t_means) > 0 else crop_cords
        mean = t_mean if t_mean > 0 else max(t_means) if max(t_means) > 0 else mean
        crop_cords = t_crop_cords if t_mean > 0 else crop_cords
        debug("RETURNED")
    return mean, crop_cords

def getPlainMean(image):
    ranges = LUMINOL_RANGES
    i = 0
    mean = 0
    hsv_img = cvtColor(image, 40)
    while i < len(ranges) and mean==0 or type(mean) not in [float, int, np.float64, np.float32]:
        mean, area, crop_cords = calculateMean(image, hsv_img, ranges[i])
        if mean > 0:
            break
        i+=1
    return mean,area, crop_cords

def calculateMean(image, hsv_image, lightness):
    min_range, max_range = [np.array([110,170, lightness]), np.array([130, 255,255])]
    mask = inRange(hsv_image, min_range, max_range)
    required_pixels = image[mask==255]
    mean = 0
    crop_cords = {}
    for required_size in range(10000, 4500, -250):
        if required_pixels.size > required_size:
            mean = np.mean(required_pixels)
            y_cords, x_cords = np.where(mask==255)
            crop_cords["Max-X"] = np.max(x_cords)
            crop_cords["Max-Y"] = np.max(y_cords)
            crop_cords["Min-X"] = np.min(x_cords)
            crop_cords["Min-Y"] = np.min(y_cords)
            break
    return mean, required_pixels.size, crop_cords

def is_float(x):
    try:
        n = float(x)
        return True
    except Exception as e:
        return False
    
def numpy_to_qt_image(image, swapped=True):
    if len(image.shape) < 3:
        image = np.stack((image,)*3, axis=-1)
    height, width, channel = image.shape
    bytesPerLine = 3 * width
    if not swapped:
        return QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
    return QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()