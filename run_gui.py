import sys
from Python.gui_app import GuiApp
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui_app = GuiApp()
    sys.exit(app.exec_())