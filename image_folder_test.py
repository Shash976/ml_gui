import cv2
import os
import numpy as np
import pandas as pd
import openpyxl
from findmaxima2d import find_local_maxima, find_maxima

path = r"C:\Users\shashg\Documents\AI_Data"    

data = {
        "Concentration":[],
        "Intensity":[],
        "Lightness":[],
        "Image":[],
        "Residual":[]
        }

def getMean(image_path, concentration):
    image = cv2.imread(image_path)
    print(f"Working with {image_path}")
    mean = 0
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    val_ranges = [210, 175,170, 160, 140, 125, 80, 55, 40, 20]
    for min_lightness in val_ranges:
        ranges = [np.array([110, 170, min_lightness]), np.array([120,255,255])]
        mask = cv2.inRange(hsv_img, ranges[0], ranges[1])
        pixels = []
        rows, cols = np.where(mask==255)

        if len(rows) < 10000:
            continue
        else:
            for row, col in zip(rows,cols):
                pixels.append(image[row][col])
            pixels = np.array(pixels)
            mean = np.mean(pixels)
            print(f"\t original mean is {mean} at {min_lightness}")
            if len(data["Intensity"]) >= 2:
                prev_mean = data["Intensity"][-1]
                if concentration != data["Concentration"][-1]:
                    print("\t concentrations UNEQUAL")
                    t_lightness = min_lightness
                    test_mean = mean
                    while np.round(test_mean,2) not in [np.round(i,2) for i in np.arange(np.round(prev_mean, 2)-10, np.round(prev_mean, 2) +10, 0.01)]:
                        print(f"\t\t Lightness: {t_lightness}")
                        t_light_index = val_ranges.index(t_lightness)
                        if t_light_index == len(val_ranges)-1 or t_light_index == 0:
                            break
                        elif test_mean > prev_mean and t_light_index < len(val_ranges)-1:
                            t_lightness = val_ranges[t_light_index+1]
                            print(f"\t\t New Lightness: {t_lightness}")
                        elif test_mean < prev_mean and t_light_index > 0:
                            t_lightness = val_ranges[t_light_index-1]
                            print(f"\t\t New Lightness: {t_lightness}")   
                        test_mean = set_mean(image,  t_lightness)
                        print(f"\t\t Test Mean: {test_mean}")
                    mean = test_mean
                    min_lightness = t_lightness
                elif data["Concentration"][-1] == concentration:
                    print("\t concentration are EQUAL")
                    t_lightness = min_lightness
                    test_mean = mean
                    while np.round(test_mean,2) not in [np.round(i,2) for i in np.arange(np.round(prev_mean, 2)-8, np.round(prev_mean, 2) +6, 0.01)]:
                        print(f"\t Mean not in range. Applying weights. Current Lightness: {t_lightness}")
                        t_light_index = val_ranges.index(t_lightness)
                        if t_light_index == len(val_ranges)-1 or t_light_index == 0:
                            break
                        elif test_mean > prev_mean and t_light_index < len(val_ranges)-1:
                            t_lightness = val_ranges[t_light_index+1]
                            print(f"\t\t New Lightness: {t_lightness}")
                        elif test_mean < prev_mean and t_light_index > 0:
                            t_lightness = val_ranges[t_light_index-1]  
                            print(f"\t\t New Lightness: {t_lightness}")
                        test_mean = set_mean(image,  t_lightness)
                        print(f"\t\t Test Mean: {test_mean}")
                    mean = test_mean
                    min_lightness = t_lightness
            return mean, min_lightness
    

def set_mean(image, prev_light):
    n_ranges = [np.array([110, 170, prev_light]), np.array([120,255,255])]
    t_mask = cv2.inRange(cv2.cvtColor(image, cv2.COLOR_BGR2HSV), n_ranges[0], n_ranges[1])
    t_pixels = []
    t_rows, t_cols = np.where(t_mask==255)
    for row, col in zip(t_rows,t_cols):
        t_pixels.append(image[row][col])
    t_pixels = np.array(t_pixels)
    test_mean = np.mean(t_pixels)
    return test_mean

"""
Model:

if current_concentration == previous_concentration then
    if current_mean not within +5 range of means in same concentration then
        lightness = lower_lightness
    elif current_mean nto withing -5 range of means in same concentration then
        lightness = higher_lightness
"""
def makeExcel(path, data, sortby = None, ascending=True):
    df = pd.DataFrame(data)

    # Sort the DataFrame in ascending order
    if sortby:
        df.sort_values(by=[sortby], inplace=True, ascending=ascending)

    # Write the DataFrame to an Excel file with auto-adjusted column widths and AutoFit text
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
        for row in worksheet.iter_rows():
            for cell in row:
                cell.alignment = openpyxl.styles.Alignment(wrap_text=True)


for folder_name in os.listdir(path):
    folder_path = os.path.join(path,folder_name)
    if os.path.isdir(folder_path):
        try:
            concentration = float(folder_name[:folder_name.index(" ")].strip())
            for file_name in os.listdir(folder_path):
                filepath = os.path.join(folder_path, file_name)
                if os.path.isfile(filepath):
                    if filepath.endswith((".png", ".jpg", ".jpeg")):
                        mean, lightness = getMean(filepath, concentration)
                        data["Concentration"].append(concentration)
                        data['Intensity'].append(mean)
                        data["Lightness"].append(lightness)
                        data["Image"].append(float(os.path.splitext(os.path.split(filepath)[1])[0]))
                        data["Residual"].append(abs(float(os.path.splitext(os.path.split(filepath)[1])[0]) - mean))
                        print(f"{file_name} done -> {mean} at {lightness}")
        except Exception as err:
            print(err)

makeExcel(os.path.join(path, "testing.xlsx"), data, "Residual", False)