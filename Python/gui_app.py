import cv2
import time

from PyQt5 import QtGui
from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QTimer
from random import randint
from .sensor_visualization import SensorVisualization
from .pose_estimation import PoseEstimation
from .gui.dialog import YoutubeDialog, GuideDialog, temp_url

class PoseThread(QThread):
    change_pixmap_signal = pyqtSignal(tuple)

    def run(self):
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
        sv = SensorVisualization(filepath='Python/imgs/chair_axis.png')
        sv.draw_base_pressure_circles(sv.org_img)
        while True:
            pressure_sensors = [randint(3, 60), randint(3, 60), randint(3, 60), randint(3, 60)]
            waist_sonic, neck_sonic = randint(10, 90), randint(10, 90)
            self.change_pixmap_signal.emit(sv.visualize(sv.org_img, pressure_sensors, waist_sonic, neck_sonic))
            time.sleep(0.4)

class GuiApp(QWidget):
    def __init__(self):
        super().__init__()

        # set variables
        self.start_time = time.time()
        self.pressure_sensors, self.waist_sonic, self.neck_sonic, self.unbalance_level, self.max_rad = -1, -1, -1, -1, -1
        self.sensor_label_size = (700, 700)
        self.pose_label_size = (900, 900)

        # initiate ui setting
        self.init_ui()
        
        # set QTimer
        qtimer = QTimer(self)
        qtimer.setInterval(900)
        qtimer.timeout.connect(self.timer_out_event)
        qtimer.start()

        # create the video capture thread
        self.thread = SensorThread()
        self.thread2 = PoseThread()

        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread2.change_pixmap_signal.connect(self.update_image2)

        # start the thread
        self.thread.start()
        self.thread2.start()

    def init_ui(self):
        self.setWindowTitle("Smart Chair Posture Correction Program")
        self.move(10, 10)

        # create the label that holds the image
        self.image_label = QLabel('label1', self)
        self.image_label.resize(self.sensor_label_size[0], self.sensor_label_size[1])
        self.image_label2 = QLabel('label2', self)
        self.image_label2.resize(self.pose_label_size[0], self.pose_label_size[1])
        self.info_label = QLabel('info1', self)
        # self.info_label.setFont(QtGui.QFont("맑은고딕", 20))
        self.time_label = QLabel('time', self)

        waiting_img = self.convert_cv_qt(cv2.imread('Python/imgs/waiting_sensor.jpg'), self.sensor_label_size)
        self.image_label.setPixmap(waiting_img)
        waiting_img = self.convert_cv_qt(cv2.imread('Python/imgs/waiting_webcam.jpg'), self.sensor_label_size)
        self.image_label2.setPixmap(waiting_img)

        # buttons
        self.btn1 = QPushButton('테스트버튼1', self)
        self.btn1.clicked.connect(self.btn1_clicked)
        self.btn2 = QPushButton('테스트버튼2', self)

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
        grid.addWidget(self.time_label, 3, 0)
        self.setLayout(grid)

        self.show()

    def btn1_clicked(self):
        self.guide_dialog.show()

    def guide_yes_btn(self):
        self.guide_dialog.close()
        self.youtube_dialog.set_webview_url(temp_url)
        self.youtube_dialog.show()

    def guide_no_btn(self):
        self.guide_dialog.close()

    def timer_out_event(self):
        sit_time = time.time() - self.start_time
        time_text = time.strftime('앉은 시간 : %H시 %M분 %S초', time.gmtime(sit_time))
        self.time_label.setText(time_text)

        if sit_time > 1:
            if (not self.youtube_dialog.isVisible()) and (not self.guide_dialog.isVisible()) and (int(sit_time) % 10 == 0):
                self.guide_dialog.set_label(f'앉은지 {int(sit_time)}초가 지났습니다. 스트레칭을 시작하실래요?')
                self.guide_dialog.show()

    @pyqtSlot(tuple)  # Sensor Visualization
    def update_image(self, data):
        """Updates the image_label with a new opencv image"""
        cv_img, self.pressure_sensors, self.waist_sonic, self.neck_sonic = data
        qt_img = self.convert_cv_qt(cv_img, self.sensor_label_size)
        self.image_label.setPixmap(qt_img)

        self.unbalance_level = abs((sum(self.pressure_sensors[:2]) / (sum(self.pressure_sensors[:2]) + sum(self.pressure_sensors[2:])) - 0.5) * 100)
        self.update_info_label()

    @pyqtSlot(tuple)
    def update_image2(self, data):  # PoseEstimation
        """Updates the image_label with a new opencv image"""
        cv_img , self.max_rad = data
        qt_img = self.convert_cv_qt(cv_img, self.pose_label_size)
        self.image_label2.setPixmap(qt_img)
        self.update_info_label()

    def update_info_label(self):
        self.info_label.setText(f'불균형도 : {self.unbalance_level:.3}%, 허리 센서거리 : {self.waist_sonic}, 목 센서거리 : {self.neck_sonic}, 목 각도 : {self.max_rad:.3f}')
    
    def convert_cv_qt(self, cv_img, size):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(size[0], size[1], Qt.KeepAspectRatio)

        return QPixmap.fromImage(p)
