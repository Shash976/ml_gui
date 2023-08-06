from processing import ML_Model, process_main, x, y
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import *
from PIL import Image, ImageTk
from prediction import load, predict_value, download_predictions
import pandas as pd
import os

def browse_file(entry_path, file_types=[("Excel Files", "*.xlsx")]):
    file_path = filedialog.askopenfilename(filetypes=file_types)
    if file_path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, file_path)

def on_tab_selected(event):
    selected_tab = event.widget.select()
    tab_text = event.widget.tab(selected_tab, "text")
    if tab_text == analysis_tab_text:
        app.configure(bg="white")
    elif tab_text == predict_tab_text:
        app.configure(bg="black")

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
                            for i, model in enumerate(selected_models):
                                model_button = tk.Button(analysis_tab, text=model.name, command=lambda:Image.open(os.path.join(parentPath, f"{model.name.strip().replace(' ', '_').strip().lower()}.jpg")).show())
                                model_button.grid(row=10, column=i, padx=2, pady=2, sticky="ew")
                                extras.append(model_button)
                            extras += [set_test_percentage,set_labels_button,test_selection,test_percentage_input,selection_label_x,x_dropdown,selection_label_y, y_dropdown]
                            new_analysis_button = tk.Button(analysis_tab, text="Train New Models", command=lambda: (extras.append(new_analysis_button), reset()))
                            new_analysis_button.grid(row=11, column=0, padx=10, pady=10, sticky="ew")
                    except ValueError:
                        status_label.config(text="Please enter an integer")
                        
                set_test_percentage = tk.Button(analysis_tab, text="Set Test % and Download", command=set_test_size)
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
            x_val = predict_entry.get()
            try:
                x_val = float(x_val.strip())
                predictions, label_text = predict_value(x_val, loaded_models)
                prediction_label.config(text= label_text)
                download_prediction = tk.Button(prediction_tab, text="Download Prediction", command=lambda:(download_predictions(x_val,predictions, path), status_label.config(text="Downloaded")))
                download_prediction.grid(row=6, column=0, padx=5, pady=5, sticky="ew")
            except ValueError:
                status_label.config(text="Please enter a number")
                return

        predict_entry = tk.Entry(prediction_tab, width=10)
        predict_button = tk.Button(prediction_tab, text="Predict", command=predict_button_click)

        predict_entry.grid(row=3, column=0, columnspan=3)
        predict_button.grid(row=3, column=4, padx=5, pady=5,sticky="ew")
    else:
        status_label.config(text="Please enter a valid filepath")

app = tk.Tk()
app.title("ECL Predictive Analysis Interface")
app.iconbitmap(r"C:\Users\shashg\Desktop\Programming\PythonPrograms\GUi\models_gui\maxresdefault.ico")

app_tab_book = Notebook(app)
app_tab_book.grid(row=0, column=0, sticky='nsew')

analysis_tab = Frame(app_tab_book)
analysis_tab_text = "Analysis"
app_tab_book.add(analysis_tab, text=analysis_tab_text)

prediction_tab = Frame(app_tab_book)
predict_tab_text = "Predict"
app_tab_book.add(prediction_tab, text=predict_tab_text)

app_tab_book.bind("<<NotebookTabChanged>>", on_tab_selected)

#Analysis Tab elements
img = Image.open(r"C:\Users\shashg\Desktop\Programming\PythonPrograms\GUi\models_gui\mmne.jpg")
img = img.resize((200, (200*img.height//img.width) ))
img = ImageTk.PhotoImage(img)
logo_label = tk.Label(analysis_tab, image=img)
analysis_file_path = tk.Entry(analysis_tab, width=50)
analysis_browse_button = tk.Button(analysis_tab, text="Browse", command=lambda: browse_file(analysis_file_path))
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
browse_predict_path = tk.Button(prediction_tab, text="Browse", command=lambda:browse_file(predict_path, [("Excel Files", "*.xlsx"), ("Pickle", "*pkl")]))
load_model_button = tk.Button(prediction_tab, text="Load Model(s)", command=load_model)
logo_label = tk.Label(prediction_tab, image=img)
prediction_label = tk.Label(prediction_tab,text="")

prediction_label.grid(row=10, column=0, sticky="ew")
logo_label.grid(row=3, column=len(ML_Model.models)-1, columnspan=4, padx=10, pady=5, sticky="ew")
predict_path.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
browse_predict_path.grid(row=1, column=5, padx=5, pady=5, sticky="ew")
load_model_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

#Footer
status_label = tk.Label(app, text="")
status_label.grid(row=20, column=0, sticky="ew")