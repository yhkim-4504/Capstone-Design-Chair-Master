import cv2
import time
import serial

from PyQt5 import QtGui
from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QGridLayout, QGroupBox, QInputDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QTimer
from random import randint
from .sensor_visualization import SensorVisualization
from .pose_estimation import PoseEstimation
from .gui.dialog import YoutubeDialog, GuideDialog, temp_url, url_list
from .tts_guide import TTS
from multiprocessing import Process

class PoseThread(QThread):
    change_pixmap_signal = pyqtSignal(tuple)

    def run(self):
        # pe = PoseEstimation('Python/hrnet_implementation/video_cut.mp4')
        # pe = PoseEstimation(None)
        pe = PoseEstimation(filename=None, camera_id=0)

        if not pe.is_opened:
            print('Video Capture Error')
            return

        while True:
            ret, cv_img = pe.video.read()
            if ret:
                self.change_pixmap_signal.emit(pe.predict_and_draw(cv_img))
                # for _ in range(20):
                #     pe.video.read()
                # time.sleep(0.01) 

class SensorThread(QThread):
    change_pixmap_signal = pyqtSignal(tuple)

    def __init__(self, parent, arduino_serial):
        super().__init__(parent=parent)
        self.arduino_serial = arduino_serial

    def run(self):
        sv = SensorVisualization(filepath='Python/imgs/chair_axis.png')
        sv.draw_base_pressure_circles(sv.org_img)
        while True:
            sensor_data = self.arduino_serial.readline().decode().split(';')
            # pressure_sensors = [randint(3, 60), randint(3, 60), randint(3, 60), randint(3, 60)]
            # waist_sonic, neck_sonic = randint(10, 90), randint(10, 90)
            # self.change_pixmap_signal.emit(sv.visualize(sv.org_img, pressure_sensors, waist_sonic, neck_sonic, 60))
            pressure_sensors = list(map(int, sensor_data[0:4]))
            waist_sonic, neck_sonic = 0, int(sensor_data[4])
            self.change_pixmap_signal.emit(sv.visualize(sv.org_img, pressure_sensors, waist_sonic, neck_sonic, 1024))
            # time.sleep(0.4)

class GuiApp(QWidget):
    def __init__(self):
        super().__init__()
        self.move(10, 10)
        self.setWindowTitle("Smart Chair Posture Correction Program")
        self.show()
        
        text, ok = QInputDialog.getText(self, 'Serial Port Setting', '??????????????? ????????? ????????? ??????????????????.')

        while True:
            try:
                self.arduino_serial = serial.Serial(text, 9600)
                break
            except:
                text, ok = QInputDialog.getText(self, 'Serial Port Setting', '????????? ??????????????????. ?????? ??????????????? ????????? ???????????????.')
                if not ok:
                    self.arduino_serial = None
                    break


        self.tts = TTS('tts.mp3')
        self.tts_process= Process(target=self.tts.run, args=('???????????????. ??????????????? ?????????????????????.', ))
        self.tts_process.start()

        # set variables
        self.start_time = time.time()
        self.pressure_sensors, self.waist_sonic, self.neck_sonic, self.unbalance_level, self.max_rad = -1, -1, -1, -1, 360
        self.sensor_label_size = (700, 700)
        self.pose_label_size = (900, 900)
        self.average_unbalance = []
        self.average_degree = []

        # initiate ui setting
        self.init_ui()
        
        # set QTimer
        qtimer = QTimer(self)
        qtimer.setInterval(900)
        qtimer.timeout.connect(self.timer_out_event)
        qtimer.start()

        # create the video capture thread
        self.thread = SensorThread(self, self.arduino_serial)
        self.thread2 = PoseThread(self)

        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread2.change_pixmap_signal.connect(self.update_image2)

        # start the thread
        if self.arduino_serial is not None:
            self.thread.start()
        self.thread2.start()

    def init_ui(self):
        # create the label that holds the image
        self.image_label = QLabel('label1', self)
        self.image_label.resize(self.sensor_label_size[0], self.sensor_label_size[1])
        self.image_label2 = QLabel('label2', self)
        self.image_label2.resize(self.pose_label_size[0], self.pose_label_size[1])
        self.info_label = QLabel('????????? ??????????????????.', self)
        self.info_label.setFont(QtGui.QFont("????????????", 20))
        self.time_label = QLabel('time', self)

        # GROUP BOX
        group_box1 = QGroupBox('Sensor Visualization')
        group_box1_grid = QGridLayout()
        group_box1_grid.addWidget(self.image_label)
        group_box1.setLayout(group_box1_grid)

        group_box2 = QGroupBox('Angle Measurement')
        group_box2_grid = QGridLayout()
        group_box2_grid.addWidget(self.image_label2)
        group_box2.setLayout(group_box2_grid)

        # waiting images
        waiting_img = self.convert_cv_qt(cv2.imread('Python/imgs/waiting_sensor.jpg'), self.sensor_label_size)
        self.image_label.setPixmap(waiting_img)
        waiting_img = self.convert_cv_qt(cv2.imread('Python/imgs/waiting_webcam.jpg'), self.sensor_label_size)
        self.image_label2.setPixmap(waiting_img)

        # # buttons
        # self.btn1 = QPushButton('btn1', self)
        # self.btn1.clicked.connect(self.btn1_clicked)
        # self.btn2 = QPushButton('btn2', self)

        # dialogs
        self.youtube_dialog = YoutubeDialog(self)
        self.guide_dialog = GuideDialog(self)
        self.guide_dialog.yes_btn.clicked.connect(self.guide_yes_btn)
        self.guide_dialog.no_btn.clicked.connect(self.guide_no_btn)

        # create a vertical box layout and add the two labels
        grid = QGridLayout()
        grid.addWidget(group_box1, 0, 0)
        grid.addWidget(group_box2, 0, 1)
        grid.addWidget(self.info_label, 1, 0, 1, 2)
        # grid.addWidget(self.btn1, 2, 0)
        # grid.addWidget(self.btn2, 2, 1)
        grid.addWidget(self.time_label, 3, 0)
        self.setLayout(grid)

    def guide_yes_btn(self):
        if self.tts_process.is_alive:
            self.tts_process.terminate()
        self.guide_dialog.close()
        self.youtube_dialog.show()

    def guide_no_btn(self):
        if self.tts_process.is_alive:
            self.tts_process.terminate()
        self.guide_dialog.close()

    def timer_out_event(self):
        sit_time = time.time() - self.start_time
        time_text = time.strftime('?????? ?????? : %H??? %M??? %S???'.encode('unicode-escape').decode(), time.gmtime(sit_time)).encode().decode('unicode-escape')
        self.time_label.setText(time_text)
        
        if sit_time > 1:
            if (not self.youtube_dialog.isVisible()) and (not self.guide_dialog.isVisible()) and (int(sit_time) % 60 == 0):
                text = f'????????? {int(sit_time)}?????? ???????????????. ??????????????? ???????????????????'
                self.guide_dialog.set_label(text)
                self.terminate_play_tts(text)
                self.guide_dialog.show()

            elif (not self.youtube_dialog.isVisible()) and (not self.guide_dialog.isVisible()) and (int(sit_time) % 30 == 0):
                average_unbalnce = sum(self.average_unbalance) / max(1, len(self.average_unbalance))
                average_degree = sum(self.average_degree) / max(1, len(self.average_degree))

                # No condition
                if average_unbalnce == 0 and average_degree == 0:
                    return

                if average_unbalnce > 20 and average_degree < 160:
                    text = '???????????? ????????? ??????????????????. ?????? ??????????????? ?????????????????????.'
                    self.terminate_play_tts(text)
                    self.guide_dialog.set_label(text + " ???????????????????")
                    self.youtube_dialog.set_webview_url(url_list['whole_body'])
                    self.guide_dialog.show()
                elif average_unbalnce > 20 and average_degree >= 160:
                    text = '???????????? ????????? ??????????????????. ????????? ??????????????? ??????????????????.'
                    self.guide_dialog.set_label(text + " ???????????????????")
                    self.terminate_play_tts(text)
                    self.youtube_dialog.set_webview_url(url_list['lower_body'])
                    self.guide_dialog.show()
                elif average_unbalnce <= 20 and average_degree < 160:
                    text = '?????? ????????? ?????? ????????????. ????????? ??????????????? ?????????????????????.'
                    self.guide_dialog.set_label(text + " ???????????????????")
                    self.terminate_play_tts(text)
                    self.youtube_dialog.set_webview_url(url_list['turtle_neck'])
                    self.guide_dialog.show()
                elif average_unbalnce <= 20 and average_degree >= 160:
                    text = '?????? ????????? ???????????? ????????????. ????????? ??????????????????.'
                    self.guide_dialog.set_label(text + " ???????????????????")
                    self.terminate_play_tts(text)

                self.average_degree.clear()
                self.average_unbalance.clear()

    def terminate_play_tts(self, text):
        if self.tts_process.is_alive:
            self.tts_process.terminate()
        self.tts_process = Process(target=self.tts.run, args=(text, ))
        self.tts_process.start()

    @pyqtSlot(tuple)  # Sensor Visualization
    def update_image(self, data):
        """Updates the image_label with a new opencv image"""
        cv_img, self.pressure_sensors, self.waist_sonic, self.neck_sonic = data
        qt_img = self.convert_cv_qt(cv_img, self.sensor_label_size)
        self.image_label.setPixmap(qt_img)

        self.unbalance_level = abs((sum(self.pressure_sensors[:2]) / (sum(self.pressure_sensors[:2]) + sum(self.pressure_sensors[2:])) - 0.5) * 100)
        self.average_unbalance.append(self.unbalance_level)
        self.update_info_label()

    @pyqtSlot(tuple)
    def update_image2(self, data):  # PoseEstimation
        """Updates the image_label with a new opencv image"""
        cv_img , self.max_rad = data
        qt_img = self.convert_cv_qt(cv_img, self.pose_label_size)
        self.image_label2.setPixmap(qt_img)
        if self.max_rad != -1:
            self.average_degree.append(self.max_rad)
        self.update_info_label()

    def update_info_label(self):
        average_unbalnce = sum(self.average_unbalance) / max(1, len(self.average_unbalance))
        average_degree = sum(self.average_degree) / max(1, len(self.average_degree))
        if average_degree == 360:
            average_degree = -1
        self.info_label.setText(
        f"""???????????? : {float(self.unbalance_level):.3f}%, ?????? ???????????? : {self.waist_sonic}cm, ??? ???????????? : {self.neck_sonic}cm, ??? ?????? : {float(self.max_rad):.1f}???
?????? ???????????? : {float(average_unbalnce):.3f}%, ?????? ?????? : ??? ?????? : {float(average_degree):.1f}???""")
    
    def convert_cv_qt(self, cv_img, size):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(size[0], size[1], Qt.KeepAspectRatio)

        return QPixmap.fromImage(p)
