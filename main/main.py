from ml_gui_pyqt5 import MainWindow, QApplication, datetime

# Running the application
if __name__ == "__main__":
    try:
        app = QApplication([])
        window = MainWindow()
        window.showMaximized()
        window.show()
        app.exec_()
    except Exception as error:
        log = open("ecl_log.txt", "w+")
        now = datetime.now()
        _ = log.write(f'{now.strftime("%Y-%m-%d %H:%M:%S")} Error ->\n {error}')
        log.close()
