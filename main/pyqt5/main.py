from ml_gui_pyqt5 import MainWindow, QApplication

# Running the application
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()