import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
import time
from image_analysis import getPlainMean
picam2 = Picamera2()
video_config = picam2.create_video_configuration()
encoder = H264Encoder(10000000)
class CameraApp(QWidget):
	def __init__(self):
		super().__init__()
		self.power_button = QPushButton("Power On Camera", self)
		self.power_button.clicked.connect(self.start_recording)
		self.pic_label = QLabel(self)
		self.px= QPixmap("media/mmne.jpg")
		self.pic_label.setPixmap(self.px)
		self.pic_label.setMaximumHeight(200)
		self.pic_label.setMaximumWidth(200)
		self.layout = QVBoxLayout(self)
		self.layout.addWidget(self.power_button)
		self.layout.addWidget(self.pic_label)
		
		# OpenCV widget
		self.opencv_widget = QLabel(self)
		self.layout.addWidget(self.opencv_widget)
		self.loading_label_recording = QLabel(self)
		self.progress_bar_recording = QProgressBar(self)
		self.loading_label_results = QLabel(self)
		self.loading_label_results.setMaximumWidth(500)
		
		self.result_label = QLabel(self)
		
		
		
	def start_recording(self):
		self.power_button.setEnabled(False)
		self.pic_label.hide()
		picam2.configure(video_config)
		picam2.start_recording(encoder, 'test.h264')
		self.record_start_time = time.time()
		self.timer_recording = QTimer(self)
		self.timer_recording.timeout.connect(self.record_for_10_seconds)
		self.timer_recording.start(100)
		self.loading_label_recording.setText("Recording...")
		
		self.layout.addWidget(self.loading_label_recording)
		self.layout.addWidget(self.pic_label)
		self.layout.addWidget(self.progress_bar_recording)
		
	def record_for_10_seconds(self):
		elapsed_time = time.time() - self.record_start_time
		progress_value = int((elapsed_time / 10) * 100)
		self.progress_bar_recording.setValue(progress_value)
		if elapsed_time >= 10:
			self.timer_recording.stop()
			self.loading_label_recording.hide()
			self.progress_bar_recording.hide()
			self.pic_label.hide()
			self.stop_recording()
	def stop_recording(self):
		picam2.stop_recording()
		self.calculate_results()
	def calculate_results(self):
		self.loading_label_results.setText("Electrochemiluminescence")
		self.loading_label_results.show()
		'''self.progress_bar_results.setRange(0, 100)
		self.progress_bar_results.setValue(0)
		self.progress_bar_results.show()'''
		self.result_timer = QTimer(self)
		self.result_timer.timeout.connect(self.show_result)
		self.result_timer.start(50)
		self.result_start_time = time.time()
	def show_result(self):
		elapsed_time = time.time() - self.result_start_time
		'''progress_value = int((elapsed_time / 5) * 100)
		self.progress_bar_results.setValue(progress_value)'''
		cap = cv2.VideoCapture('test.h264')
		max_intensity = 0.0
		while cap.isOpened():
			ret, frame = cap.read()
			if ret:
				hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
				light_blue = np.array([100, 50, 50])
				dark_blue = np.array([130, 255, 255])
				mask = cv2.inRange(hsv, light_blue, dark_blue)
				mean_value = getPlainMean(frame, "Luminol")
				mean_value, area, crop_cords = getPlainMean(frame, "Luminol")
				if max_intensity < mean_value:
					max_intensity = mean_value
				mask_image = QImage(mask.data, mask.shape[1], mask.shape[0], QImage.Format_Indexed8)
				pixmap = QPixmap.fromImage(mask_image)
				self.opencv_widget.setPixmap(pixmap)
				self.opencv_widget.setMaximumHeight(400)
				self.opencv_widget.setMaximumWidth(600)
				self.opencv_widget.show()
				QApplication.processEvents()  # Process events to update the GUI
				cv2.waitKey(50)
			else:
				break
		cap.release()
		cv2.destroyAllWindows()
		if elapsed_time >= 5:
			self.result_timer.stop()
			self.loading_label_results.hide()
			'''self.progress_bar_results.hide()'''
			# Simulate background calculation
			time.sleep(2)
			self.result_label.setText(f"Maximum intensity light: {max_intensity}")
			self.layout.addWidget(self.result_label)
			reset_button = QPushButton("Reset", self)
			reset_button.clicked.connect(self.reset_interface)
			self.layout.addWidget(reset_button)
	def reset_interface(self):
		for i in reversed(range(self.layout.count())):
			widget = self.layout.itemAt(i).widget()
			if widget is not None:
				widget.setParent(None)
		self.power_button.setEnabled(True)
		self.layout.addWidget(self.power_button)
def main():
	app = QApplication(sys.argv)
	window = CameraApp()
	window.show()
	sys.exit(app.exec_())
if __name__ == "__main__":
	main()