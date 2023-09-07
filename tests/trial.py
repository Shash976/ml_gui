from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
import os
from PIL import Image
import sys

class MyWindow(QWidget):
    def __init__(self):
        super(MyWindow, self).__init__()

        self.setWindowTitle("PyQt5 Image Example")
        self.setGeometry(200, 200, 800, 600)

        self.layout = QVBoxLayout()

        selected_models = [{"name": "Model1"}, {"name": "Model2"}, {"name": "Model3"}]  # Replace this with your actual list of models
        parentPath = "your/directory/here"

        for i, m in enumerate(selected_models):
            model_button = QPushButton(m["name"])
            model_button.clicked.connect(lambda checked, m_name=m["name"]: self.open_graph_image(m_name, parentPath))
            self.layout.addWidget(model_button)

        self.image_label = QLabel()
        im = Image.open(r"G:\My Drive\Background\Naruto_12.jpg")
        im = im.resize((200,(200*im.height//im.width)))
        self.image_label.setPixmap(im.toqpixmap())
        self.layout.addWidget(self.image_label)
        self.test_btn = QPushButton("TEST")
        self.setLayout(self.layout)
    
    def testing(self):
        pass

    def open_graph_image(self, m_name, parentPath):
        print(m_name, type(m_name), parentPath)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())