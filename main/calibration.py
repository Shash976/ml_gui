
import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSlider, QFileDialog, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

class ImageMaskApp(QWidget):
    def __init__(self):
        super().__init__()
        self.color_space = 'LAB'  # Default color space
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        self.browseButton = QPushButton('Browse')
        self.browseButton.clicked.connect(self.loadImage)
        main_layout.addWidget(self.browseButton)

        # Radio buttons for color space selection
        self.labRadioButton = QRadioButton('LAB')
        self.labRadioButton.setChecked(True)
        self.labRadioButton.toggled.connect(self.onColorSpaceChanged)
        self.hsvRadioButton = QRadioButton('HSV')
        self.hsvRadioButton.toggled.connect(self.onColorSpaceChanged)
        color_space_layout = QHBoxLayout()
        color_space_layout.addWidget(self.labRadioButton)
        color_space_layout.addWidget(self.hsvRadioButton)
        main_layout.addLayout(color_space_layout)

        # Image layout
        image_layout = QHBoxLayout()
        self.imageLabel = QLabel(self)
        self.maskLabel = QLabel(self)
        self.resultLabel = QLabel(self)
        image_layout.addWidget(self.imageLabel)
        image_layout.addWidget(self.maskLabel)
        image_layout.addWidget(self.resultLabel)
        main_layout.addLayout(image_layout)

        # Result mean value label
        self.resultMeanLabel = QLabel('Mean: N/A')
        main_layout.addWidget(self.resultMeanLabel)

        # Sliders
        slider_layout = QVBoxLayout()
        self.slider_names = [
            "Lower 1st Channel", "Lower 2nd Channel", "Lower 3rd Channel",
            "Upper 1st Channel", "Upper 2nd Channel", "Upper 3rd Channel"
    ]

        self.sliders = []
        self.slider_labels = []
        for i, name in enumerate(self.slider_names):
            row_layout = QHBoxLayout()
            label = QLabel(name)
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(255)
            slider.setValue(255 if i >= 3 else 0)  # Upper sliders initialized to max
            slider.valueChanged.connect(self.updateMask)
            self.sliders.append(slider)
            self.slider_labels.append(label)
            row_layout.addWidget(label)
            row_layout.addWidget(slider)
            slider_layout.addLayout(row_layout)

        main_layout.addLayout(slider_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('Color Space Masking')
        #self.setGeometry(300, 300, 900, 600)

    def loadImage(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if fname:
            self.image = cv2.imread(fname)
            self.displayImage(self.image, self.imageLabel)
            self.updateMask()

    def displayImage(self, image, label):
        if image is not None:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, channel = image.shape
            bytesPerLine = 3 * width
            qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
            label.setPixmap(QPixmap.fromImage(qImg))
            label.setScaledContents(True)

    def onColorSpaceChanged(self):
        if self.labRadioButton.isChecked():
            self.color_space = 'LAB'
        elif self.hsvRadioButton.isChecked():
            self.color_space = 'HSV'
        if hasattr(self, "image"):
            self.updateMask()

    def updateMask(self):
        if hasattr(self, 'image'):
            if self.color_space == 'LAB':
                color_converted = cv2.cvtColor(self.image, cv2.COLOR_BGR2LAB)
            elif self.color_space =='HSV':
                color_converted = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
            for i, label in enumerate(self.slider_labels):
                label.setText(f"{self.slider_names[i]}: {str(self.sliders[i].value())}")
            lower_bound = np.array([self.sliders[i].value() for i in range(0, 3)])
            upper_bound = np.array([self.sliders[i].value() for i in range(3, 6)])

            # Create mask
            mask = cv2.inRange(color_converted, lower_bound, upper_bound)

            # Apply mask to get the resultant image
            result = cv2.bitwise_and(self.image, self.image, mask=mask)

            # Display the original image, mask, and resultant image
            self.displayImage(self.image, self.imageLabel)
            self.displayImage(mask, self.maskLabel)
            self.displayImage(result, self.resultLabel)

        # Calculate the mean of the result image where the mask is applied
            mean_val = np.mean(result[mask == 255])
            self.resultMeanLabel.setText(f'Mean: {mean_val:.2f}')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageMaskApp()
    window.show()
    sys.exit(app.exec_())