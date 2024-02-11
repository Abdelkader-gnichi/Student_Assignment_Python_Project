from PySide6.QtWidgets import QApplication
from login import LoginWindow
from PySide6 import QtUiTools
from PySide6.QtGui import *

import sys

if __name__ == "__main__":
    app = QApplication([])
    login_window = LoginWindow()
    login_window.show()
    app.exec()
