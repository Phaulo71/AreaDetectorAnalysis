#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
#C In some methods LFit or L refer to the Lattice Constant not RLU
"""
# ---------------------------------------------------------------------------------------------------------------------#
from __future__ import unicode_literals
import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pylab as plt

# ---------------------------------------------------------------------------------------------------------------------#

class AreaDetectorAnalysisWindow(QMainWindow):
    """Main window class"""
    def __init__(self, parent=None):
        super(AreaDetectorAnalysisWindow, self).__init__(parent)
        self.setGeometry(50, 50, 1024, 720)
        self.setWindowTitle("Area Data Analysis")
        self.setMinimumSize(824, 520)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.createMenus()

        # File list widgets
        self.fileListTitle = QLabel("Image files to load")
        self.fileListBox = QListWidget()
        self.fileListBox.setFixedWidth(245)
        self.removeFileBtn = QPushButton("Remove")
        self.removeAllFileBtn = QPushButton("Remove All")

        vBox_file = QVBoxLayout()
        vBox_file.addWidget(self.fileListTitle, alignment=Qt.AlignCenter)
        vBox_file.addWidget(self.fileListBox)
        vBox_file.addWidget(self.removeFileBtn)
        vBox_file.addWidget(self.removeAllFileBtn)


        # Plot Figures and controls
        self.figure1 = plt.figure(1, figsize=(5, 4), dpi=100)
        self.figure2 = plt.figure(2, figsize=(5, 4), dpi=100)
        self.figure3 = plt.figure(3, figsize=(5, 4), dpi=100)
        self.canvas1 = FigureCanvas(self.figure1)
        self.canvas1.setParent(self.centralWidget)
        self.canvas2 = FigureCanvas(self.figure2)
        self.canvas2.setParent(self.centralWidget)
        self.canvas3 = FigureCanvas(self.figure3)
        self.canvas3.setParent(self.centralWidget)

        self.resetRoiBtn = QPushButton("Reset")
        self.sc_dxc = QSpinBox()
        self.sc_dyc = QSpinBox()
        self.sc_dxw = QSpinBox()
        self.sc_dyw = QSpinBox()
        self.sc_pxc = QSpinBox()
        self.sc_pyc = QSpinBox()
        self.sc_pxw = QSpinBox()
        self.sc_pyw = QSpinBox()
        self.sc_bxc = QSpinBox()
        self.sc_byc = QSpinBox()
        self.sc_bxw = QSpinBox()
        self.sc_byw = QSpinBox()
        self.sc_pln_order1 = QSpinBox()
        self.sc_pln_order1.setRange(1, 5)
        self.sc_pln_order1.setValue(1)
        self.sc_pln_order2 = QSpinBox()
        self.sc_pln_order2.setRange(1, 5)
        self.sc_pln_order2.setValue(1)
        self.hkl_H = QLineEdit()
        self.hkl_K = QLineEdit()
        self.hkl_L = QLineEdit()
        self.energy = QLineEdit()
        self.mon = QLineEdit()
        self.trans = QLineEdit()

        gLayout_control = QGridLayout()
        gLayout_control.addWidget(self.resetRoiBtn, 0, 0)
        gLayout_control.addWidget(QLabel("x_cen"), 0, 1, alignment=Qt.AlignCenter)
        gLayout_control.addWidget(QLabel("y_cen"), 0, 2, alignment=Qt.AlignCenter)
        gLayout_control.addWidget(QLabel("x_width"), 0, 3, alignment=Qt.AlignCenter)
        gLayout_control.addWidget(QLabel("y_width"), 0, 4, alignment=Qt.AlignCenter)
        gLayout_control.addWidget(QLabel("Data ROI"), 1, 0)
        gLayout_control.addWidget(self.sc_dxc, 1, 1)
        gLayout_control.addWidget(self.sc_dyc, 1, 2)
        gLayout_control.addWidget(self.sc_dxw, 1, 3)
        gLayout_control.addWidget(self.sc_dyw, 1, 4)
        gLayout_control.addWidget(QLabel("Peak Area"), 2, 0)
        gLayout_control.addWidget(self.sc_pxc, 2, 1)
        gLayout_control.addWidget(self.sc_pyc, 2, 2)
        gLayout_control.addWidget(self.sc_pxw, 2, 3)
        gLayout_control.addWidget(self.sc_pyw, 2, 4)
        gLayout_control.addWidget(QLabel("Bkgd Area"), 3, 0)
        gLayout_control.addWidget(self.sc_bxc, 3, 1)
        gLayout_control.addWidget(self.sc_byc, 3, 2)
        gLayout_control.addWidget(self.sc_bxw, 3, 3)
        gLayout_control.addWidget(self.sc_byw, 3, 4)

        hBox_pln = QHBoxLayout()
        hBox_pln.addWidget(QLabel("Bkgd Fit Order1"))
        hBox_pln.addWidget(self.sc_pln_order1)
        hBox_pln.addWidget(QLabel("Bkgd Fit Order2"))
        hBox_pln.addWidget(self.sc_pln_order2)
        gLayout_control.addLayout(hBox_pln, 4, 0, 1, 5)

        hBox_hkl1 = QHBoxLayout()
        hBox_hkl1.addWidget(QLabel("H"))
        hBox_hkl1.addWidget(self.hkl_H)
        hBox_hkl1.addWidget(QLabel("K"), alignment=Qt.AlignCenter)
        hBox_hkl1.addWidget(self.hkl_K)
        hBox_hkl1.addWidget(QLabel("L"), alignment=Qt.AlignCenter)
        hBox_hkl1.addWidget(self.hkl_L)
        gLayout_control.addLayout(hBox_hkl1, 5, 0, 1, 5)

        hBox_hkl2 = QHBoxLayout()
        hBox_hkl2.addWidget(QLabel("Energy"), alignment=Qt.AlignCenter)
        hBox_hkl2.addWidget(self.energy)
        hBox_hkl2.addWidget(QLabel("MON"), alignment=Qt.AlignCenter)
        hBox_hkl2.addWidget(self.mon)
        hBox_hkl2.addWidget(QLabel("Trans"), alignment=Qt.AlignCenter)
        hBox_hkl2.addWidget(self.trans)
        gLayout_control.addLayout(hBox_hkl2, 6, 0, 1, 5)

        gLayout = QGridLayout()
        gLayout.addWidget(self.canvas1, 0, 0)
        gLayout.addWidget(self.canvas2, 0, 1)
        gLayout.addWidget(self.canvas3, 1, 0)
        gLayout.addLayout(gLayout_control, 1, 1)

        # Save buttons
        self.saveAndNextBtn = QPushButton("Save and Next")
        self.saveBtn = QPushButton("Save")
        self.nextBtn = QPushButton("Next")
        self.saveAsBtn = QPushButton("Save As")

        hBox_save = QHBoxLayout()
        hBox_save.addWidget(self.saveAndNextBtn)
        hBox_save.addWidget(self.saveBtn)
        hBox_save.addWidget(self.nextBtn)
        hBox_save.addWidget(self.saveAsBtn)

        # Log display
        self.log = QTextEdit()
        self.log.setFixedHeight(140)

        vBox_right = QVBoxLayout()
        vBox_right.addLayout(gLayout)
        vBox_right.addWidget(self.log)
        vBox_right.addLayout(hBox_save)

        # Adding to the central widget
        hBox_central = QHBoxLayout()
        hBox_central.addLayout(vBox_file)
        hBox_central.addLayout(vBox_right)

        self.centralWidget.setLayout(hBox_central)

    def createMenus(self):
        self.mainMenu = QMenuBar()
        self.fileMenu = self.mainMenu.addMenu("File")
        self.optionsMenu = self.mainMenu.addMenu("Options")
        self.setMenuBar(self.mainMenu)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('Ready', 3000)

        # self.createActions()
        # self.fileMenu.addAction(self.openImagesAction)


    def createActions(self):
        """Function that creates the actions used in the menu bar
        """
        self.openImagesAction = QAction('Open Images', statusTip= 'List up the image files to open.',
                                  triggered=self.OnOpenImage)

        self.readMetadataAction = QAction('Read Metadata', statusTip='Read a metadata file.',
                                        triggered=self.OnReadMetaData)
        self.saveAction = QAction("Save", statusTip="Save the result.",
                                         triggered=self.OnSave)
        self.nextAction = QAction("Next", statusTip="Go to the next image.",
                                         triggered=self.OnNext)
        self.saveAndNextAction = QAction("Save and Next", statusTip="Save the result and go to the next image.",
                                         triggered=self.OnSaveNext)
        self.exitAction = QAction("Exit", statusTip="Exits the program.", triggered=self.OnExit)

    def OnOpenImage(self):
        print "Not ready, yet."

    def OnReadMetaData(self):
        print "Not ready, yet."

    def OnSaveNext(self):
        print "Not ready, yet."

    def OnExit(self):
        print "Not ready, yet."





def main():
    """Main method.
    """
    app = QApplication(sys.argv)
    areaDetector = AreaDetectorAnalysisWindow()
    areaDetector.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()