# from pose_estimation import PoseEstimation
from sensor_visualization import SensorVisualization
from pose_estimation import PoseEstimation

from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QGridLayout
from PyQt5.QtGui import QPixmap
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
import time
from random import randint

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
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        sv = SensorVisualization(filepath='Python/chair_axis.png')
        sv.draw_base_pressure_circles(sv.org_img)
        while True:
            pressure_sensors = [randint(3, 60), randint(3, 60), randint(3, 60), randint(3, 60)]
            waist_sonic, neck_sonic = randint(10, 90), randint(10, 90)
            self.change_pixmap_signal.emit(sv.visualize(sv.org_img, pressure_sensors, waist_sonic, neck_sonic))
            time.sleep(0.1)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt live label demo")
        self.disply_width = 500
        self.display_height = 900
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)
        self.image_label2 = QLabel(self)
        self.image_label2.resize(self.disply_width, self.display_height)
        # create a text label
        self.textLabel = QLabel('Webcam')

        # create a vertical box layout and add the two labels
        grid = QGridLayout()
        self.setLayout(grid)
        grid.addWidget(self.image_label, 0, 0)
        grid.addWidget(self.image_label2, 0, 1)
        grid.addWidget(self.textLabel, 1, 0)

        # create the video capture thread
        self.thread = SensorThread()
        self.thread2 = PoseThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread2.change_pixmap_signal.connect(self.update_image2)
        # start the thread
        self.thread.start()
        self.thread2.start()



    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

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
    a = App()
    a.show()
    sys.exit(app.exec_())