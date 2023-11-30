import time
from image_analysis import debug, error, cvtColor, calculateMean, getPlainMean
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
import cv2

picam2 = Picamera2()
video_config = picam2.create_video_configuration()
encoder = H264Encoder(10000000)

def start_recording(power_button, record_start_time, timer_recording, loading_label_recording, layout):
    power_button.setEnabled(False)
    picam2.configure(video_config)
    picam2.start_recording(encoder, 'test.h264')
    record_start_time = time.time()
    timer_recording = QTimer(self)
    timer_recording.timeout.connect(self.record_for_10_seconds)
    timer_recording.start(100)
    loading_label_recording.setText("Recording...")
    layout.addWidget(self.loading_label_recording)
    layout.addWidget(self.progress_bar_recording)

def record_for_10_seconds(record_start_time, progress_bar_recording, timer_recording, loading_label_recording):
        elapsed_time = time.time() - record_start_time
        progress_value = int((elapsed_time / 10) * 100)
        progress_bar_recording.setValue(progress_value)

        if elapsed_time >= 10:
            timer_recording.stop()
            loading_label_recording.hide()
            progress_bar_recording.hide()
            stop_recording()

def stop_recording():
    picam2.stop_recording()
    calculate_results()

def calculate_results(loading_label_results, progress_bar_results):
    loading_label_results.setText("Calculating Results...")
    loading_label_results.show()
    progress_bar_results.setRange(0, 100)
    progress_bar_results.setValue(0)
    progress_bar_results.show()