from image_ana import getMean, is_float, processFolder, calculateMean
from processing import ML_Model, process_main, x, y, makeExcel
import tkinter as tk
from cv2 import imread, cvtColor
from tkinter import filedialog
from tkinter.ttk import *
from PIL import Image, ImageTk
from prediction import load, predict_value, download_predictions
import pandas as pd
import os
from time import time

def browse_path(entry_path, file_types=[("Excel Files", "*.xlsx")], file=True):
    if file:
        path = filedialog.askopenfilename(filetypes=file_types)
    else:
        path = filedialog.askdirectory()
    if path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, path)

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
        listbox_models.select_set(0, tk.END)  # Select all items
    else:
        listbox_models.selection_clear(0, tk.END)  # Deselect all items

def process_file():
    filepath = analysis_file_path.get()
    if filepath != "" and os.path.exists(filepath):
        selected_models = [model for model in ML_Model.models if model.name in [listbox_models.get(idx) for idx in listbox_models.curselection()]]
        if not selected_models:
            status_label.config(text="Please select at least one model")
            return
        parentPath = os.path.splitext(filepath)[0] 
        os.makedirs(parentPath) if not os.path.exists(parentPath) else None
        df = pd.read_excel(filepath)
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
                                analysis_file_path.delete(0,tk.END)
                                listbox_models.selection_clear(0, tk.END)
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
                                model_button = tk.Button(analysis_tab, text=m.name, command=lambda m_name=m.name:open_graph_image(m_name))
                                model_button.grid(row=10, column=i, padx=2, pady=2, sticky="ew")
                                extras.append(model_button)
                            extras += [set_test_percentage,set_labels_button,test_selection,test_percentage_input,selection_label_x,x_dropdown,selection_label_y, y_dropdown]
                            new_analysis_button = tk.Button(analysis_tab, text="Train New Models", command=lambda: (extras.append(new_analysis_button), reset()))
                            new_analysis_button.grid(row=11, column=0, padx=10, pady=10, sticky="ew")
                    except ValueError:
                        status_label.config(text="Please enter an integer")
                        
                set_test_percentage = tk.Button(analysis_tab, text="Set Test % and Download Models", command=set_test_size)
                set_test_percentage.grid(row=9, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
                test_selection = tk.Label(analysis_tab, text="Enter test percentage (20% recommended)")
                test_percentage_input= tk.Entry(analysis_tab, width=10)
                test_selection.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
                test_percentage_input.grid(row=8, column=4, padx=5, pady=5, sticky="ew")
                
            else:
                status_label.config(text="Set valid labels")
                return
            
        selection_label_x = tk.Label(analysis_tab, text="Independent Variable (X-Axis): ")
        x_selection_str = tk.StringVar(analysis_tab)
        x_selection_str.set("Select")
        x_dropdown = tk.OptionMenu(analysis_tab, x_selection_str, *labels)
        selection_label_y = tk.Label(analysis_tab, text="Dependent Variable (Y-Axis): ")
        y_selection_str = tk.StringVar(analysis_tab)
        y_selection_str.set("Select")
        y_dropdown = tk.OptionMenu(analysis_tab, y_selection_str, *labels)
        set_labels_button = tk.Button(analysis_tab, text="Set Labels", command=on_labels_clicked)
        
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
                image = imread(predict_image_entry.get().strip())
                hsv_img = cvtColor(image,40)
                x_val,_,_ = calculateMean(imread(predict_image_entry.get().strip()), hsv_img, 210, 8500)
                for i in [175,170, 160, 140, 80, 55, 40]:
                    if x_val == 0:
                        x_val,_,_ = calculateMean(imread(predict_image_entry.get().strip()), hsv_img, i, 8500)
                    else:
                        break
                predictions, label_text = predict_value(x_val, loaded_models)
                prediction_label.config(text= label_text)
                download_prediction = tk.Button(prediction_tab, text=f"Download predicition for intensity {round(x_val, 2)}", command=lambda: (download_predictions(x_val,predictions, path), status_label.config(text="Downloaded")))
                download_prediction.grid(row=6, column=0, padx=5, pady=5, sticky="ew")
            except ValueError:
                status_label.config(text="Please enter a number")
                return
            
        predict_button = tk.Button(prediction_tab, text="Predict", command=predict_button_click)
        predict_image_entry = tk.Entry(prediction_tab, width=50)
        predict_image_browse = tk.Button(prediction_tab, text="Browse", command=lambda:browse_path(predict_image_entry, [("JPG", "*.jpg"),("PNG", "*.png"),("JPEG", "*.jpeg")]))
        
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

app = tk.Tk()
app.title("ECL Predictive Analysis Interface")
app.iconbitmap("maxresdefault.ico")

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
img = Image.open("media/img/mmne.jpg")
img = img.resize((200, (200*img.height//img.width) ))
img = ImageTk.PhotoImage(img)
logo_label = tk.Label(analysis_tab, image=img)
analysis_file_path = tk.Entry(analysis_tab, width=50)
analysis_browse_button = tk.Button(analysis_tab, text="Browse", command=lambda: browse_path(analysis_file_path))
listbox_models = tk.Listbox(analysis_tab, selectmode=tk.MULTIPLE, height=len(ML_Model.models))
for model in ML_Model.models:
    listbox_models.insert(tk.END, model.name)
select_all_var = tk.BooleanVar()
select_all_checkbox = tk.Checkbutton(analysis_tab, text="Select All", variable=select_all_var, command=select_all_models)
start_processing_button = tk.Button(analysis_tab, text="Process File", command=process_file, state=tk.NORMAL)

analysis_file_path.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
analysis_browse_button.grid(row=2, column=3, padx=5, pady=5, sticky="e")
logo_label.grid(row=2, column=len(ML_Model.models)-1, padx=5,pady=5, sticky="ew")
listbox_models.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
select_all_checkbox.grid(row=3, column=4, padx=5, pady=5, sticky="w")
start_processing_button.grid(row=4, column=0, columnspan=4, padx=10, pady=5, sticky="ew")

#Predict Tab Elements
predict_path = tk.Entry(prediction_tab, width=50)
browse_predict_path = tk.Button(prediction_tab, text="Browse", command=lambda:browse_path(predict_path, [("Excel Files", "*.xlsx"), ("Pickle", "*pkl")]))
load_model_button = tk.Button(prediction_tab, text="Load Model(s)", command=load_model)
logo_label = tk.Label(prediction_tab, image=img)
prediction_label = tk.Label(prediction_tab,text="")

prediction_label.grid(row=10, column=0, sticky="ew")
logo_label.grid(row=3, column=len(ML_Model.models)-1, columnspan=4, padx=10, pady=5, sticky="ew")
predict_path.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
browse_predict_path.grid(row=1, column=5, padx=5, pady=5, sticky="ew")
load_model_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

#Image Analysis Tab Elements
image_folder_path = tk.Entry(image_analysis_tab, width=50)
browse_folder_path = tk.Button(image_analysis_tab, text="Browse", command=lambda:browse_path(image_folder_path, file=False))
analyse_image_button = tk.Button(image_analysis_tab, text="Perform Analysis", command=lambda: (analyse_image_button.config(state="disabled"), perform_image_analysis(), analyse_image_button.config(state="normal")), background="blue")
logo_label = tk.Label(image_analysis_tab, image=img)
image_analysis_label = tk.Label(image_analysis_tab, text="")

image_analysis_label.grid(row=10, column=0, sticky="ew")
logo_label.grid(row=3, column=len(ML_Model.models)-1, columnspan=4, padx=10, pady=5, sticky="ew")
image_folder_path.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
browse_folder_path.grid(row=1, column=5, padx=5, pady=5, sticky="ew")
analyse_image_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

#Footer
status_label = tk.Label(app, text="")
status_label.grid(row=20, column=0, sticky="ew")