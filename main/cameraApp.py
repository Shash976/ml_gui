#!/usr/bin/python3

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
                             QVBoxLayout, QWidget)
from PyQt5.QtCore import QTimer

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
from picamera2.previews.qt import QGlPicamera2
import cv2
import numpy as np
from sys import platform
import subprocess
import os


class CameraApp(QWidget):
    def __init__(self):
        super().__init__()

        self.picam2 = Picamera2()
        #self.picam2.post_callback = self.post_callback
        self.picam2.configure(self.picam2.create_video_configuration(main={"size": (1280, 720)}))

        
        self.qpicamera2 = QGlPicamera2(self.picam2, width=800, height=480, keep_ar=False)
        self.button = QPushButton("Start recording")
        self.button.clicked.connect(self.on_button_clicked)
        self.video_label = QLabel()
        self.result_label = QLabel()
        self.setWindowTitle("Qt Picamera2 App")
        self.recording = False

        self.init_video_timer()
        self.init_result_timer()

        self.result_label.setAlignment(QtCore.Qt.AlignTop)
        layout_vertical = QVBoxLayout()
        layout_horizontal = QHBoxLayout()
        layout_horizontal.addWidget(self.result_label)
        layout_horizontal.addWidget(self.video_label)
        layout_horizontal.addWidget(self.button)
        layout_vertical.addWidget(self.qpicamera2)
        layout_vertical.addLayout(layout_horizontal)
        self.setLayout(layout_vertical)

        self.picam2.start()

    def init_video_timer(self):
        self.current_time = 0
        self.video_label.setText("Please start recording")
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.video_timer_timeout)

    def post_callback(self, request):
        self.result_label.setText(''.join(f"{k}: {v}\n" for k, v in request.get_metadata().items()))

    def on_button_clicked(self):
        if not self.recording:
            encoder = H264Encoder(10000000)
            output = FileOutput("test.h264")
            self.picam2.start_encoder(encoder, output)
            self.init_result_timer()
            self.init_video_timer()
            self.button.setText("Recording..")
            self.button.setEnabled(False)
            self.recording = True
            self.video_timer.start(1200)
        else:
            self.picam2.stop_encoder()
            self.button.setEnabled(True)
            self.button.setText("Start recording")
            self.init_video_timer()
            #open_window("image.jpg")
            self.recording = False

    def video_timer_timeout(self):
        self.current_time +=1
        to_add = f"Recording.. {self.current_time}"
        self.video_label.setText(to_add)
        if self.current_time==10:
            self.video_timer.stop()
            self.current_time=0
            self.picam2.stop_encoder()
            self.cap = cv2.VideoCapture('test.h264')
            self.frames = []
            self.max_intensity = 0.0
            self.result_timer.start(10)
            self.result_label.setText(f"Intensity is {self.max_intensity} RLU")
            self.on_button_clicked()

    def init_result_timer(self):
        self.result_timer = QTimer()
        self.result_timer.timeout.connect(self.process_frame)
        self.result_label.setText("")
        

    def process_frame(self):
        ret, frame = self.cap.read()
        if ret:
            res = self.single_frame(frame)
            self.frames.append(res.astype(np.uint8))
              # Process events to update the GUI
            self.result_label.setText("Processing....")
            cv2.waitKey(20)
        else:
            self.frames = np.array(self.frames).astype(np.uint8)
            max_frame = np.max(self.frames, axis=0)
            self.max_intensity = np.round(np.mean(max_frame), 2)
            cv2.imwrite("image.jpg", max_frame)
            self.cap.release()
            cv2.destroyAllWindows()
            self.result_timer.stop()
            self.result_label.setText(f"Intensity is {self.max_intensity} RLU")

    def single_frame(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        light_blue = np.array([100, 50, 50])
        dark_blue = np.array([130, 255, 255])
        mask = cv2.inRange(hsv, light_blue, dark_blue)
        res = cv2.bitwise_and(frame, frame, mask=mask)
        return res

def open_window(path):
    if any([platform.startswith(system) for system in ["os","darwin","linux"]]):
        subprocess.call(["open", path])
    elif "win" in platform:
        os.startfile(path)

if __name__ == "__main__":
    app = QApplication([])
    camera_app = CameraApp()
    camera_app.show()
    app.exec()