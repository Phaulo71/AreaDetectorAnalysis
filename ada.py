#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
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
from PIL import Image
import numpy as np
import time
from matplotlib.patches import Rectangle
from areaData import AreaData
from specReader import ReadSpec
import csv

# ---------------------------------------------------------------------------------------------------------------------#
class RedirectText(QObject):
    def __init__(self, log):
        self.out = log

    def write(self, string):
        self.out.insertPlainText(string)


class AreaDetectorAnalysisWindow(QMainWindow):
    """Main window class"""
    def __init__(self, parent=None):
        super(AreaDetectorAnalysisWindow, self).__init__(parent)
        self.setGeometry(50, 50, 1500, 800)
        self.setWindowTitle("Area Data Analysis")
        self.setMinimumSize(1000, 650)
        self.readSpec = ReadSpec(self)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.workDirOpen = False
        self.createMenus()
        self.ControlDockWidget()

        self.fileList = []
        self.yPixelData = []
        self.xPixelData = []
        self.imgIndx = -1
        self.is_metadata_read = False
        self.imgArray = np.array(0)
        self.savedatafile = None
        self.bad_pixels_on = False
        self.bad_pixels = []
        self.replacing_pixels = []
        self.efficiency_on = False
        self.mouse1_is_pressed = False
        self.dir = None

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
        self.figure4 = plt.figure(4, figsize=(5, 4), dpi=100)
        self.figure5 = plt.figure(5, figsize=(5, 4), dpi=100)
        self.canvas1 = FigureCanvas(self.figure1)
        self.canvas1.setParent(self.centralWidget)
        self.canvas2 = FigureCanvas(self.figure2)
        self.canvas2.setParent(self.centralWidget)
        self.canvas3 = FigureCanvas(self.figure3)
        self.canvas3.setParent(self.centralWidget)

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        gLayout = QGridLayout()
        gLayout.addWidget(self.canvas1, 0, 0)
        gLayout.addWidget(self.log, 0, 1)
        gLayout.addWidget(self.canvas2, 1, 0)
        gLayout.addWidget(self.canvas3, 1, 1)


        vBox_right = QVBoxLayout()
        vBox_right.addLayout(gLayout)

        # Adding to the central widget
        hBox_central = QHBoxLayout()
        hBox_central.addLayout(vBox_file)
        hBox_central.addLayout(vBox_right)

        self.centralWidget.setLayout(hBox_central)

        self.fileListBox.itemDoubleClicked.connect(self.OnListSelected)
        self.removeFileBtn.clicked.connect(self.OnRemoveFile)
        self.removeAllFileBtn.clicked.connect(self.OnRemoveAllFiles)
        self.canvas1.mpl_connect('motion_notify_event', self.OnMouseMove)
        self.canvas1.mpl_connect('button_press_event', self.OnMousePress)
        self.canvas1.mpl_connect('button_release_event', self.OnMouseRelease)

        redir = RedirectText(self.log)
        sys.stdout = redir
        redir2 = RedirectText(self.log)
        sys.stderr = redir2

        print("AreaDetectorAnalysis: " + time.ctime())

    def ControlDockWidget(self):
        self.controlDockWidget = QDockWidget("Controls", self)
        self.controlDockWidget.setMaximumWidth(280)
        self.controlDockWidget.setMinimumWidth(280)
        self.controlDockWidget.setAllowedAreas(Qt.RightDockWidgetArea)

        # Controls
        self.resetRoiBtn = QPushButton("Reset")
        self.sc_dxc = QSpinBox()
        self.sc_dxc.setMaximumSize(65, 30)
        self.sc_dyc = QSpinBox()
        self.sc_dyc.setMaximumSize(65, 30)
        self.sc_dxw = QSpinBox()
        self.sc_dxw.setMaximumSize(65, 30)
        self.sc_dyw = QSpinBox()
        self.sc_dyw.setMaximumSize(65, 30)
        self.sc_pxc = QSpinBox()
        self.sc_pxc.setMaximumSize(65, 30)
        self.sc_pyc = QSpinBox()
        self.sc_pyc.setMaximumSize(65, 30)
        self.sc_pxw = QSpinBox()
        self.sc_pxw.setMaximumSize(65, 30)
        self.sc_pyw = QSpinBox()
        self.sc_pyw.setMaximumSize(65, 30)
        self.sc_bxc = QSpinBox()
        self.sc_bxc.setMaximumSize(65, 30)
        self.sc_byc = QSpinBox()
        self.sc_byc.setMaximumSize(65, 30)
        self.sc_bxw = QSpinBox()
        self.sc_bxw.setMaximumSize(65, 30)
        self.sc_byw = QSpinBox()
        self.sc_byw.setMaximumSize(65, 30)
        self.sc_pln_order1 = QSpinBox()
        self.sc_pln_order1.setRange(1, 5)
        self.sc_pln_order1.setValue(1)
        self.sc_pln_order2 = QSpinBox()
        self.sc_pln_order2.setRange(1, 5)
        self.sc_pln_order2.setValue(1)
        spacer = QFrame()
        spacer.setFrameShape(QFrame.HLine)
        spacer1 = QFrame()
        spacer1.setFrameShape(QFrame.HLine)
        spacer2 = QFrame()
        spacer2.setFrameShape(QFrame.HLine)
        spacer3 = QFrame()
        spacer3.setFrameShape(QFrame.HLine)
        spacer4 = QFrame()
        spacer4.setFrameShape(QFrame.HLine)
        spacer5 = QFrame()
        spacer5.setFrameShape(QFrame.HLine)

        self.sl_dxc = QSlider(Qt.Horizontal)
        self.sl_dxc.setTickInterval(3)
        self.sl_dxc.valueChanged.connect(self.sc_dxc.setValue)
        self.sl_dyc = QSlider(Qt.Horizontal)
        self.sl_dyc.valueChanged.connect(self.sc_dyc.setValue)
        self.sl_dxw = QSlider(Qt.Horizontal)
        self.sl_dxw.valueChanged.connect(self.sc_dxw.setValue)
        self.sl_dyw = QSlider(Qt.Horizontal)
        self.sl_dyw.valueChanged.connect(self.sc_dyw.setValue)
        self.sl_pxc = QSlider(Qt.Horizontal)
        self.sl_pxc.valueChanged.connect(self.sc_pxc.setValue)
        self.sl_pyc = QSlider(Qt.Horizontal)
        self.sl_pyc.valueChanged.connect(self.sc_pyc.setValue)
        self.sl_pxw = QSlider(Qt.Horizontal)
        self.sl_pxw.valueChanged.connect(self.sc_pxw.setValue)
        self.sl_pyw = QSlider(Qt.Horizontal)
        self.sl_pyw.valueChanged.connect(self.sc_pyw.setValue)
        self.sl_bxc = QSlider(Qt.Horizontal)
        self.sl_bxc.valueChanged.connect(self.sc_bxc.setValue)
        self.sl_byc = QSlider(Qt.Horizontal)
        self.sl_byc.valueChanged.connect(self.sc_byc.setValue)
        self.sl_bxw = QSlider(Qt.Horizontal)
        self.sl_bxw.valueChanged.connect(self.sc_bxw.setValue)
        self.sl_byw = QSlider(Qt.Horizontal)
        self.sl_byw.valueChanged.connect(self.sc_byw.setValue)

        # Signal and slots for the SpinBoxs
        self.sc_dxc.valueChanged.connect(self.sl_dxc.setValue)
        self.sc_dyc.valueChanged.connect(self.sl_dyc.setValue)
        self.sc_dxw.valueChanged.connect(self.sl_dxw.setValue)
        self.sc_dyw.valueChanged.connect(self.sl_dyw.setValue)
        self.sc_pxc.valueChanged.connect(self.sl_pxc.setValue)
        self.sc_pyc.valueChanged.connect(self.sl_pyc.setValue)
        self.sc_pxw.valueChanged.connect(self.sl_pxw.setValue)
        self.sc_pyw.valueChanged.connect(self.sl_pyw.setValue)
        self.sc_bxc.valueChanged.connect(self.sl_bxc.setValue)
        self.sc_byc.valueChanged.connect(self.sl_byc.setValue)
        self.sc_bxw.valueChanged.connect(self.sl_bxw.setValue)
        self.sc_byw.valueChanged.connect(self.sl_byw.setValue)

        # Redrawing image
        self.sc_dxc.valueChanged.connect(self.RedrawImage)
        self.sc_dyc.valueChanged.connect(self.RedrawImage)
        self.sc_dxw.valueChanged.connect(self.RedrawImage)
        self.sc_dyw.valueChanged.connect(self.RedrawImage)
        self.sc_pxc.valueChanged.connect(self.RedrawImage)
        self.sc_pyc.valueChanged.connect(self.RedrawImage)
        self.sc_pxw.valueChanged.connect(self.RedrawImage)
        self.sc_pyw.valueChanged.connect(self.RedrawImage)
        self.sc_bxc.valueChanged.connect(self.RedrawImage)
        self.sc_byc.valueChanged.connect(self.RedrawImage)
        self.sc_bxw.valueChanged.connect(self.RedrawImage)
        self.sc_byw.valueChanged.connect(self.RedrawImage)

        self.resetRoiBtn.clicked.connect(self.OnResetDataROI)

        vROI_Layout = QVBoxLayout()
        ROI_Label = QLabel("Data ROI")
        ROI_Label.setMaximumHeight(15)
        h1Layout = QHBoxLayout()
        h1Layout.addWidget(QLabel("x_cen:"))
        h1Layout.addWidget(self.sc_dxc)
        h1Layout.addWidget(self.sl_dxc)
        h2Layout = QHBoxLayout()
        h2Layout.addWidget(QLabel("y_cen:"))
        h2Layout.addWidget(self.sc_dyc)
        h2Layout.addWidget(self.sl_dyc)
        h3Layout = QHBoxLayout()
        h3Layout.addWidget(QLabel("x_wid:"))
        h3Layout.addWidget(self.sc_dxw)
        h3Layout.addWidget(self.sl_dxw)
        h4Layout = QHBoxLayout()
        h4Layout.addWidget(QLabel("y_wid:"))
        h4Layout.addWidget(self.sc_dyw)
        h4Layout.addWidget(self.sl_dyw)
        vROI_Layout.addWidget(spacer)
        vROI_Layout.addWidget(ROI_Label)
        vROI_Layout.addLayout(h1Layout)
        vROI_Layout.addLayout(h2Layout)
        vROI_Layout.addLayout(h3Layout)
        vROI_Layout.addLayout(h4Layout)

        vPeak_Layout = QVBoxLayout()
        Peak_Label = QLabel("Peak Area")
        Peak_Label.setMaximumHeight(15)
        h5Layout = QHBoxLayout()
        h5Layout.addWidget(QLabel("x_cen:"))
        h5Layout.addWidget(self.sc_pxc)
        h5Layout.addWidget(self.sl_pxc)
        h6Layout = QHBoxLayout()
        h6Layout.addWidget(QLabel("y_cen:"))
        h6Layout.addWidget(self.sc_pyc)
        h6Layout.addWidget(self.sl_pyc)
        h7Layout = QHBoxLayout()
        h7Layout.addWidget(QLabel("x_wid:"))
        h7Layout.addWidget(self.sc_pxw)
        h7Layout.addWidget(self.sl_pxw)
        h8Layout = QHBoxLayout()
        h8Layout.addWidget(QLabel("y_wid:"))
        h8Layout.addWidget(self.sc_pyw)
        h8Layout.addWidget(self.sl_pyw)
        vPeak_Layout.addWidget(spacer1)
        vPeak_Layout.addWidget(Peak_Label)
        vPeak_Layout.addLayout(h5Layout)
        vPeak_Layout.addLayout(h6Layout)
        vPeak_Layout.addLayout(h7Layout)
        vPeak_Layout.addLayout(h8Layout)

        vBkgd_Layout = QVBoxLayout()
        Bkgd_Label = QLabel("Background Area")
        Bkgd_Label.setMaximumHeight(15)
        h9Layout = QHBoxLayout()
        h9Layout.addWidget(QLabel("x_cen:"))
        h9Layout.addWidget(self.sc_bxc)
        h9Layout.addWidget(self.sl_bxc)
        h10Layout = QHBoxLayout()
        h10Layout.addWidget(QLabel("y_cen:"))
        h10Layout.addWidget(self.sc_byc)
        h10Layout.addWidget(self.sl_byc)
        h11Layout = QHBoxLayout()
        h11Layout.addWidget(QLabel("x_wid:"))
        h11Layout.addWidget(self.sc_bxw)
        h11Layout.addWidget(self.sl_bxw)
        h12Layout = QHBoxLayout()
        h12Layout.addWidget(QLabel("y_wid:"))
        h12Layout.addWidget(self.sc_byw)
        h12Layout.addWidget(self.sl_byw)
        vBkgd_Layout.addWidget(spacer2)
        vBkgd_Layout.addWidget(Bkgd_Label)
        vBkgd_Layout.addLayout(h9Layout)
        vBkgd_Layout.addLayout(h10Layout)
        vBkgd_Layout.addLayout(h11Layout)
        vBkgd_Layout.addLayout(h12Layout)
        vBkgd_Layout.addWidget(spacer3)

        vBox_pln = QVBoxLayout()
        hBox_pln1 = QHBoxLayout()
        hBox_pln1.addWidget(QLabel("Background Fit Order 1:"))
        hBox_pln1.addWidget(self.sc_pln_order1)
        hBox_pln2 = QHBoxLayout()
        hBox_pln2.addWidget(QLabel("Background Fit Order 2:"))
        hBox_pln2.addWidget(self.sc_pln_order2)
        vBox_pln.addLayout(hBox_pln1)
        vBox_pln.addLayout(hBox_pln2)
        vBox_pln.addWidget(spacer4)

        self.saveAndNextBtn = QPushButton("Save and Next")
        self.saveBtn = QPushButton("Save")
        self.nextBtn = QPushButton("Next")
        self.saveAsBtn = QPushButton("Save As")

        #  Save buttons
        hBox_save1 = QHBoxLayout()
        hBox_save2 = QHBoxLayout()
        hBox_save1.addWidget(self.saveBtn)
        hBox_save1.addWidget(self.nextBtn)
        hBox_save2.addWidget(self.saveAsBtn)
        hBox_save2.addWidget(self.saveAndNextBtn)
        self.saveAsBtn.clicked.connect(self.OnSaveAs)
        self.saveBtn.clicked.connect(self.OnSave)
        self.nextBtn.clicked.connect(self.OnNext)
        self.saveAndNextBtn.clicked.connect(self.OnSaveNext)
        dockLayout = QVBoxLayout()

        if self.workDirOpen == False:
            dockLayout.addLayout(vROI_Layout)
            dockLayout.addLayout(vPeak_Layout)
            dockLayout.addLayout(vBkgd_Layout)
            dockLayout.addLayout(vBox_pln)
            dockLayout.addWidget(self.resetRoiBtn)
            dockLayout.addLayout(hBox_save1)
            dockLayout.addLayout(hBox_save2)
            dockLayout.addStretch(1)
        elif self.workDirOpen == True:
            dockLayout.addLayout(vROI_Layout)
            dockLayout.addLayout(vPeak_Layout)
            dockLayout.addLayout(vBkgd_Layout)
            dockLayout.addLayout(vBox_pln)
            dockLayout.addLayout(self.readSpec.SpecDataInfo())
            dockLayout.addWidget(self.resetRoiBtn)
            dockLayout.addLayout(hBox_save1)
            dockLayout.addLayout(hBox_save2)
            dockLayout.addStretch(1)

        widget = QWidget()
        widget.setLayout(dockLayout)
        self.controlDockWidget.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.controlDockWidget)

    def createMenus(self):
        self.mainMenu = QMenuBar()
        self.fileMenu = self.mainMenu.addMenu("File")
        self.optionsMenu = self.mainMenu.addMenu("Options")
        self.badPixelsMenu = self.optionsMenu.addMenu("Bad Pixels")
        self.flatfieldMenu = self.optionsMenu.addMenu("Flatfield Correction")
        self.setMenuBar(self.mainMenu)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('Ready', 3000)

        self.createActions()
        self.fileMenu.addAction(self.openWorkDirAction)
        self.fileMenu.addAction(self.nextAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addAction(self.saveAndNextAction)
        self.exportMenu = self.fileMenu.addMenu("Export")
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)
        self.exportMenu.addAction(self.pixelDataAction)
        self.badPixelsMenu.addAction(self.badPixelsOnAction)
        self.badPixelsMenu.addAction(self.badPixelsOffAction)
        self.flatfieldMenu.addAction(self.flatfieldOnAction)
        self.flatfieldMenu.addAction(self.badPixelsOffAction)


    def createActions(self):
        """Function that creates the actions used in the menu bar
        """
        self.openWorkDirAction = QAction('Open Work Directory', self)
        self.openWorkDirAction.setStatusTip('Open the directory with the images and spec file.')
        self.openWorkDirAction.triggered.connect(self.OnOpenWorkDir)


        self.saveAsAction = QAction("Save As", self)
        self.saveAsAction.setStatusTip("Save the result.")
        self.saveAsAction.triggered.connect(self.OnSaveAs)

        self.saveAction = QAction("Save", self)
        self.saveAction.setStatusTip("Save the result.")
        self.saveAction.triggered.connect(self.OnSave)

        self.nextAction = QAction("Next", self)
        self.nextAction.setStatusTip("Go to the next image.")
        self.nextAction.triggered.connect(self.OnNext)

        self.saveAndNextAction = QAction("Save and Next", self)
        self.saveAndNextAction.setStatusTip("Save the result and go to the next image.")
        self.saveAndNextAction.triggered.connect(self.OnSaveNext)

        self.exitAction = QAction("Exit", self)
        self.exitAction.setStatusTip("Exits the program.")
        self.exitAction.triggered.connect(self.OnExit)

        self.pixelDataAction = QAction("Pixel Data", self)
        self.pixelDataAction.setStatusTip("Exports file with pixel data.")
        self.pixelDataAction.triggered.connect(self.PixelDataDialog)

        self.badPixelsOnAction = QAction("On", self)
        self.badPixelsOnAction.setStatusTip("Toggle on, bad pixel correction.")
        self.badPixelsOnAction.triggered.connect(self.OnBadPixelCorrection)

        self.badPixelsOffAction = QAction("Off", self)
        self.badPixelsOffAction.setStatusTip("Toggle off, bad pixel correction.")
        self.badPixelsOffAction.triggered.connect(self.OffBadPixelCorrection)

        self.flatfieldOnAction = QAction("On", self)
        self.flatfieldOnAction.setStatusTip("Toggle on, pixel by pixel efficiency correction")
        self.flatfieldOnAction.triggered.connect(self.OnFlatfieldCorrection)

        self.flatfieldOffAction = QAction("On", self)
        self.flatfieldOffAction.setStatusTip("Toggle off, pixel by pixel efficiency correction")
        self.flatfieldOffAction.triggered.connect(self.OffFlatfieldCorrection)

    def OnOpenWorkDir(self):
        try:
            self.fileList = []
            self.imgList = []

            self.dir = QFileDialog.getExistingDirectory(caption="Choose work directory")

            if os.path.isdir(self.dir):
                items = os.listdir(self.dir)

                for item in items:
                    if self.dir.find("/") == 0:
                        path = self.dir + '/' + item
                    elif self.dir.find("\\") == 0:
                        path = self.dir + '\\' + item
                    if os.path.isdir(path):
                        imgDir = path
                    elif os.path.isfile(path):
                        specFile = path


                images = os.listdir(imgDir)
                for img in images:
                    self.fileListBox.addItem(img)
                    self.imgList.append(img)
                    if self.dir.find("/") == 0:
                        self.fileList.append(imgDir + '/' + img)
                    elif self.dir.find("\\") == 0:
                        self.fileList.append(imgDir + '\\' + img)

                self.workDirOpen = True
                self.readSpec.loadSpec(specFile, imgDir)
        except:
            QMessageBox.warning(self, "Error", "Please make sure the work directory follows the correct format.\n\n"
                                "Directory should contain:\n\n" "1. Folder with images\n2. Spec file"
                                "\n\nNote: The images folder should be named the number of the scan. For example 64.")
            self.fileListBox.clear()
            self.fileList = []
            self.imgList = []


    def OnSaveAs(self):
        """Ask Jong what he wants to save"""
        print "Not ready, yet."

    def OnSave(self):
        """Ask Jong what he wants to save."""
        print "Not ready, yet."

    def OnNext(self):
        print self.fileListBox.count()
        indx = self.imgIndx + 1
        print indx
        self.fileListBox.setCurrentRow(indx)
        self.OnListSelected()

    def OnSaveNext(self):
        self.OnSave()
        self.OnNext()

    def OnExit(self):
        self.close()

    def OnBadPixelCorrection(self):
        """Ask Jong what file is required for this"""
        print "Not ready, yet"

    def OffBadPixelCorrection(self):
        self.bad_pixels_on = False

    def OnFlatfieldCorrection(self):
        """ Ask Jong what file is needed here."""
        print "Not ready, yet"

    def OffFlatfieldCorrection(self):
        self.efficiency_on = False

    def OnListSelected(self):
        self.imgIndx = self.fileListBox.currentRow()
        self.curimg = Image.open(self.fileList[self.imgIndx])
        self.imgArray = np.array(self.curimg)

        self.readSpec.getSpecData(self.imgIndx)

        if self.efficiency_on == True:
            self.imgArray = self.imarray / self.efficiencyarray

        if self.bad_pixels_on == True:
            for i in range(len(self.bad_pixels)):
                self.imgArray[self.bad_pixels[i][1], self.bad_pixels[i][0]] = \
                    self.imgArray[self.replacing_pixels[i][1], self.replacing_pixels[i][0]]

        self.RedrawImage()

    def RedrawImage(self):
        try:
            if self.imgArray.any():
                self.resetRoiRange()
                ih, iw = self.imgArray.shape
                droi, proi, broi = self.getRoiValues()

                if droi == (0, 0, 0, 0):
                    self.sc_dxc.setValue(iw / 2)
                    self.sc_dyc.setValue(ih / 2)
                    self.sc_dxw.setValue(iw)
                    self.sc_dyw.setValue(ih)
                    droi, proi, broi = self.getRoiValues()

                boundsError = self.checkingBounds()
                if boundsError == False:
                    h, bins = np.histogram(self.imgArray)
                    vmin = bins[0]
                    vmax = bins[-1]
                    dxlim = [droi[0] - droi[2] / 2. - 0.5, droi[0] + droi[2] / 2. + 0.5]
                    dylim = [droi[1] + droi[3] / 2. - 0.5, droi[1] - droi[3] / 2. + 0.5]
                    px = [proi[0] - proi[2] / 2., proi[0] + proi[2] / 2., proi[0] + proi[2] / 2., proi[0] - proi[2] / 2.,
                          proi[0] - proi[2] / 2.]
                    py = [proi[1] - proi[3] / 2., proi[1] - proi[3] / 2., proi[1] + proi[3] / 2., proi[1] + proi[3] / 2.,
                          proi[1] - proi[3] / 2.]
                    bx = [broi[0] - broi[2] / 2., broi[0] + broi[2] / 2., broi[0] + broi[2] / 2., broi[0] - broi[2] / 2.,
                          broi[0] - broi[2] / 2.]
                    by = [broi[1] - broi[3] / 2., broi[1] - broi[3] / 2., broi[1] + broi[3] / 2., broi[1] + broi[3] / 2.,
                          broi[1] - broi[3] / 2.]
                    self.figure1.clear()
                    ax = self.figure1.add_subplot(111)
                    ax.imshow(self.imgArray, interpolation='none', vmin=vmin, vmax=vmax)
                    ax.set_xlim(dxlim)
                    ax.set_ylim(dylim)
                    ax.plot(px, py, 'y-', linewidth=1.0)
                    ax.plot(bx, by, 'g-', linewidth=1.0)
                    self.canvas1.draw()

                    if (0 in proi) or (0 in broi):
                        pass
                    else:
                        self.areaIntegrationShow(self.imgArray, droi, proi, broi)
        except IndexError:
            print "Make sure to stay in between the pictures bounds."

    def checkingBounds(self):
        droi, proi, broi = self.getRoiValues()
        print proi
        print broi
        pxc = proi[0]
        pyc = proi[1]
        pxw = proi[2]
        pyw = proi[3]
        bxc = broi[0]
        byc = broi[1]
        bxw = broi[2]
        byw = broi[3]
        print  pxc - pxw / 2

        if pxc - pxw / 2 < bxc - bxw / 2 or pxc + pxw / 2 > bxc + bxw / 2 or pyc - pyw / 2 < byc - byw / 2 or\
                                pyc + pyw / 2 > byc + byw / 2:
            print "True"
            return True
        else:
            print "False"
            return False

    def checkingValue(self):
        error = self.checkingBounds()

        if error == False:
            pass

    def OnRemoveFile(self):
        if len(self.fileList) != 0:
            indx = self.fileListBox.currentRow()
            self.fileListBox.takeItem(indx)
            self.fileList.remove(self.fileList[indx])
            self.imgList.pop(indx)

            for n in self.readSpec.specInfoValue:
                if isinstance(n, list):
                    n.pop(indx)


    def OnRemoveAllFiles(self):
        if len(self.fileList) != 0:
            self.fileListBox.clear()
            self.fileList = []

    def OnResetDataROI(self):
        if self.imgArray.any():
            ih, iw = self.imgArray.shape
            print ih, iw
            self.sc_dxc.setRange(0, iw)
            self.sc_dxc.setValue(iw / 2)
            self.sc_dyc.setRange(0, ih)
            self.sc_dyc.setValue(ih / 2)
            self.sc_dxw.setRange(0, iw)
            self.sc_dxw.setValue(iw)
            self.sc_dyw.setRange(0, ih)
            self.sc_dyw.setValue(ih)
            self.sl_dxc.setRange(0, iw)
            self.sl_dxc.setValue(iw / 2)
            self.sl_dyc.setRange(0, ih)
            self.sl_dyc.setValue(ih / 2)
            self.sl_dxw.setRange(0, iw)
            self.sl_dxw.setValue(iw)
            self.sl_dyw.setRange(0, ih)
            self.sl_dyw.setValue(ih)
            self.RedrawImage()

    def resetRoiRange(self):
        ih, iw = self.imgArray.shape
        self.sc_dxc.setRange(0, iw)
        self.sc_dyc.setRange(0, ih)
        self.sc_dxw.setRange(0, iw)
        self.sc_dyw.setRange(0, ih)
        self.sc_pxc.setRange(0, iw)
        self.sc_pyc.setRange(0, ih)
        self.sc_pxw.setRange(0, iw)
        self.sc_pyw.setRange(0, ih)
        self.sc_bxc.setRange(0, iw)
        self.sc_byc.setRange(0, ih)
        self.sc_bxw.setRange(0, iw)
        self.sc_byw.setRange(0, ih)
        self.sl_dxc.setRange(0, iw)
        self.sl_dyc.setRange(0, ih)
        self.sl_dxw.setRange(0, iw)
        self.sl_dyw.setRange(0, ih)
        self.sl_pxc.setRange(0, iw)
        self.sl_pyc.setRange(0, ih)
        self.sl_pxw.setRange(0, iw)
        self.sl_pyw.setRange(0, ih)
        self.sl_bxc.setRange(0, iw)
        self.sl_byc.setRange(0, ih)
        self.sl_bxw.setRange(0, iw)
        self.sl_byw.setRange(0, ih)

    def areaIntegrationShow(self, lum_img, droi, proi, broi):
        self.yPixelData = []
        self.xPixelData = []
        self.imageName = self.imgList[self.imgIndx]
        areadata = AreaData(lum_img, droi, proi, broi)  #
        self.I2d, self.sigI2d = areadata.areaIntegral()
        xb2, yb2, yb2_err, yb2_pln, self.I1d1, self.sigI1d1 = areadata.lineIntegral(1, self.sc_pln_order2.value())
        xb3, yb3, yb3_err, yb3_pln, self.I1d0, self.sigI1d0 = areadata.lineIntegral(0, self.sc_pln_order1.value())
        # plot in canvas2
        self.figure2.clear()
        self.figure2.add_subplot(111)
        ax2 = self.figure2.gca()
        ax2.errorbar(xb2, yb2, yerr=yb2_err, fmt='ro-', capsize=2.0)
        ax2.plot(xb2, yb2_pln, 'bo--', markerfacecolor='none')
        self.yPixelData.append(xb2)
        self.yPixelData.append(yb2)
        ax2.set_title("1D Integration(2)", fontsize=10)
        ax2.set_xlabel("y (pixel)")
        ax2.set_ylabel("Int. (counts)")
        self.figure2.tight_layout()
        self.canvas2.draw()
        # plot in canvas3
        self.figure3.clear()
        self.figure3.add_subplot(111)
        ax3 = self.figure3.gca()
        ax3.errorbar(xb3, yb3, yerr=yb3_err, fmt='ro-', capsize=2.0)
        ax3.plot(xb3, yb3_pln, 'bo--', markerfacecolor='none')
        self.xPixelData.append(xb3)
        self.xPixelData.append(yb3)
        ax3.set_title("1D Integration(1)", fontsize=10)
        ax3.set_xlabel("x (pixel)")
        ax3.set_ylabel("Int. (counts)")
        self.figure3.tight_layout()
        self.canvas3.draw()

    def getRoiValues(self):
        dxc = self.sc_dxc.value()
        dyc = self.sc_dyc.value()
        dxw = self.sc_dxw.value()
        dyw = self.sc_dyw.value()
        pxc = self.sc_pxc.value()
        pyc = self.sc_pyc.value()
        pxw = self.sc_pxw.value()
        pyw = self.sc_pyw.value()
        bxc = self.sc_bxc.value()
        byc = self.sc_byc.value()
        bxw = self.sc_bxw.value()
        byw = self.sc_byw.value()
        return (dxc, dyc, dxw, dyw), (pxc, pyc, pxw, pyw), (bxc, byc, bxw, byw)

    def OnMouseMove(self, event):
        if self.imgArray.any():
            if event.inaxes:
                ix, iy = event.xdata, event.ydata
                iz = self.imgArray[np.int(round(iy)), np.int(round(ix))]
                self.setStatusTip("p=(" + str(int(round(ix))) + ', ' + str(int(round(iy))) + "), I=" + str(iz))
                if self.mouse1_is_pressed == True:
                    xw = ix - self.mousex0
                    yw = iy - self.mousey0
                    ax = self.figure1.gca()
                    rect = Rectangle((self.mousex0, self.mousey0), xw, yw, linestyle='solid', color='magenta',
                                     fill=True, alpha=0.4)
                    ax.add_patch(rect)
                    for item in ax.findobj(match=Rectangle)[:-2]:
                        item.remove()
                    self.canvas1.draw()

    def OnMousePress(self, event):
        if event.button == 1 and event.inaxes:
            self.mouse1_is_pressed = True
            self.mousex0 = event.xdata
            self.mousey0 = event.ydata
        elif event.button == 3 and event.xdata and event.ydata:
            self.mouse3_is_pressed = True
        else:
            pass

    def OnMouseRelease(self, event):
        try:
            if event.button == 1 and event.inaxes:
                self.mouse1_is_pressed = False
                self.mousex1 = event.xdata
                self.mousey1 = event.ydata
                self.sc_dxc.setValue(int(abs(self.mousex1 + self.mousex0) / 2))
                self.sc_dyc.setValue(int(abs(self.mousey1 + self.mousey0) / 2))
                self.sc_pxc.setValue(int(abs(self.mousex1 + self.mousex0) / 2))
                self.sc_pyc.setValue(int(abs(self.mousey1 + self.mousey0) / 2))
                self.sc_bxc.setValue(int(abs(self.mousex1 + self.mousex0) / 2))
                self.sc_byc.setValue(int(abs(self.mousey1 + self.mousey0) / 2))

                if abs(self.mousex1 - self.mousex0) < 1 or abs(self.mousey1 - self.mousey0) < 1:
                    pass
                else:
                    self.sc_dxw.setValue(int(abs(self.mousex1 - self.mousex0)))
                    self.sc_dyw.setValue(int(abs(self.mousey1 - self.mousey0)))
                    self.sc_pxw.setValue(int(abs(self.mousex1 - self.mousex0) * 0.3))
                    self.sc_pyw.setValue(int(abs(self.mousey1 - self.mousey0) * 0.3))
                    self.sc_bxw.setValue(int(abs(self.mousex1 - self.mousex0) * 0.6))
                    self.sc_byw.setValue(int(abs(self.mousey1 - self.mousey0) * 0.6))
            elif event.button == 3:
                self.mouse3_is_pressed = False
                self.sc_dxw.setValue(self.sc_dxw.GetValue() * 1.25)
                self.sc_dyw.setValue(self.sc_dyw.GetValue() * 1.25)
            self.RedrawImage()
        except:
            print "Error"

    def PixelDataDialog(self):
        self.pixelDataDialog = QDialog(self)
        dialogBox = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        vBox = QVBoxLayout()

        groupBox = QGroupBox("Select pixel data")

        self.xPixelReportCb = QRadioButton("X pixel")
        self.yPixelReportCb = QRadioButton("Y pixel")
        self.allPixelReportCb = QRadioButton("X && Y pixels")

        vBox.addWidget(self.xPixelReportCb)
        vBox.addWidget(self.yPixelReportCb)
        vBox.addWidget(self.allPixelReportCb)
        groupBox.setLayout(vBox)

        ok = QPushButton("Ok")
        cancel = QPushButton('Cancel')

        ok.clicked.connect(self.CreatePixelReport)
        cancel.clicked.connect(self.pixelDataDialog.close)

        buttonLayout.addWidget(cancel)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(ok)

        dialogBox.addWidget(groupBox)
        dialogBox.addLayout(buttonLayout)

        self.pixelDataDialog.setWindowTitle("Export Pixel Data")
        self.pixelDataDialog.setLayout(dialogBox)
        self.pixelDataDialog.resize(200, 50)
        self.pixelDataDialog.exec_()

    def CreatePixelReport(self):
        if len(self.xPixelData) != 0:
            if self.xPixelReportCb.isChecked() or self.yPixelReportCb.isChecked() or self.allPixelReportCb.isChecked():
                self.reportFile, self.reportFileFilter = QFileDialog.getSaveFileName(self, "Save Report", "",
                                                                                     ".txt")
                if self.reportFile != "":
                    self.reportFile += self.reportFileFilter
                    self.PrintPixelReport()
                    self.pixelDataDialog.close()


    def PrintPixelReport(self):
            if len(self.xPixelData[0]) >= len(self.yPixelData[0]):
                maxLength = len(self.xPixelData[0])
            elif len(self.xPixelData[0]) < len(self.yPixelData[0]):
                maxLength = len(self.yPixelData[0])

            reportData = []
            header = "#H "

            if self.xPixelReportCb.isChecked() or self.allPixelReportCb.isChecked():
                header += "xPixel xCount "
                reportData.append(self.xPixelData[0])
                reportData.append(self.xPixelData[1])

            if self.yPixelReportCb.isChecked() or self.allPixelReportCb.isChecked():
                header += "yPixel yCount"
                reportData.append(self.yPixelData[0])
                reportData.append(self.yPixelData[1])

            # Writes to sheet
            file = open(self.reportFile, "w")
            file.write("#C " + self.imageName + "\n")
            file.write(header + "\n")
            j = 0
            while j < maxLength:
                string = ''
                for s in reportData:
                    if len(s) > j:
                        string += "{:5}".format(str(s[j])) + " "
                j += 1
                file.write(string + "\n")



def main():
    """Main method.
    """
    app = QApplication(sys.argv)
    areaDetector = AreaDetectorAnalysisWindow()
    areaDetector.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()