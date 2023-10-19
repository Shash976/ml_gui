from cv2 import cvtColor, inRange, imdecode, threshold, THRESH_BINARY, THRESH_OTSU,COLOR_BGR2GRAY
from processing import makeExcel, os, np, pd
from util import is_float
from logging import basicConfig, INFO, WARNING, CRITICAL, ERROR, DEBUG, info, warning, error, critical, debug 
from PyQt5.QtGui import QImage, QPixmap
from util import crop_image, getFrame, get_image_array
from PIL.Image import fromarray
import os

Y = "Concentration"
X = "Intensity"
DATA = pd.DataFrame(columns=[Y, X])
VAL_RANGES = [210, 175,170, 160,140,80,55, 40, 20,10]
basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=DEBUG)
global total_images

def processFolder(folder_path, progress_bar, progress_status_bar, status_label, image_placeholder, mean_label, reagent):
    global total_images
    subfolder_paths =  [os.path.join(folder_path, path) for path in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, path))]
    total_images = [os.path.join(sub_folder, image) for sub_folder in subfolder_paths if any(is_float(part) for part in os.path.basename(sub_folder).split(" ")) for image in os.listdir(sub_folder) if image.endswith((".jpg", ".png", ".jpeg", ".gif"))]
    for i, image in enumerate(total_images):
        data = processImage(progress_bar, progress_status_bar, status_label, image_placeholder, mean_label, total_images, i, image, reagent, DATA)
        if data:
            continue
        else:
            return
    makeExcel(path=os.path.join(folder_path, "data.xlsx"), data=data, sortby=Y)

def processImage(progress_bar, progress_status_bar, status_label, image_placeholder, mean_label, total_images, i, image, reagent,data=DATA):
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
        mean, crop_cords = getMean(image, conc, data_frame=data, reagent=reagent, X=X, Y=Y, total_images=total_images)
        debug(f"is Mean works till line 27")  
        mean_label.setVisible(True)
        mean_label.setText(f"Intensity: {round(mean,2)} | File : {os.path.join(os.path.split(os.path.split(image)[0])[1],os.path.split(image)[1])}")
        debug(f"{mean} is Mean works till line 29. Crop Cords are {crop_cords}")
        im = crop_image(image_array, crop_cords) if mean > 0 else image_array
        debug(f"61 {type(im)}, {im.size}, {im.shape}")
        im = fromarray(np.uint8(cvtColor(im,4)))
        debug(f"63, {type(im)}")
        im = im.resize((200*(im.height//im.width), 200))
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

def getMean(image,concentration,reagent, data_frame=DATA, X = X, Y=Y, total_images=[]):
    image_name = image
    image = get_image_array(image)
    hsv_img = cvtColor(image, 40)
    lightness_ranges = VAL_RANGES if reagent.lower() in [r.name.lower() for r in Reagent.reagents] else []
    mean, _, crop_cords = getPlainMean(image, reagent)
    if len(data_frame) > 2:
        req_range = 5 if data_frame[Y].iloc[-1] == concentration else 20 if concentration-data_frame[Y].iloc[-1] >=0.25 else 8
        prev_conc_data = data_frame[data_frame[Y]==data_frame[Y].iloc[-1]]
        mean_of_prev_means = round(prev_conc_data[X].mean())
        mean_of_prev_means = (data_frame[data_frame[Y]==data_frame[Y].iloc[-2]][X].max() + data_frame[X].iloc[-1])/2 if data_frame[Y].iloc[-1] == concentration and len(data_frame[data_frame[Y]==data_frame[Y].iloc[-1]]) == 1 else mean_of_prev_means
        max_of_prev_means = round(prev_conc_data[X].max()) 
        next_image_mean = getPlainMean(get_image_array(total_images[total_images.index(image_name) + 1]), reagent) if total_images.index(image_name)+1 < len(total_images) else (0,0,0)
        next_image_mean = next_image_mean[0]
        info(f"{image_name} Initial Mean: {mean}\n\t Mean to compare to: {mean_of_prev_means if data_frame[Y].iloc[-1] == concentration else max_of_prev_means}")
        mean, crop_cords = addWeights(image, concentration, data_frame, Y, hsv_img, lightness_ranges, mean, crop_cords, req_range, mean_of_prev_means, max_of_prev_means, next_image_mean, data_frame[Y].iloc[-1] == concentration, reagent) 
    if len(crop_cords.keys()) == 4:
        selected_area = crop_image(image, crop_cords, pad=0)
        if mean - np.mean(selected_area) > 10:
            area_to_check = crop_image(image, crop_cords, pad=-2)
            gray_area = cvtColor(area_to_check, 6)
            thresh = threshold(gray_area, 0, 255,THRESH_BINARY+THRESH_OTSU)[1]
            new_mean = mean
            new_crop_cords = crop_cords
            for i in range(area_to_check.shape[0]):
                if np.sum(thresh[i, :]) == 0 and i+2 < area_to_check.shape[0] and i-3>0:
                    if all([np.sum(thresh[i+n,:]) == 0 for n in range(-3, 3)]):
                        means = [getPlainMean(area_to_check[:i+2,:,:], reagent), getPlainMean(area_to_check[i-3:,:,:], reagent)]
                        to_check = [new_mean, means[0][0], means[1][0]]
                        new_mean = max(to_check)
                        if new_mean in [means[0][0], means[1][0]]:
                            new_crop_cords = means[[means[0][0], means[1][0]].index(new_mean)][2]
            for i in range(area_to_check.shape[1]):
                if np.sum(thresh[:,i]) == 0 and i+2 < area_to_check.shape[1] and i-3>0:
                    if all([np.sum(thresh[:,i+n]) == 0 for n in range(-3, 3)]):
                        means = [getPlainMean(area_to_check[:,:i+2,:], reagent), getPlainMean(area_to_check[:,i-3:,:], reagent)]
                        to_check = [new_mean, means[0][0], means[1][0]]
                        new_mean = max(to_check)
                        if new_mean in [means[0][0], means[1][0]]:
                            new_crop_cords = means[[means[0][0], means[1][0]].index(new_mean)][2]
            mean = new_mean
            crop_cords = new_crop_cords
    return mean, crop_cords

def addWeights(image, concentration, data_frame, Y, hsv_img, lightness_ranges, mean, crop_cords, req_range, mean_of_prev_means, max_of_prev_means, next_image_mean, same_conc, reagent):
    temporary_mean, temporary_crop_cords = mean, crop_cords
    temporary_means_list, temporary_means_residuals, temporary_crop_cords_list = [],[],[]
    for lightness_index in range(len(lightness_ranges)):
        temporary_mean, _, temporary_crop_cords  = calculateMean(image, hsv_img, lightness_ranges[lightness_index], reagent)
        temporary_mean_rounded = round(temporary_mean)
        difference = temporary_mean_rounded-mean_of_prev_means
        lightness_index += 1
        temporary_means_list.append(temporary_mean)
        temporary_means_residuals.append(temporary_mean_rounded-max_of_prev_means if data_frame[Y].iloc[-1] < concentration else abs(difference))
        temporary_crop_cords_list.append(temporary_crop_cords)
        if data_frame[Y].iloc[-1] == concentration and abs(difference) <= req_range or data_frame[Y].iloc[-1] < concentration and 2 <= temporary_mean_rounded - max_of_prev_means <= req_range:
            debug(f"Concentration {'==' if data_frame[Y].iloc[-1] == concentration else '!='} and difference {abs(difference)} is in the range")
            break
    if same_conc and abs(difference) > req_range:
        temporary_mean = temporary_means_list[temporary_means_residuals.index(min(temporary_means_residuals))]    
    elif not same_conc:
        if abs(temporary_mean_rounded-max_of_prev_means) > req_range or temporary_mean_rounded-max_of_prev_means < 0:
            try:
                temporary_mean = temporary_means_list[temporary_means_residuals.index(min([i for i in temporary_means_residuals if i >= 0]))]
            except:
                temporary_mean = max(temporary_means_list)          
        elif any([abs(temp_mean-next_image_mean)<=5 for temp_mean in temporary_means_list]):
            next_mean_res = [abs(temp_mean-next_image_mean) for temp_mean in temporary_means_list]
            for res in next_mean_res:
                if res <= 5:
                    temporary_mean = temporary_means_list[next_mean_res.index(res)]
                    debug(f"temporary_mean changed to {temporary_mean} due to pressure from next mean {next_image_mean}")
    debug(f"\tNew temporary_mean ({'equal' if same_conc else 'UNEQUAL'} conc): {temporary_mean}")
    temporary_crop_cords = temporary_crop_cords_list[temporary_means_list.index(temporary_mean)] if temporary_mean > 0 else max(temporary_means_list) if max(temporary_means_list) > 0 else crop_cords
    mean = temporary_mean if temporary_mean > 0 else max(temporary_means_list) if max(temporary_means_list) > 0 else mean
    crop_cords = temporary_crop_cords if temporary_mean > 0 else crop_cords
    debug("RETURNED")
    return mean,crop_cords

def getPlainMean(image, reagent="luminol"):
    ranges = VAL_RANGES
    i = 0
    mean = 0
    hsv_img = cvtColor(image, 40)
    while i < len(ranges) and mean==0 or type(mean) not in [float, int, np.float64, np.float32]:
        mean, area, crop_cords = calculateMean(image, hsv_img, ranges[i], reagent)
        if mean > 0:
            break
        i+=1
    return mean,area, crop_cords

def calculateMean(image, hsv_image, lightness, reagent):
    reagent = Reagent.get_reagent(reagent)
    if type(reagent) != Reagent:
        return False
    min_hue, max_hue = reagent.min_hue, reagent.max_hue
    min_range, max_range = [np.array([min_hue,170, lightness]), np.array([max_hue, 255,255])]
    mask = inRange(hsv_image, min_range, max_range)
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
   
def numpy_to_qt_image(image, swapped=True):
    if len(image.shape) < 3:
        image = np.stack((image,)*3, axis=-1)
    height, width, channel = image.shape
    bytesPerLine = 3 * width
    if not swapped:
        return QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
    return QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()