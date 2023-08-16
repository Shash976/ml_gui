import cv2
import os
import numpy as np
import pandas as pd
import openpyxl
from findmaxima2d import find_local_maxima, find_maxima

path = r"C:\Users\shashg\Documents\AI_Data"

"""
def grayMaxIntensity(img, size=(12,12,12,12)):
    frame = img
    gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    g_max = np.max(gray_img)
    finalMeans = []
    rows, cols = np.where(gray_img == g_max)
    xd,xp,yd,yp = size
    finalMeans = getGrayFinalMeans(frame, finalMeans, rows, cols, xd, xp, yd, yp)
    while len(finalMeans) == 0:
        g_max = g_max-1
        rows, cols = np.where(gray_img==g_max)
        finalMeans = getGrayFinalMeans(frame, finalMeans, rows, cols, xd, xp, yd, yp)

    maxVal = max([obj['mean'] for obj in finalMeans if str(obj['mean']).lower() != 'nan'])
    meanObj = [obj for obj in finalMeans if obj['mean'] == maxVal][0]
    meanObj['max'] = g_max
    return meanObj

def getGrayFinalMeans(frame, finalMeans=[], rows=0, cols=0, xd=0, xp=0, yd=0, yp=0):
    frame_height,frame_width,_ = frame.shape
    for row, col in zip(rows,cols):
        if row+yp > frame_height:
            yd += row+yp-frame_height
            yp = frame_height - row
        elif row - yd < 0:
            yp += abs(row-yd)
            yd = row
        if col+xp > frame_width:
            xd += col+xp-frame_width
            xp = frame_width - col
        elif col-xd < 0:
            xp += abs(row-xd)
            xd = col
        row2, row1, col2, col1 = row+yp, row-yd, col+xp, col-xd
        region = frame[row1:row2, col1:col2]
        m = np.mean(region)
        if not np.isnan(m):
            finalMeans.append({'mean': m, 'region':region, 'x': [
                              col2, col1], 'y': [row2, row1]})
    return finalMeans


def getMaximaPoints(image,prominence = 100):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image,6)
    local_max = find_local_maxima(image)
    y,x,_ = find_maxima(image, local_max, prominence)
    img_height, img_width = image.shape

    break_loop = False

    while break_loop == False:
        x = x.tolist() if type(x) is not list else x
        y = y.tolist() if type(y) is not list else y
        no_x = [num for num in  range(img_width, img_width-11, -1)] + [num for num in range(0,11,1)]
        no_y = [num for num in  range(img_height, img_height-11, -1)] + [num for num in range(0,11,1)]
        for num in no_x:
            if num in x:
                i = x.index(num)
                x.pop(i)
                y.pop(i)
        for num in no_y:
            if num in y:
                i = y.index(num)
                x.pop(i)
                y.pop(i)

        if len(x) > 0:
            break_loop = True
        else:
            if prominence > 0:
                if prominence > 10:
                    prominence -= 5
                if prominence <= 10:
                    prominence -= 0.1
                y,x,_ = find_maxima(image, local_max, prominence)
            else:
                print("No Maxima")
                break_loop = True
    return prominence,y,x, image
"""

def color_detection(image):
    mean = 0
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    ranges = [np.array([0,0,50]), np.array([120,255,255])]
    mask = cv2.inRange(hsv_img, ranges[0], ranges[1])
    contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cropped = image[y:y+h, x:x+w]
            mean = np.mean(cropped) if np.mean(cropped) > mean else mean
    else:
        cropped=image
        mean = np.mean(cropped)
    return mean

data = {
        "Concentration":[],
        "Intensity":[]
        }


def makeExcel(path, data, sortby = None):
    df = pd.DataFrame(data)

    # Sort the DataFrame in ascending order
    if sortby:
        df.sort_values(by=[sortby], inplace=True)

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
                        img = cv2.imread(filepath)
                        mean = color_detection(img)
                        data["Concentration"].append(concentration)
                        data['Intensity'].append(mean)
                        print(f"{file_name} done")
        except ValueError:
            print(folder_name)

makeExcel(os.path.join(path, "testing.xlsx"), data)