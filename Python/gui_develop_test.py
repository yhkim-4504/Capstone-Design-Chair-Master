from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QGridLayout, QPushButton, QDialog
from PyQt5.QtGui import QPixmap
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QUrl
import numpy as np
import time
from random import randint
from PyQt5 import QtWebEngineWidgets

temp_url = "https://www.youtube.com/embed/t67_zAg5vvI?autoplay=1"

class YoutubeDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setWindowTitle('Dialog Title')
        self.setWindowModality(Qt.ApplicationModal)

        self.webview = QtWebEngineWidgets.QWebEngineView(self)
        self.webview.setUrl(QUrl(temp_url))
        self.webview.setGeometry(0, 0, 500, 300)

    def set_webview_url(self, url: str) -> None:
        self.webview.setUrl(QUrl(url))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.webview.setUrl(QUrl("about:blank"))
        return super().closeEvent(a0)


class GuideDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setWindowTitle('Guide Dialog')
        self.setWindowModality(Qt.ApplicationModal)

        self.label = QLabel('여실래요?')
        self.yes_btn = QPushButton('네')
        self.no_btn = QPushButton('아니요')

        layout = QGridLayout()
        layout.addWidget(self.label, 0, 0, 2, 4)
        layout.addWidget(self.yes_btn, 2, 0, 2, 2)
        layout.addWidget(self.no_btn, 2, 2, 2, 2)

        self.setLayout(layout)

    def set_label(self, text):
        self.label.setText(text)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt live label demo")
        self.disply_width = 500
        self.display_height = 900
        # create the label that holds the image
        self.image_label = QLabel(self)
        
        self.image_label.setText('image_label')
        self.image_label.resize(self.disply_width, self.display_height)
        self.image_label2 = QLabel(self)
        self.image_label2.setText('image_label')
        self.image_label2.resize(self.disply_width, self.display_height)

        # create a text label
        self.info_label = QLabel('Webcam')

        #################################
        self.youtube_dialog = YoutubeDialog(self)
        self.guide_dialog = GuideDialog(self)
        self.guide_dialog.yes_btn.clicked.connect(self.guide_yes_btn)
        self.guide_dialog.no_btn.clicked.connect(self.guide_no_btn)

        self.btn1 = QPushButton('보이기', self)
        self.btn1.clicked.connect(self.btn1_clicked)
        self.btn2 = QPushButton('감추기', self)
        self.btn2.clicked.connect(self.btn2_clicked)

        # self.webview = QtWebEngineWidgets.QWebEngineView(self.dialog)
        # self.webview.setUrl(QUrl("https://www.youtube.com/embed/t67_zAg5vvI?autoplay=1"))
        # self.webview.setGeometry(0,0,500,300)


        #######################################

        # create a vertical box layout and add the two labels
        grid = QGridLayout(self)
        self.setLayout(grid)
        grid.addWidget(self.image_label, 0, 0)
        grid.addWidget(self.image_label2, 0, 1)
        grid.addWidget(self.info_label, 1, 0)
        
        #######################################
        # grid.addWidget(self.webview, 0, 3)
        grid.addWidget(self.btn1, 0, 2)
        grid.addWidget(self.btn2, 1, 2)
        #######################################

    def btn1_clicked(self):
        self.youtube_dialog.set_webview_url(temp_url)
        # self.youtube_dialog.show()
        self.guide_dialog.show()
        
    def btn2_clicked(self):
        pass

    def guide_yes_btn(self):
        self.guide_dialog.close()
        self.youtube_dialog.set_webview_url(temp_url)
        self.youtube_dialog.show()

    def guide_no_btn(self):
        self.guide_dialog.close()

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
if __name__=="__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())