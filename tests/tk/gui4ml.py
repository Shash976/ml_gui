from cv2 import imread, cvtColor, inRange, VideoCapture
import numpy as np
from time import time
from PIL import Image, ImageTk
from pandas import DataFrame, read_excel, ExcelWriter
from tkinter import filedialog, Button, BooleanVar, StringVar, Listbox, Label, OptionMenu, Checkbutton, Entry, Tk
from tkinter.ttk import Progressbar, Notebook, Frame
from openpyxl import styles
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.linear_model import LinearRegression,RANSACRegressor, HuberRegressor, TheilSenRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.neighbors import KNeighborsRegressor
#from xgboost import XGBRegressor
from sklearn.svm import SVR
from logging import basicConfig, INFO, WARNING, CRITICAL, ERROR, DEBUG, info, warning, error, critical, debug 
from PIL.Image import fromarray
from PIL.ImageTk import PhotoImage
import joblib
import os

# Prelimenary Funcs
def makeExcel(path, data, sortby = None):
    df = data if type(data) is DataFrame else DataFrame(data)

    # Sort the DataFrame in ascending order
    if sortby:
        df.sort_values(by=[sortby], inplace=True)

    # Write the DataFrame to an Excel file with auto-adjusted column widths and AutoFit text
    with ExcelWriter(path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
        for row in worksheet.iter_rows():
            for cell in row:
                cell.alignment = styles.Alignment(wrap_text=True)

def browse_path(entry_path, file_types=[("Excel Files", "*.xlsx")], file=True):
    if file:
        path = filedialog.askopenfilename(filetypes=file_types)
    else:
        path = filedialog.askdirectory()
    if path:
        entry_path.delete(0, 'end')
        entry_path.insert(0, path)

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


class DataAxis:
    axes = []
    def __init__(self, label, original, test, train):
        self.label = label
        self.original = original
        self.test = test
        self.train = train
        DataAxis.axes.append(self)

global x
x = DataAxis("",[],[],[])
global y
y = DataAxis("",[],[],[])

class ML_Model:
    models = []
    def __init__(self, name, model, category, r2=0, mse=0, rmse=0, mae=0, ypred=[]):
        self.name = name
        self.model = model
        self.category = category
        self.rmse = rmse
        self.mae = mae
        self.r2 = r2
        self.mse = mse
        self.ypred = ypred
        ML_Model.models.append(self)

    def get_results(self):
        return {
            "R2 Score": self.r2,
            "MAE": self.mae,
            "MSE":self.mse,
            "RMSE": self.rmse,
            "Y-Pred": self.ypred
        }
    
    def get_error_metrics(models):
        error_metrics = {
            'Model': [],
            'R2 Score': [],
            'MAE': [],
            'MSE': [],
            'RMSE': []
        }
    
        for model in models:
            model_result = model.get_results()
            error_metrics['Model'].append(model.name)
            error_metrics['R2 Score'].append(model_result["R2 Score"])
            error_metrics['MAE'].append(model_result["MAE"])
            error_metrics['MSE'].append(model_result["MSE"])
            error_metrics['RMSE'].append(model_result["RMSE"])
        
        return error_metrics

    def get_model_names():
        return [model.name for model in ML_Model.models]

lr = ML_Model("Linear Regression", LinearRegression(), "Linear")
ransac = ML_Model("RANSAC Regression", RANSACRegressor(), "Linear")
huber = ML_Model("Huber Regression", HuberRegressor(), "Linear")
tsr = ML_Model("Theil-Sen Regression", TheilSenRegressor(), "Linear")
dtr = ML_Model("Decision Tree", DecisionTreeRegressor(), "Tree")
rfr = ML_Model("Random Forest", RandomForestRegressor(), "Ensemble")
ada = ML_Model("AdaBoost", AdaBoostRegressor(), "Ensemble")
gdboost = ML_Model("Gradient Boost", GradientBoostingRegressor(), "Ensemble")
#xgboost = ML_Model("XGBoost", XGBRegressor(), "Ensemble")
knn = ML_Model("KNeighbors", KNeighborsRegressor(), "Neighbor")
svm = ML_Model("Support Vector Machine", SVR(), "SVM")

def process_main(x,y,df, test_size, parentPath, models):
    y.original = df[y.label]
    if x.label in df.columns:
        x.original = df.drop([col for col in df.columns if col != x.label], axis=1)
    x.train, x.test, y.train, y.test = train_test_split(x.original.values,y.original.values, test_size=test_size, random_state=10)
    for model in models:
        try:
            model.model.fit(x.train, y.train)
        except Exception as e:
            print("Error at model.fit ", e)
        model.ypred = model.model.predict(x.test)
        model.r2 = r2_score(y.test, model.ypred)
        model.mse = mean_squared_error(y.test, model.ypred)
        model.mae = mean_absolute_error(y.test, model.ypred)
        model.rmse = np.sqrt(model.mse)
        modelsPath= os.path.join(parentPath, "models")
        if not os.path.exists(modelsPath):
            os.makedirs(modelsPath)
        modelPath = os.path.join(modelsPath, f"{model.name}.pkl")
        joblib.dump(model, modelPath)
    
    def errorMetricsSheet(parentPath):
        path = os.path.join(parentPath, 'error-metrics.xlsx')
        error_metrics = ML_Model.get_error_metrics(models)
        makeExcel(path, error_metrics)
        '''# Write the DataFrame to an Excel file
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets["Sheet 1"]
            for column_cells in worksheet.columns:
                length = max(len(str(cell.value)) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
            for row in worksheet.iter_rows():
                for cell in row:
                    cell.alignment = openpyxl.styles.Alignment(wrap_text=True)'''
    
    def putDataInCSV(parentPath):
        path = os.path.join(parentPath, 'xy-data.xlsx')
        y_preds = {
            f'{x.label}': x.test.flatten(),
            f'Original {y.label}': y.test.flatten()
        }
        for model in models:
            y_preds[model.name] = model.ypred.flatten()
    
        makeExcel(path, y_preds, f"Original {y.label}")

    def one_has_all(parentPath):
        models_num = len(models)
        plt.figure(figsize=((models_num*1.5)//1, (models_num*1.75)//1))
        for i, model in enumerate(models):
            if models_num % 3 ==0:
                row_div, cols, add = 3, 3, 0
            elif models_num%2 == 0:
                row_div, cols,add = 2,2, 0
            elif models_num%5 == 0:
                row_div, cols,add = 5,5, 0 
            else:
                row_div,cols,add = 3, 3, 1
            plt.subplot((models_num//row_div)+add, cols, i+1)
            plotSingleModel(model, parentPath)
        plt.savefig(os.path.join(parentPath, f'models.jpg'))
    
    def singlePlots(parentPath):
        for model in models:
            plotSingleModel(model, parentPath,save=True)
    
    def plotSingleModel(model,parentPath,save=False):
        if save:
            plt.figure(figsize=(10,10))
        plt.scatter(x.original,y.original, color="blue")
        plt.scatter(x.test, model.ypred, color="red")
        plt.legend(["Orginial", model.name])
        plt.title(f"{model.name} Technique")
        plt.xlabel(x.label)
        plt.ylabel(y.label)
        if save:
            save_name = model.name.strip().replace(" ", "_").strip().lower()
            save_path = os.path.join(parentPath, f"{save_name}.jpg")
            plt.savefig(save_path)
            plt.close()
    
    def all_in_one(parentPath):
        plt.figure(figsize=(10,10))
        plt.scatter(x.original,y.original, color="blue", label="Original")
        for color, model in zip(('red', 'green', 'black', 'magenta', 'orange', 'violet', 'brown', 'cyan', 'gray', 'khaki'),models):
            plt.scatter(x.test, model.ypred, color=color, label=model.name)
        plt.legend()
        plt.xlabel(x.label)
        plt.ylabel(y.label)
        plt.title(f"{x.label} vs {y.label}")
        plt.savefig(os.path.join(parentPath, f"total.jpg"))
    
    errorMetricsSheet(parentPath)
    putDataInCSV(parentPath)
    singlePlots(parentPath)
    plt.close()
    one_has_all(parentPath)
    plt.close()
    all_in_one(parentPath)
    plt.close()

#Prediction
def load(path):
    loaded_models = {}
    def load_model(model_path):
        loaded_model = joblib.load(model_path)
        loaded_model_path = os.path.splitext(os.path.split(model_path)[1])[0]
        loaded_models[loaded_model_path] = loaded_model
    if path.endswith(".pkl"):
        load_model(path)
    elif path.endswith(".xlsx"):
        parentPath = os.path.join(os.path.splitext(path)[0], "models")
        for model_file in os.listdir(parentPath):
            path = os.path.join(parentPath, model_file)
            load_model(path)
    return loaded_models

def predict_value(x_val, loaded_models):
    predictions = {}
    label_text = ""
    for loaded_model_name, predict_model in loaded_models.items():
        predictions[predict_model]  = round(predict_model.model.predict(np.array([x_val]).reshape(-1,1))[0], 3)
        label_text += f"{predict_model.name} ({predict_model.category}) -> {predictions[predict_model]}\n"
        
    return predictions, label_text

def download_predictions(x_val, predictions, parentPath):
    debug("checking")
    if parentPath.endswith(".xlsx"):
        info("ends with xlsx")
        parentPath = os.path.join(os.path.splitext(parentPath)[0], "predictions")
    elif parentPath.endswith(".pkl"):
        parentPath = os.path.join(os.path.split(os.path.split(parentPath)[0])[0], "predictions")
    print(parentPath)
    os.makedirs(parentPath) if not os.path.exists(parentPath) else None
    filename = f"prediction_({(len(os.listdir(parentPath)))}).xlsx"
    path = os.path.join(parentPath, filename)    
    print(path)
    preds = {
        "Model":["X-Val"],
        "Category":["-"],
        "Prediction":[x_val]
    }
    for model, prediction in predictions.items():
        preds["Model"].append(model.name)
        preds["Category"].append(model.category)
        preds["Prediction"].append(prediction)
    makeExcel(path, preds, sortby="Category")


#Image Analysis

Y = "Concentration"
X = "Intensity"
DATA = DataFrame(columns=[Y, X])
VAL_RANGES = [210, 175,170, 160,140,80,55, 40]
basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=CRITICAL)

def processFolder(folder_path, progress_bar, progress_status_bar, status_label, image_placeholder, mean_label):
    subfolder_paths =  [os.path.join(folder_path, path) for path in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, path))]
    total_images = [os.path.join(sub_folder, image) for sub_folder in subfolder_paths if any(is_float(part) for part in os.path.basename(sub_folder).split(" ")) for image in os.listdir(sub_folder) if image.endswith((".jpg", ".png", ".jpeg", ".gif"))]
    for i, image in enumerate(total_images):
        try:
            for part in os.path.split(os.path.split(image)[0])[-1].split(" "):
                try:
                    conc=float(part)
                except:
                    continue
            status_label.config(text="Processing....")
            if image.endswith(".gif"):
                image_array = getFrame(image)
            else:
                image_array = imread(image)
            print(f"is Mean works till line 25")                       
            mean, crop_cords = getMean(image_array, conc, data_frame=DATA, X=X, Y=Y)
            print(f"is Mean works till line 27")  
            mean_label.config(text=f"Intensity: {round(mean,2)}")
            mean_label.update_idletasks()
            print(f"{mean} is Mean works till line 29")   
            im = fromarray(np.uint8(cvtColor(image_array[crop_cords["Min-Y"]-10:crop_cords["Max-Y"]+10, crop_cords["Min-X"]-10:crop_cords["Max-X"]]+10,4)))
            
            im = im.resize((200, (200*im.height//im.width)))
            im = PhotoImage(im)
            image_placeholder.config(image=im)
            image_placeholder.update_idletasks()
            progress_bar["value"] = i*100//(len(total_images)-1)
            progress_status_bar.config(text=f"{i+1} out of {len(total_images)} done")
            progress_status_bar.update_idletasks()
            progress_bar.update_idletasks()
            DATA.loc[len(DATA)] = [conc, mean]
            print("----------------------------------")
        except Exception as e:
            print(f"Error - > {e}")
            return
    makeExcel(path=os.path.join(folder_path, "data.xlsx"), data=DATA, sortby=Y)
    return

def getMean(image,concentration, data_frame=DATA, X = X, Y=Y):
    if type(image) is str:
        if image.endswith(".gif"):
                image = getFrame(image)
        else:
            image = imread(image)
    mean = 0
    hsv_img = cvtColor(image, 40)
    debug("\t\t\t working... line 32")
    for lightness in VAL_RANGES:
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
                    t_lightness = VAL_RANGES[VAL_RANGES.index(t_lightness)+1]

                    debug("\t\t\t working... line 47")
                else:
                    t_lightness = VAL_RANGES[VAL_RANGES.index(t_lightness)-1]
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

#GUI
def on_tab_selected(event):
    selected_tab = event.widget.select()
    tab_text = event.widget.tab(selected_tab, "text")
    if tab_text == analysis_tab_text:
        app.configure(bg="white")
    elif tab_text == predict_tab_text:
        app.configure(bg="black")
    elif tab_text == image_analysis_text:
        app.configure(bg="blue")

def select_all_models():
    if select_all_var.get():
        listbox_models.select_set(0, 'end')  # Select all items
    else:
        listbox_models.selection_clear(0, 'end')  # Deselect all items

def process_file():
    filepath = analysis_file_path.get()
    if filepath != "" and os.path.exists(filepath):
        selected_models = [model for model in ML_Model.models if model.name in [listbox_models.get(idx) for idx in listbox_models.curselection()]]
        if not selected_models:
            status_label.config(text="Please select at least one model")
            return
        parentPath = os.path.splitext(filepath)[0] 
        os.makedirs(parentPath) if not os.path.exists(parentPath) else None
        df = read_excel(filepath)
        labels = df.columns.tolist()

        def on_labels_clicked():
            x.label = x_selection_str.get()
            y.label = y_selection_str.get()
            if y.label != x.label and y.label in labels and x.label in labels:
                status_label.config(text="Labels are set")
                def set_test_size():
                    try:
                        test_percentage = int(test_percentage_input.get())
                        if test_percentage > 0 and test_percentage < 100:
                            process_main(x,y,df,test_percentage/100, parentPath, selected_models)
                            status_label.config(text="Done.")
                            extras = []
                            def reset():
                                status_label.config(text="")
                                analysis_file_path.delete(0,'end')
                                listbox_models.selection_clear(0, 'end')
                                status_label.config(text="")
                                select_all_var.set(False)
                                for extra_widget in extras:
                                    extra_widget.grid_forget()
                            def open_graph_image(m_name):
                                path = f"{m_name.strip().replace(' ', '_').strip().lower()}.jpg"
                                path = os.path.join(parentPath, path)
                                image_of_graph = Image.open(path)
                                print(f"Opening {path}")
                                image_of_graph.show()
                            for i, m in enumerate(selected_models):
                                model_button = Button(analysis_tab, text=m.name, command=lambda m_name=m.name:open_graph_image(m_name))
                                model_button.grid(row=10, column=i, padx=2, pady=2, sticky="ew")
                                extras.append(model_button)
                            extras += [set_test_percentage,set_labels_button,test_selection,test_percentage_input,selection_label_x,x_dropdown,selection_label_y, y_dropdown]
                            new_analysis_button = Button(analysis_tab, text="Train New Models", command=lambda: (extras.append(new_analysis_button), reset()))
                            new_analysis_button.grid(row=11, column=0, padx=10, pady=10, sticky="ew")
                    except ValueError:
                        status_label.config(text="Please enter an integer")
                        
                set_test_percentage = Button(analysis_tab, text="Set Test % and Download Models", command=set_test_size)
                set_test_percentage.grid(row=9, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
                test_selection = Label(analysis_tab, text="Enter test percentage (20% recommended)")
                test_percentage_input= Entry(analysis_tab, width=10)
                test_selection.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
                test_percentage_input.grid(row=8, column=4, padx=5, pady=5, sticky="ew")
                
            else:
                status_label.config(text="Set valid labels")
                return
            
        selection_label_x = Label(analysis_tab, text="Independent Variable (X-Axis): ")
        x_selection_str = StringVar(analysis_tab)
        x_selection_str.set("Select")
        x_dropdown = OptionMenu(analysis_tab, x_selection_str, *labels)
        selection_label_y = Label(analysis_tab, text="Dependent Variable (Y-Axis): ")
        y_selection_str = StringVar(analysis_tab)
        y_selection_str.set("Select")
        y_dropdown = OptionMenu(analysis_tab, y_selection_str, *labels)
        set_labels_button = Button(analysis_tab, text="Set Labels", command=on_labels_clicked)
        
        selection_label_x.grid(row=5, column=0, columnspan=2, padx=5, pady=5,sticky="ew")
        x_dropdown.grid(row=5, column=2, padx=5, pady=5,sticky="ew")
        selection_label_y.grid(row=6, column=0, columnspan=2, padx=5, pady=5,sticky="ew")
        y_dropdown.grid(row=6, column=2, padx=5, pady=5,sticky="ew")
        set_labels_button.grid(row=7, column=0, columnspan=3,padx=10, pady=10,sticky="ew") 

    else:
        status_label.config("Enter a valid filepath")

def load_model():
    path = predict_path.get()
    if os.path.exists(path):
        loaded_models = load(path)
        def predict_button_click():
            try:
                image = predict_image_entry.get().strip()
                if image.endswith(".gif"):
                    image = getFrame(image)
                else:
                    image = imread(image)
                hsv_img = cvtColor(image,40)
                x_val,_,_ = calculateMean(imread(predict_image_entry.get().strip()), hsv_img, 210, 8500)
                for i in [175,170, 160, 140, 80, 55, 40]:
                    if x_val == 0:
                        x_val,_,_ = calculateMean(imread(predict_image_entry.get().strip()), hsv_img, i, 8500)
                    else:
                        break
                predictions, label_text = predict_value(x_val, loaded_models)
                prediction_label.config(text= label_text)
                download_prediction = Button(prediction_tab, text=f"Download predicition for intensity {round(x_val, 2)}", command=lambda: (download_predictions(x_val,predictions, path), status_label.config(text="Downloaded")))
                download_prediction.grid(row=6, column=0, padx=5, pady=5, sticky="ew")
            except ValueError:
                status_label.config(text="Please enter a number")
                return
            
        predict_button = Button(prediction_tab, text="Predict", command=predict_button_click)
        predict_image_entry = Entry(prediction_tab, width=50)
        predict_image_browse = Button(prediction_tab, text="Browse", command=lambda:browse_path(predict_image_entry, [("JPG", "*.jpg"),("PNG", "*.png"),("JPEG", "*.jpeg"), ("GIF", "*.gif")]))
        
        predict_image_entry.grid(row=3, column=0, columnspan=3)
        predict_image_browse.grid(row=3, column=4, padx=5,pady=5, sticky="ew")
        predict_button.grid(row=4, column=0, padx=5, pady=5,sticky="ew")
    else:
        status_label.config(text="Please enter a valid filepath")

def perform_image_analysis():
    folder_path = image_folder_path.get()
    if os.path.exists(folder_path):
        status_label.config(text="Starting....")
        show_image_label = Label(image_analysis_tab)
        intensity_label = Label(image_analysis_tab, text="")
        progress_bar = Progressbar(image_analysis_tab, orient="horizontal", length=800, mode="determinate")
        progress_status_bar = Label(image_analysis_tab, text="")
        show_image_label.grid(row=4, column=0, padx=10, pady=15, sticky="ew")
        intensity_label.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        progress_bar.grid(row=6, column=0, padx=5, pady=5, columnspan=3,sticky="ew")
        progress_status_bar.grid(row=6, column=4, padx=5,pady=5, sticky="e")
        try:
            start_time = time()
            processFolder(folder_path, progress_bar, progress_status_bar,status_label, show_image_label, intensity_label)
            status_label.config(text=f"Done within {round(time()-start_time, 2)} seconds. Check {os.path.basename(folder_path)} to find data.xlsx. Use the Analysis Tab to perform analysis")            
            return
        except Exception as e:
            print(f"Error -> {e}")
            status_label.config(text=f"Error -> {e}")
    else:
        status_label.config(text="Please entere a valid folder path")
        return

app = Tk()
app.title("ECL Predictive Analysis Interface")


app_tab_book = Notebook(app)
app_tab_book.grid(row=0, column=0, sticky='nsew')


image_analysis_tab = Frame(app_tab_book)
image_analysis_text = "Image Analysis"
app_tab_book.add(image_analysis_tab, text=image_analysis_text)

analysis_tab = Frame(app_tab_book)
analysis_tab_text = "Data Analysis"
app_tab_book.add(analysis_tab, text=analysis_tab_text)

prediction_tab = Frame(app_tab_book)
predict_tab_text = "Predict"
app_tab_book.add(prediction_tab, text=predict_tab_text)

app_tab_book.bind("<<NotebookTabChanged>>", on_tab_selected)

#Analysis Tab elements
img = Image.open("mmne.jpg")#"media/img/mmne.jpg")
img = img.resize((200, (200*img.height//img.width) ))
img = ImageTk.PhotoImage(img)
logo_label = Label(analysis_tab, image=img)
analysis_file_path = Entry(analysis_tab, width=50)
analysis_browse_button = Button(analysis_tab, text="Browse", command=lambda: browse_path(analysis_file_path))
listbox_models = Listbox(analysis_tab, selectmode="multiple", height=len(ML_Model.models))
for model in ML_Model.models:
    listbox_models.insert('end', model.name)
select_all_var = BooleanVar()
select_all_checkbox = Checkbutton(analysis_tab, text="Select All", variable=select_all_var, command=select_all_models)
start_processing_button = Button(analysis_tab, text="Process File", command=process_file, state="normal")

#app.iconbitmap("media/img/maxresdefault.ico")
app.iconbitmap("maxresdefault.ico")

analysis_file_path.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
analysis_browse_button.grid(row=2, column=3, padx=5, pady=5, sticky="e")
logo_label.grid(row=2, column=len(ML_Model.models)-1, padx=5,pady=5, sticky="ew")
listbox_models.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
select_all_checkbox.grid(row=3, column=4, padx=5, pady=5, sticky="w")
start_processing_button.grid(row=4, column=0, columnspan=4, padx=10, pady=5, sticky="ew")

#Predict Tab Elements
predict_path = Entry(prediction_tab, width=50)
browse_predict_path = Button(prediction_tab, text="Browse", command=lambda:browse_path(predict_path, [("Excel Files", "*.xlsx"), ("Pickle", "*pkl")]))
load_model_button = Button(prediction_tab, text="Load Model(s)", command=load_model)
logo_label = Label(prediction_tab, image=img)
prediction_label = Label(prediction_tab,text="")

prediction_label.grid(row=10, column=0, sticky="ew")
logo_label.grid(row=3, column=len(ML_Model.models)-1, columnspan=4, padx=10, pady=5, sticky="ew")
predict_path.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
browse_predict_path.grid(row=1, column=5, padx=5, pady=5, sticky="ew")
load_model_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

#Image Analysis Tab Elements
image_folder_path = Entry(image_analysis_tab, width=50)
browse_folder_path = Button(image_analysis_tab, text="Browse", command=lambda:browse_path(image_folder_path, file=False))
analyse_image_button = Button(image_analysis_tab, text="Perform Analysis", command=lambda: (analyse_image_button.config(state="disabled"), perform_image_analysis(), analyse_image_button.config(state="normal")), background="blue")
logo_label = Label(image_analysis_tab, image=img)
image_analysis_label = Label(image_analysis_tab, text="")

image_analysis_label.grid(row=10, column=0, sticky="ew")
logo_label.grid(row=3, column=len(ML_Model.models)-1, columnspan=4, padx=10, pady=5, sticky="ew")
image_folder_path.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
browse_folder_path.grid(row=1, column=5, padx=5, pady=5, sticky="ew")
analyse_image_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

#Footer
status_label = Label(app, text="")
status_label.grid(row=20, column=0, sticky="ew")

app.mainloop()