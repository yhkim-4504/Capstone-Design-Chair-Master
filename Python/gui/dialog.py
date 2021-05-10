from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QGridLayout, QPushButton, QDialog
from PyQt5.QtCore import Qt, QUrl
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