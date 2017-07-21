import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pylab as plt

class AreaDetectorAnalysisWindow(QMainWindow):
    """Main window class"""
    def __init__(self, parent=None):
        super(AreaDetectorAnalysisWindow, self).__init__(parent)
        self.setGeometry(50, 50, 1024, 720)
        self.setWindowTitle("Area Data Analysis")
        self.setMinimumSize(824, 520)


def main():
    """Main method.
    """
    app = QApplication(sys.argv)
    areaDetector = AreaDetectorAnalysisWindow()
    areaDetector.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()