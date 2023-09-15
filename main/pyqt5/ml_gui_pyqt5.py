from PyQt5.QtWidgets import QApplication,QSizePolicy,QMainWindow, QAbstractItemView, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QProgressBar, QCheckBox, QListWidget, QComboBox, QFileDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap
from pandas import DataFrame, read_excel
import os
from time import time
from processing import process_main
from model_def import ML_Model, x,y
from PIL import Image
import sys

current_index = 0
total_images = []
DATA = DataFrame()
folder_path =''
progress_bar, progress_status_bar, status_label, image_placeholder, mean_label = 0,0,0,0,0
reagent = ''
timer = QTimer()
start_time = time()
global X, Y
X = x
Y = y

def initialize_processing(folder_path_args, progress_bar_elemnt, progress_status_bar_element, status_label_element, image_placeholder_element, mean_label_element, reagent_args="Luminol"):
    global total_images, current_index, DATA, Y, X, progress_bar, progress_status_bar, status_label, image_placeholder, mean_label, start_time, folder_path, reagent
    # Initialize your state here, similar to what you do at the beginning of processFolder
    reagent = reagent_args
    if os.path.exists(folder_path_args):
        folder_path = folder_path_args
        subfolder_paths = [os.path.join(folder_path, path) for path in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, path))]
        from image_analysis import is_float
        total_images = [os.path.join(sub_folder, image) for sub_folder in subfolder_paths if any(is_float(part) for part in os.path.basename(sub_folder).split(" ")) for image in os.listdir(sub_folder) if image.endswith((".jpg", ".png", ".jpeg", ".gif"))] 
        current_index = 0
        y_title = "Concentration"
        x_title = "Intensity"
        DATA = DataFrame(columns=[y_title, x_title])  # Initialize or reset your DataFrame
        start_time = time()
        progress_bar, progress_status_bar, status_label, image_placeholder, mean_label = progress_bar_elemnt, progress_status_bar_element, status_label_element, image_placeholder_element, mean_label_element
    else:
        status_label_element.setText("Enter a Valid Folderpath")
        return

def partial_processing(progress_bar, progress_status_bar, status_label, image_placeholder, mean_label, reagent="Luminol",n=1):  # You can adjust n based on how many images you want to process at a time
    global current_index, total_images, DATA
    # Your processing code here, but only for 'n' images starting from current_index
    for i in range(current_index, min(current_index + n, len(total_images))):
        image = total_images[i]
        # The rest of your code here, which includes updating labels, progress bars, etc.
        from image_analysis import processImage
        data = processImage(progress_bar,progress_status_bar, status_label, image_placeholder, mean_label, total_images, i, image, reagent=reagent, data=DATA)
        if type(data) is DataFrame:
            DATA = data
        else:
            return
    current_index += n

def check_completion():
    global current_index, total_images, start_time
    if current_index >= len(total_images):
        # Call makeExcel and stop the timer
        from image_analysis import makeExcel
        makeExcel(path=os.path.join(folder_path, "data.xlsx"), data=DATA, sortby="Concentration")  # Assuming makeExcel is your function to create Excel
        timer.stop()
        status_label.setText(f"Done within {round(time()-start_time, 2)} seconds.")

def on_timeout():
    global progress_bar, progress_status_bar, status_label, image_placeholder, mean_label, reagent
    partial_processing(progress_bar, progress_status_bar, status_label, image_placeholder, mean_label, reagent=reagent)
    check_completion()
    if current_index < len(total_images):
        timer.start(1)  # Restart the timer to process the next chunk

timer.timeout.connect(on_timeout)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ECL Predictive Analysis Interface")
        self.setWindowIcon(QIcon('mmne.jpg'))
        self.setGeometry(100, 100, 800, 600)
        
        self.central_widget = QWidget(self)
        self.main_layout = QVBoxLayout()

        #Fonts
        self.main_font = QFont("Calibri", pointSize=12, weight=30, italic=False)
        
        # Header
        self.header_bits_image = QLabel()
        i1 = Image.open(resource_path("bits_logo.jpg"))
        i1 = i1.resize((50, (50*i1.height//i1.width)))
        from numpy import array
        from image_analysis import numpy_to_qt_image
        self.header_bits_image.setPixmap(QPixmap(numpy_to_qt_image(array(i1), swapped=False)))
        self.header_label = QLabel("ECL Predictive Analysis Interface", self)
        self.header_font = QFont("Calibri", pointSize=26, weight=100, italic=False)
        self.header_label.setFont(self.header_font)
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_lab_image = QLabel()
        i2 = Image.open(resource_path("mmne.jpg"))
        i2 = i2.resize((50, (50*i2.height//i2.width)))
        self.header_lab_image.setPixmap(QPixmap(numpy_to_qt_image(array(i2), swapped=False)))
        self.header_lab_image.setAlignment(Qt.AlignRight)
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.header_bits_image)
        self.header_layout.addWidget(self.header_label)
        self.header_layout.addWidget(self.header_lab_image)
        
        self.main_layout.addLayout(self.header_layout)

        # Create tab widget and tabs
        self.tab_widget = QTabWidget()
        self.image_analysis_tab = QWidget()
        self.data_analysis_tab = QWidget()
        self.prediction_tab = QWidget()
        self.tab_widget.addTab(self.image_analysis_tab, "Image Analysis")
        self.tab_widget.addTab(self.data_analysis_tab, "Data Analysis")
        self.tab_widget.addTab(self.prediction_tab, "Prediction")

        # Layout for Image Analysis tab
        self.image_layout = QVBoxLayout()
        
        # i. Text input and Browse button
        self.image_folder_input = QLineEdit()
        self.browse_folder_btn = QPushButton("Browse")
        self.browse_folder_btn.clicked.connect(lambda:(self.browse(self.image_folder_input, False)))
        self.hbox1 = QHBoxLayout()
        self.hbox1.addWidget(self.image_folder_input)
        self.hbox1.addWidget(self.browse_folder_btn)
        
        self.luminol_formula_img_label = QLabel()
        self.luminol_formula_img_label.setPixmap(QPixmap(resource_path("eclmechanism.png")))
        self.luminol_formula_img_label.setAlignment(Qt.AlignCenter)

        self.reagent_text_label = QLabel("Reagent: ")
        self.reagent_dropdown = QLabel("Luminol")        
        self.choose_reagent_hbox = QHBoxLayout()
        self.choose_reagent_hbox.addWidget(self.reagent_text_label)
        self.choose_reagent_hbox.addWidget(self.reagent_dropdown)
        self.choose_reagent_hbox.setAlignment(Qt.AlignLeft)

        self.image_analysis_vbox1 = QVBoxLayout()
        self.image_analysis_vbox1.addLayout(self.hbox1)
        self.image_analysis_vbox1.addWidget(self.luminol_formula_img_label)
        self.image_analysis_vbox1.addLayout(self.choose_reagent_hbox)
        self.image_layout.addLayout(self.image_analysis_vbox1)

        self.perform_analysis_button  = QPushButton("Perform Analysis")
        self.perform_analysis_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.image_layout.addWidget(self.perform_analysis_button)

        # ii. Empty label for image
        self.image_label = QLabel()
        self.image_label.setVisible(False)
        self.image_layout.addWidget(self.image_label)
        
        # iii. Another empty label for dynamic text
        self.dynamic_label = QLabel()
        self.dynamic_label.setVisible(False)
        self.image_layout.addWidget(self.dynamic_label)
        
        # iv. Progress bar and percentage label
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel("0%")
        self.progress_label.setVisible(False)
        self.hbox2 = QHBoxLayout()
        self.hbox2.addWidget(self.progress_bar)
        self.hbox2.addWidget(self.progress_label)
        self.image_layout.addLayout(self.hbox2)
        
        self.image_analysis_tab.setLayout(self.image_layout)

        # Layout for Data Analysis tab
        self.data_layout = QVBoxLayout()
        
        # i. Text input and Browse button for .xlsx file
        self.data_analysis_file_input_bar = QLineEdit()
        self.browse_file_data_analysis = QPushButton("Browse")
        self.browse_file_data_analysis.clicked.connect(lambda:(self.browse(self.data_analysis_file_input_bar)))
        self.hbox3 = QHBoxLayout()
        self.hbox3.addWidget(self.data_analysis_file_input_bar)
        self.hbox3.addWidget(self.browse_file_data_analysis)

        self.load_data_button = QPushButton("Load Data from file")
        self.load_data_button.clicked.connect(self.load_listbox_bloc)
        self.vbox3 = QVBoxLayout()
        self.vbox3.addLayout(self.hbox3)
        self.vbox3.addWidget(self.load_data_button)
        self.data_layout.addLayout(self.vbox3)
        
        # The rest will be initially invisible
        # ii. Listbox and Select All checkbox
        self.listbox = QListWidget()
        self.listbox.addItems([model.name for model in ML_Model.models])
        self.listbox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listbox.setVisible(False)
        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.clicked.connect(lambda:(self.listbox.selectAll()))
        self.select_all_checkbox.setVisible(False)
        self.hbox4 = QHBoxLayout()
        self.hbox4.addWidget(self.listbox)
        self.hbox4.addWidget(self.select_all_checkbox)
        self.data_layout.addLayout(self.hbox4)
        
        # iii. Set Models button
        self.set_models_btn = QPushButton("Set Models")
        self.set_models_btn.clicked.connect(self.load_data_from_file)
        self.set_models_btn.setVisible(False)
        self.data_layout.addWidget(self.set_models_btn)
        
        # iv. X-Var dropdown
        self.x_var_label = QLabel("X-Var")
        self.x_var_dropdown = QComboBox()
        self.x_var_label.setVisible(False)
        self.x_var_dropdown.setVisible(False)
        self.hbox5 = QHBoxLayout()
        self.hbox5.addWidget(self.x_var_label)
        self.hbox5.addWidget(self.x_var_dropdown)
        self.hbox5.setAlignment(Qt.AlignCenter)
        self.data_layout.addLayout(self.hbox5)
        
        # v. Y-Var dropdown
        self.y_var_label = QLabel("Y-Var")
        self.y_var_dropdown = QComboBox()
        self.y_var_label.setVisible(False)
        self.y_var_dropdown.setVisible(False)
        self.hbox6 = QHBoxLayout()
        self.hbox6.addWidget(self.y_var_label)
        self.hbox6.addWidget(self.y_var_dropdown)
        self.hbox6.setAlignment(Qt.AlignCenter)
        self.data_layout.addLayout(self.hbox6)
        
        # vi. Set Labels button
        self.set_labels_btn = QPushButton("Set Labels")
        self.set_labels_btn.clicked.connect(self.ask_test_percentage)
        self.set_labels_btn.setVisible(False)
        self.data_layout.addWidget(self.set_labels_btn)
        
        # vii. Test percentage input
        self.test_percentage_label = QLabel("Enter test percentage (20% recommended)")
        self.test_percentage_input = QLineEdit()
        self.test_percentage_label.setVisible(False)
        self.test_percentage_input.setVisible(False)
        self.hbox7 = QHBoxLayout()
        self.hbox7.addWidget(self.test_percentage_label)
        self.hbox7.addWidget(self.test_percentage_input)
        self.data_layout.addLayout(self.hbox7)
        
        # viii. Set Test % and Download Models button
        self.set_test_btn = QPushButton("Set Test % and Download Models")
        self.set_test_btn.setVisible(False)
        self.set_test_btn.clicked.connect(self.set_test_percentage_and_run)
        self.data_layout.addWidget(self.set_test_btn)
        
        # ix. Train new data button
        self.reset_tab_btn = QPushButton("Train new data")
        self.reset_tab_btn.setVisible(False)
        self.reset_tab_btn.clicked.connect(lambda:self.reset_tab(self.data_layout))
        self.data_layout.addWidget(self.reset_tab_btn)

        self.data_analysis_tab.setLayout(self.data_layout)
        
        # Prediction tab
        self.prediction_layout = QVBoxLayout()
        
        # Loading the XLSX File
        self.prediction_file_input = QLineEdit()
        self.prediction_browse_file_btn = QPushButton("Browse")
        self.prediction_browse_file_btn.clicked.connect(lambda:(self.browse(self.prediction_file_input, file_types=[("Excel", "*.xlsx"), ("Pickle", "*.pkl")])))
        self.prediction_hbox1 = QHBoxLayout()
        self.prediction_hbox1.addWidget(self.prediction_file_input)
        self.prediction_hbox1.addWidget(self.prediction_browse_file_btn)
        self.prediction_layout.addLayout(self.prediction_hbox1)

        self.luminol_experiment_img_label = QLabel()
        self.luminol_experiment_img_label.setPixmap(QPixmap(resource_path("luminol_experiment.png")))
        self.prediction_layout.addWidget(self.luminol_experiment_img_label)

        self.prediction_reagent_label = QLabel("Reagent: ")
        self.prediction_reagent_name = QLabel("Luminol")
        self.prediction_hbox3 = QHBoxLayout()
        self.prediction_hbox3.addWidget(self.prediction_reagent_label)
        self.prediction_hbox3.addWidget(self.prediction_reagent_name)
        self.prediction_hbox3.setAlignment(Qt.AlignLeft)
        self.prediction_layout.addLayout(self.prediction_hbox3)

        self.prediction_load_file_btn = QPushButton("Load model(s) from file")
        self.prediction_load_file_btn.clicked.connect(self.load_models)
        self.prediction_layout.addWidget(self.prediction_load_file_btn)
        
        #SELECTING WHETHER TO USE IMAGE OR MANUAL VALUE
        self.select_input_method_label = QLabel("Select input method")
        self.select_input_method = QComboBox()
        self.select_input_method.addItems(["Path to an image or GIF", "Manual"])
        self.set_input_method_btn = QPushButton("Set Input Method")
        self.set_input_method_btn.clicked.connect(self.set_prediction_input_method)
        self.prediction_hbox4 = QHBoxLayout()
        self.prediction_hbox4.addWidget(self.select_input_method_label)
        self.prediction_hbox4.addWidget(self.select_input_method)
        self.prediction_hbox4.addWidget(self.set_input_method_btn)
        self.prediction_layout.addLayout(self.prediction_hbox4)

        #ENTER MANUALLY
        self.prediction_enter_manually_label = QLabel("Enter X-Value")
        self.prediction_x_val_entry = QLineEdit()
        self.prediction_hbox5 = QHBoxLayout()
        self.prediction_hbox5.addWidget(self.prediction_enter_manually_label)
        self.prediction_hbox5.addWidget(self.prediction_x_val_entry)
        self.prediction_layout.addLayout(self.prediction_hbox5)

        #LOADING THE IMAGE
        self.prediction_image_input = QLineEdit()
        self.prediction_image_input.setVisible(False)
        self.prediction_image_browse_btn = QPushButton("Browse")
        self.prediction_image_browse_btn.clicked.connect(lambda:(self.browse(self.prediction_image_input, file_types=[("Images", "*.jpg"),("Images", "*.png"),("Images", "*.jpeg"),("GIF", "*.gif")])))
        self.prediction_image_browse_btn.setVisible(False)
        self.prediction_hbox2 = QHBoxLayout()
        self.prediction_hbox2.addWidget(self.prediction_image_input)
        self.prediction_hbox2.addWidget(self.prediction_image_browse_btn)
        self.prediction_layout.addLayout(self.prediction_hbox2)

        #PREDICT
        self.prediction_load_and_predict_btn = QPushButton("Predict")
        self.prediction_load_and_predict_btn.setVisible(False)
        self.prediction_load_and_predict_btn.clicked.connect(self.load_and_predict)
        self.prediction_layout.addWidget(self.prediction_load_and_predict_btn)
        
        # RESETTING and DOWNLOAD
        self.results_label = QLabel("")
        self.results_label.setVisible(False)
        self.download_results_tn = QPushButton("Download Results")
        self.download_results_tn.setVisible(False)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(lambda:self.reset_tab(self.prediction_layout))
        self.reset_button.setVisible(False)
        self.prediction_vbox3 = QVBoxLayout()
        self.prediction_vbox3.addWidget(self.results_label)
        self.prediction_vbox3.addWidget(self.download_results_tn)
        self.prediction_vbox3.addWidget(self.reset_button)
        self.prediction_layout.addLayout(self.prediction_vbox3)

        self.prediction_tab.setLayout(self.prediction_layout)
        # Add tab widget to main layout
        self.main_layout.addWidget(self.tab_widget)

        # Footer
        self.footer_label = QLabel(" ", self)
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.footer_label)
        self.perform_analysis_button.clicked.connect(self.check_path_image_input)
        # Set layout and central widget
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)
        self.hide_elements(self.prediction_hbox5, footer=False)
        self.hide_elements(self.prediction_hbox2, footer=False)
        self.hide_elements(self.prediction_hbox4)
        self.startup()

    def startup(self):
        elements = self.getElements(self.prediction_layout)
        elements += self.getElements(self.data_layout)
        elements += self.getElements(self.image_layout)
        for element in elements:
            if type(element) in [type(self.footer_label), type(self.set_models_btn),type(self.image_folder_input), type(self.x_var_dropdown)]:
                element.setFont(self.main_font)
                if type(element) in [type(self.footer_label), type(self.set_models_btn)] and element not in [self.luminol_formula_img_label, self.luminol_experiment_img_label]:
                    element.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                    if type(element)==type(self.footer_label):
                        element.setAlignment(Qt.AlignLeft)
                elif element in [self.luminol_formula_img_label, self.luminol_experiment_img_label]:
                    element.setAlignment(Qt.AlignCenter)

    def browse(self, input_element, is_file=True, file_types=[("Excel Files", "*.xlsx")]):
        if is_file == True:
            path, _ = QFileDialog.getOpenFileName(self, filter=";;".join([f"{desc} ({ext})" for desc, ext in file_types]))
        else:
            path = QFileDialog.getExistingDirectory(self, "Select Folder")
        input_element.setText(path)
    
    def check_path_image_input(self):
        if os.path.exists(self.image_folder_input.text()):
            initialize_processing(self.image_folder_input.text(), self.progress_bar, self.progress_label, self.footer_label, self.image_label, self.dynamic_label, self.reagent_dropdown.text())
            timer.start(1)
        else:
            self.footer_label.setText("Please enter  a valid folderpath")

    def load_listbox_bloc(self):
        if os.path.exists(self.data_analysis_file_input_bar.text().strip()) and self.data_analysis_file_input_bar.text().endswith((".xlsx",".xls")):
            self.data_analysis_file_input_bar.setDisabled(True)
            self.listbox.setVisible(True)
            self.select_all_checkbox.setVisible(True)
            self.set_models_btn.setVisible(True)
            self.footer_label.setText("Please select models")
        else:
            self.footer_label.setText("Enter a valid filepath")
    
    def load_data_from_file(self):
        filepath = self.data_analysis_file_input_bar.text()
        selected_models = self.listbox.selectedItems()
        if selected_models:
            selected_models = [model for model in ML_Model.models if model.name in [m.text() for m in selected_models]]
            self.listbox.setDisabled(True)
            self.select_all_checkbox.setDisabled(True)
            df = read_excel(filepath)
            labels = df.columns.tolist()
            self.x_var_dropdown.addItems(labels)
            self.y_var_dropdown.addItems(labels)
            self.x_var_dropdown.setVisible(True)
            self.y_var_dropdown.setVisible(True)
            self.x_var_label.setVisible(True)
            self.y_var_label.setVisible(True)
            self.set_labels_btn.setVisible(True)
            self.footer_label.setText("Labels are selected")
        else:
            self.footer_label.setText("Please select at least one model")

    def ask_test_percentage(self):
        x_label = self.x_var_dropdown.currentText()
        y_label = self.y_var_dropdown.currentText()
        if x_label != y_label:
            global X, Y
            X.label = x_label
            Y.label = y_label
            self.set_test_btn.setVisible(True)
            self.test_percentage_input.setVisible(True)
            self.test_percentage_label.setVisible(True)
            self.x_var_dropdown.setDisabled(True)
            self.y_var_dropdown.setDisabled(True)
            self.footer_label.setText("Labels are set. Please set the test %")
        else:
            self.footer_label.setText("Please select labels. The X-label and Y-Label cannot be the same.")
    
    def set_test_percentage_and_run(self):
        test_percentage = self.test_percentage_input.text().strip()
        from image_analysis import is_float
        if is_float(test_percentage):
            test_percentage = float(test_percentage)
            filepath = self.data_analysis_file_input_bar.text()
            selected_models = [model for model in ML_Model.models if model.name in [m.text() for m in self.listbox.selectedItems()]]
            df = read_excel(filepath)
            parentPath = os.path.join(os.path.split(filepath)[0], os.path.splitext(os.path.split(filepath)[-1])[0])
            os.makedirs(parentPath) if not os.path.exists(parentPath) else None
            self.test_percentage_input.setDisabled(True)
            self.footer_label.setText("Starting.")
            try:
                global X,Y
                process_main(X, Y, df, int(test_percentage)/100, parentPath, selected_models)
            except Exception as e:
                self.footer_label.setText(f"Error -> {e}")
                return
            self.footer_label.setText("Done.")
            def open_graph_image(i):
                path = f"{selected_models[i].name.strip().replace(' ', '_').strip().lower()}.jpg"
                path = os.path.join(parentPath, path)
                from PIL import Image
                image_of_graph = Image.open(path)
                image_of_graph.show()
            self.hbox8 = QHBoxLayout()
            for i, m in enumerate(selected_models):
                model_button = QPushButton(m.name)
                m_name = m.name
                if type(m_name) is str:
                    model_button.clicked.connect(lambda checked, n=i:open_graph_image(n))
                    self.hbox8.addWidget(model_button)
            self.data_layout.addLayout(self.hbox8)
            self.reset_tab_btn.setVisible(True)
        else:
            self.footer_label.setText("Please choose a number between 1 and 100 for test percentage")

    def hide_elements(self, layout, exempt_list=[], footer=True):
        exempt_list=[self.load_data_button, self.browse_file_data_analysis, self.data_analysis_file_input_bar] if len(exempt_list) == 0 else exempt_list
        print("w1")
        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget != None:
                if widget not in exempt_list:
                    widget.setVisible(False)
                widget.setDisabled(False)
            elif widget == None:
                self.hide_elements(item, exempt_list)
        if footer:
            self.footer_label.setText("")
    
    def load_elements(self, layout, exempt_list=[]):
        exempt_list = [] if len(exempt_list) == 0 else exempt_list
        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget= item.widget()
            if widget != None:
                if widget not in exempt_list:
                    widget.setVisible(True)
                    widget.setDisabled(False)
            elif widget == None:
                if item not in exempt_list:
                    self.load_elements(item, exempt_list)

    def getElements(self, layout):
        count= layout.count()
        elements = []
        for i in range(count):
            item = layout.itemAt(i)
            if item.widget() is not None:
                elements.append(item.widget())
            elif item.widget() == None:
                elements += self.getElements(item)
        return elements

    def reset_tab(self, layout=None):
        layout = self.data_layout if layout == None else layout
        if layout == self.data_layout:
            global X, Y
            X=x
            Y=y
            print("w")
            self.hide_elements(self.data_layout)
        elif layout == self.prediction_layout:
            self.hide_elements(self.prediction_layout, exempt_list=[self.luminol_experiment_img_label,self.prediction_load_file_btn,self.prediction_reagent_label]+self.getElements(self.prediction_hbox1)+self.getElements(self.prediction_hbox3))

    def load_models(self):
        if os.path.exists(self.prediction_file_input.text().strip()) and self.prediction_file_input.text().strip().endswith(".xlsx"):
            self.prediction_file_input.setDisabled(True)
            self.load_elements(self.prediction_hbox4)
        else:
            self.footer_label.setText("Please enter a valid filepath")

    def set_prediction_input_method(self):
        self.select_input_method.setDisabled(True)
        if "image" in self.select_input_method.currentText().strip().lower():
            self.load_elements(self.prediction_hbox2)
        else:
            self.load_elements(self.prediction_hbox5)
        self.prediction_load_and_predict_btn.setVisible(True)
            
    def load_and_predict(self):
        x_val = None
        if "image" in self.select_input_method.currentText().lower():
            if os.path.exists(self.prediction_image_input.text()) and self.prediction_image_input.text().endswith((".gif",".jpg", ".jpeg", ".png")):
                self.prediction_image_input.setDisabled(True)
                image_path = self.prediction_image_input.text()
                reagent = self.prediction_reagent_name.text()
                self.prediction_reagent_name.setDisabled(True)
                if image_path.endswith(".gif"):
                    from image_analysis import getFrame
                    image = getFrame(image_path)
                else:
                    from image_analysis import imread
                    image = imread(image_path)
                from image_analysis import cvtColor, calculateMean, LUMINOL_RANGES
                hsv_image = cvtColor(image,40)
                reagent_ranges = {"Luminol": LUMINOL_RANGES}
                x_val,_,_ = calculateMean(image, hsv_image, reagent_ranges[reagent][0], 8500)
                for i in reagent_ranges[reagent][1:]:
                        if x_val == 0:
                            x_val,_,_ = calculateMean(image, hsv_image, i, 8500)
                        else:
                            break
            else:
                self.footer_label.setText("Please enter a valid Image Path.")
                return
        else:
            from image_analysis import is_float
            if is_float(self.prediction_x_val_entry.text()):
                x_val = float(self.prediction_x_val_entry.text())
            else:
                self.footer_label.setText("Please enter a valid number")
                return
        if x_val != None:
            from prediction import predict_value, load, download_predictions
            loaded_models = load(self.prediction_file_input.text().strip())
            predictions, label_text = predict_value(x_val, loaded_models)
            self.results_label.setText(f"At Intensity of {x_val}, the predicted Conentrations are \n{label_text}" )
            self.download_results_tn.clicked.connect(lambda:(download_predictions(x_val, predictions, parentPath=self.prediction_file_input.text().strip()), self.footer_label.setText("Downloaded")))
            self.load_elements(self.prediction_vbox3)
            self.footer_label.setText("Done")