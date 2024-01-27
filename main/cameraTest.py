import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QProgressBar
from PyQt5.QtCore import QTimer
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

class VideoRecorder(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize camera
        self.camera = Picamera2()

        # Start button
        self.start_btn = QPushButton('Start Recording', self)
        self.start_btn.clicked.connect(self.start_recording)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(10)  # 10 seconds

        # Timer for progress bar
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress_bar)
        self.current_time = 0

    def start_recording(self):
        # Start recording
        self.camera.start_recording('video.h264')
        self.timer.start(1000)  # Update every second

    def update_progress_bar(self):
        self.current_time += 1
        self.progress_bar.setValue(self.current_time)

        # Stop recording after 10 seconds
        if self.current_time >= 10:
            self.timer.stop()
            self.camera.stop_recording()
            self.progress_bar.reset()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoRecorder()
    ex.show()
    sys.exit(app.exec_())
