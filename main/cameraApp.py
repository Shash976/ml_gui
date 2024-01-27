import sys
import cv2
import numpy as np
import time
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

# Camera initialization
picam2 = Picamera2()
video_config = picam2.create_video_configuration()
encoder = H264Encoder(10000000)

class CameraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.serial_number = 1
        self.video_name = "video.h264"

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.power_button = QPushButton("Start Recording", self)
        self.power_button.clicked.connect(self.record)
        self.layout.addWidget(self.power_button)

        self.opencv_widget = QLabel(self)
        self.layout.addWidget(self.opencv_widget)
        
        self.init_labels()
        self.init_timer()
        self.init_table()
        self.init_next_button()
        self.init_reset()
        self.init_export()

    def init_labels(self):
        self.loading_label_recording = QLabel(self)
        self.progress_bar_recording = QProgressBar(self)
        self.loading_label_results = QLabel(self)
        self.progress_bar_results = QProgressBar(self)
        self.result_label = QLabel(self)
        self.to_hide = [self.loading_label_recording, self.progress_bar_recording, self.loading_label_results, self.progress_bar_results,  self.result_label ]
        for element in self.to_hide:
            element.setVisible(False)
        self.layout.addWidget(self.result_label)

    def init_timer(self):
        self.record_timer = QTimer(self)
        self.record_timer.timeout.connect(self.update_progress_bar)
        self.current_time = 0

    def init_table(self):
        self.results_table_widget = QTableWidget(0, 2)  # 0 rows and 2 columns
        self.results_table_widget.setHorizontalHeaderLabels(["Serial Number", "Max Intensity"])
        self.results_table_widget.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.results_table_widget)

    def init_reset(self):
        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(self.reset_interface)
        self.layout.addWidget(self.reset_button)

    def init_next_button(self):
        self.next_button = QPushButton("Next", self)
        self.next_button.clicked.connect(self.next_recording)
        self.layout.addWidget(self.next_button)
    
    def init_export(self):
        self.export_csv_button = QPushButton("Export as CSV", self)
        self.export_csv_button.clicked.connect(self.export_as_csv)
        self.layout.addWidget(self.export_csv_button)

    '''def start_recording(self):
        self.power_button.setEnabled(False)
        picam2.configure(video_config)
        picam2.start_recording(encoder, 'test.h264')
        self.record_start_time = time.time()
        self.timer_recording = QTimer(self)
        self.timer_recording.timeout.connect(self.record_for_10_seconds)
        self.timer_recording.start(100)
        self.loading_label_recording.setText("Recording...")
        self.layout.addWidget(self.loading_label_recording)
        self.layout.addWidget(self.progress_bar_recording)

    def record_for_10_seconds(self):
        elapsed_time = time.time() - self.record_start_time
        progress_value = int((elapsed_time / 10) * 100)
        self.progress_bar_recording.setValue(progress_value)
        if elapsed_time >= 10:
            self.timer_recording.stop()
            self.loading_label_recording.hide()
            self.progress_bar_recording.hide()
            self.stop_recording()'''
            
    def record(self):
        self.power_button.setEnabled(False)
        self.progress_bar_recording.setVisible(True)
        self.progress_bar_recording.setMaximum(10)
        picam2.configure(video_config)
        picam2.start_recording(encoder, self.video_name)
        self.record_timer.start(1000)
    
    def update_progress_bar(self):
        self.current_time += 1
        self.progress_bar_recording.setValue(self.current_time)
        if self.current_time >= 10:
            self.current_time = 0
            picam2.stop_recording()
            for element in self.to_hide:
                element.setVisible(True)
            self.loading_label_results.setText("Calculating Results...")
            self.calculateTimer = QTimer(self)
            self.calculateTimer.timeout.connect(self.calculateIntensity)
            self.calculateTimer.start(50)
            
    def calculateIntensity(self):
        self.result_timer = QTimer(self)
        self.result_timer.timeout.connect(self.)
        print("STARTING?")
        self.current_time +=1
        cap = cv2.VideoCapture(self.video_name)
        max_intensity = 0.0
        frames = []
        print("CAP READY")
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("framin")
                l_a_b = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                light_blue = np.array([0, 0, 0])
                dark_blue = np.array([0, 0, 100])
                mask = cv2.inRange(l_a_b, light_blue, dark_blue)
                res = cv2.bitwise_and(frame, frame, mask=mask)
                pixmap = QPixmap(numpy_to_qt_image(frame))
                frames.append(res.astype(np.uint8))
                self.opencv_widget.setPixmap(pixmap)
                self.opencv_widget.setMaximumHeight(200)
                self.opencv_widget.setMaximumWidth(200)
                QApplication.processEvents()  # Process events to update the GUI
                cv2.waitKey(50)
            else:
                break
        max_intensity = 100
        print("MAX INTENSITY FOUND")
        self.result_label.setText(f"Intensity is {max_intensity}")
        row_position = self.results_table_widget.rowCount()
        self.results_table_widget.insertRow(row_position)
        self.results_table_widget.setItem(row_position, 0, QTableWidgetItem(str(self.serial_number)))
        self.results_table_widget.setItem(row_position, 1, QTableWidgetItem(str(max_intensity)))
        self.serial_number += 1 
        print("ADDED")
        cap.release()
        cv2.destroyAllWindows()

    def export_as_csv(self):
        with open('results.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Serial Number', 'Max Intensity'])
            for row in range(self.results_table_widget.rowCount()):
                serial_number = self.results_table_widget.item(row, 0).text()
                max_intensity = self.results_table_widget.item(row, 1).text()
                writer.writerow([serial_number, max_intensity])

    def reset_interface(self):
        self.results_table_widget.setRowCount(0)
        self.serial_number = 1
        self.power_button.setEnabled(True)

    def next_recording(self):
        self.loading_label_recording.hide()
        self.loading_label_results.hide()
        self.progress_bar_recording.setValue(0)
        self.progress_bar_results.setValue(0)
        self.opencv_widget.clear()
        self.power_button.setEnabled(True)

''' 
    def stop_recording(self):
        picam2.stop_recording()
        self.calculate_results()

    def calculate_results(self):
        self.loading_label_results.setText("Calculating Results...")
        self.loading_label_results.show()
        self.progress_bar_results.setRange(0, 100)
        self.progress_bar_results.setValue(0)
       ''' '''self.progress_bar_results.show()''' '''

        self.result_timer = QTimer(self)
        self.result_timer.timeout.connect(self.show_result)
        self.result_timer.start(50)
        self.result_start_time = time.time()
    def show_result(self):
        elapsed_time = time.time() - self.result_start_time
        progress_value = int((elapsed_time / 5) * 100)
        self.progress_bar_results.setValue(progress_value)

        cap = cv2.VideoCapture('test.h264')
        max_intensity = 0.0
        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                l_a_b = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                light_blue = np.array([0, 0, 0])
                dark_blue = np.array([0, 0, 100])
                mask = cv2.inRange(l_a_b, light_blue, dark_blue)
                res = cv2.bitwise_and(frame, frame, mask=mask)
                height, width, channel = res.shape
                bytesPerLine = 3 * width
                res_image = QImage(res.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
                pixmap = QPixmap.fromImage(res_image)
                frames.append(res.astype(np.uint8))
                self.opencv_widget.setPixmap(pixmap)
                self.opencv_widget.setMaximumHeight(200)
                self.opencv_widget.setMaximumWidth(200)
                QApplication.processEvents()  # Process events to update the GUI
                cv2.waitKey(50)
            else:
                break

        frames = np.array(frames).astype(np.uint8)
        max_intensity = np.mean(np.max(frames, axis=0))
        cap.release()
        cv2.destroyAllWindows()

        if elapsed_time >= 5:
            self.result_timer.stop()
            self.loading_label_results.hide()
            self.progress_bar_results.hide()
            time.sleep(2)'''  # Simulate background calculation''

def numpy_to_qt_image(image, swapped=True):
    if len(image.shape) < 3:
        image = np.stack((image,)*3, axis=-1)
    height, width, channel = image.shape
    bytesPerLine = 3 * width
    if not swapped:
        return QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
    return QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

def main():
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
