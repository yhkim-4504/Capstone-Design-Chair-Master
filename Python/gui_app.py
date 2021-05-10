import sys
import cv2
import numpy as np
import time

from PyQt5 import QtGui
from PyQt5.QtWidgets import QPushButton, QWidget, QApplication, QLabel, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from random import randint
from .sensor_visualization import SensorVisualization
from .pose_estimation import PoseEstimation
from .gui.dialog import YoutubeDialog, GuideDialog, temp_url

class PoseThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        pe = PoseEstimation('Python/hrnet_implementation/video_cut.mp4')

        while True:
            ret, cv_img = pe.video.read()
            if ret:
                self.change_pixmap_signal.emit(pe.predict_and_draw(cv_img))
                for _ in range(20):
                    pe.video.read()
                time.sleep(0.01) 

class SensorThread(QThread):
    change_pixmap_signal = pyqtSignal(tuple)

    def run(self):
        # capture from web cam
        sv = SensorVisualization(filepath='Python/chair_axis.png')
        sv.draw_base_pressure_circles(sv.org_img)
        while True:
            pressure_sensors = [randint(3, 60), randint(3, 60), randint(3, 60), randint(3, 60)]
            waist_sonic, neck_sonic = randint(10, 90), randint(10, 90)
            self.change_pixmap_signal.emit(sv.visualize(sv.org_img, pressure_sensors, waist_sonic, neck_sonic))
            time.sleep(0.4)

class GuiApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # # create the video capture thread
        # self.thread = SensorThread()
        # self.thread2 = PoseThread()
        # # connect its signal to the update_image slot
        # self.thread.change_pixmap_signal.connect(self.update_image)
        # self.thread2.change_pixmap_signal.connect(self.update_image2)
        # # start the thread
        # self.thread.start()
        # self.thread2.start()

    def init_ui(self):
        self.setWindowTitle("Qt live label demo")
        self.disply_width = 500
        self.display_height = 900

        # create the label that holds the image
        self.image_label = QLabel('label1', self)
        self.image_label.resize(self.disply_width, self.display_height)
        self.image_label2 = QLabel('label2', self)
        self.image_label2.resize(self.disply_width, self.display_height)
        self.info_label = QLabel('Webcam')

        # buttons
        self.btn1 = QPushButton('btn1', self)
        self.btn1.clicked.connect(self.btn1_clicked)
        self.btn2 = QPushButton('btn2', self)

        # dialogs
        self.youtube_dialog = YoutubeDialog(self)
        self.guide_dialog = GuideDialog(self)
        self.guide_dialog.yes_btn.clicked.connect(self.guide_yes_btn)
        self.guide_dialog.no_btn.clicked.connect(self.guide_no_btn)

        # create a vertical box layout and add the two labels
        grid = QGridLayout()
        grid.addWidget(self.image_label, 0, 0)
        grid.addWidget(self.image_label2, 0, 1)
        grid.addWidget(self.info_label, 1, 0)
        grid.addWidget(self.btn1, 2, 0)
        grid.addWidget(self.btn2, 2, 1)
        self.setLayout(grid)

    def btn1_clicked(self):
        self.guide_dialog.show()

    def guide_yes_btn(self):
        self.guide_dialog.close()
        self.youtube_dialog.set_webview_url(temp_url)
        self.youtube_dialog.show()

    def guide_no_btn(self):
        self.guide_dialog.close()

    @pyqtSlot(tuple)
    def update_image(self, data):
        """Updates the image_label with a new opencv image"""
        cv_img, pressure_sensors, waist_sonic, neck_sonic = data
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

        unbalance_level = abs((sum(pressure_sensors[:2]) / (sum(pressure_sensors[:2]) + sum(pressure_sensors[2:])) - 0.5) * 100)
        self.info_label.setText(f'불균형도 : {unbalance_level:.3}%, 허리 센서거리 : {waist_sonic}, 목 센서거리 : {neck_sonic}')

    @pyqtSlot(np.ndarray)
    def update_image2(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label2.setPixmap(qt_img)
    
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
    gui_app = GuiApp()
    gui_app.show()
    sys.exit(app.exec_())