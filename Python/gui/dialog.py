from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QGridLayout, QPushButton, QDialog
from PyQt5.QtCore import Qt, QUrl
from PyQt5 import QtWebEngineWidgets

temp_url = "https://www.youtube.com/embed/HtQmxoWytIA"

url_list = {'turtle_neck': 'https://www.youtube.com/embed/Io5NYpzfsEU?start=37',
            'whole_body': 'https://www.youtube.com/embed/XZCJRfhYJ-w?start=39',
            'lower_body': 'https://www.youtube.com/embed/--MMq6I07b4?start=23',
            }

class YoutubeDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setWindowTitle('스트레칭 영상')
        self.setWindowModality(Qt.ApplicationModal)

        self.webview = QtWebEngineWidgets.QWebEngineView(self)
        self.webview.setUrl(QUrl(temp_url))
        self.webview.setGeometry(0, 0, 900, 600)

    def set_webview_url(self, url: str) -> None:
        self.webview.setUrl(QUrl(url))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.webview.setUrl(QUrl("about:blank"))
        return super().closeEvent(a0)


class GuideDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setWindowTitle('스트레칭 알림')
        self.setWindowModality(Qt.ApplicationModal)

        self.label = QLabel('여시겠습니까?')
        self.yes_btn = QPushButton('네!')
        self.no_btn = QPushButton('아니요..')

        layout = QGridLayout()
        layout.addWidget(self.label, 0, 0, 2, 4)
        layout.addWidget(self.yes_btn, 2, 0, 2, 2)
        layout.addWidget(self.no_btn, 2, 2, 2, 2)

        self.setLayout(layout)

    def set_label(self, text):
        self.label.setText(text)