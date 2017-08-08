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
from matplotlib.patches import Rectangle
from areaData import AreaData

# ---------------------------------------------------------------------------------------------------------------------#

class AreaDetectorAnalysisWindow(QMainWindow):
    """Main window class"""
    def __init__(self, parent=None):
        super(AreaDetectorAnalysisWindow, self).__init__(parent)
        self.setGeometry(50, 50, 1500, 800)
        self.setWindowTitle("Area Data Analysis")
        self.setMinimumSize(1000, 650)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.createMenus()
        self.ControlDockWidget()

        self.fileList = []
        self.metadataList = []
        self.is_metadata_read = False
        self.imgArray = np.array(0)
        self.savedatafile = None
        self.bad_pixels_on = False
        self.bad_pixels = []
        self.replacing_pixels = []
        self.efficiency_on = False
        self.mouse1_is_pressed = False

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
        self.canvas4 = FigureCanvas(self.figure4)
        self.canvas4.setParent(self.centralWidget)
        self.canvas5 = FigureCanvas(self.figure5)
        self.canvas5.setParent(self.centralWidget)

        self.log = QTextEdit()

        gLayout = QGridLayout()
        gLayout.addWidget(self.canvas1, 0, 0)
        gLayout.addWidget(self.log, 0, 1)
        gLayout.addWidget(self.canvas2, 1, 0)
        gLayout.addWidget(self.canvas3, 1, 1)
        gLayout.addWidget(self.canvas4, 2, 0)
        gLayout.addWidget(self.canvas5, 2, 1)

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


        vBox_right = QVBoxLayout()
        vBox_right.addLayout(gLayout)
        vBox_right.addLayout(hBox_save)

        # Adding to the central widget
        hBox_central = QHBoxLayout()
        hBox_central.addLayout(vBox_file)
        hBox_central.addLayout(vBox_right)

        self.centralWidget.setLayout(hBox_central)

        self.fileListBox.itemDoubleClicked.connect(self.OnListSelected)
        self.removeFileBtn.clicked.connect(self.OnRemoveFile)
        self.removeAllFileBtn.clicked.connect(self.OnRemoveAllFiles)
        self.saveAsBtn.clicked.connect(self.OnSaveAs)
        self.saveBtn.clicked.connect(self.OnSave)
        self.nextBtn.clicked.connect(self.OnNext)
        self.saveAndNextBtn.clicked.connect(self.OnSaveNext)
        self.resetRoiBtn.clicked.connect(self.OnResetDataROI)
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
        self.canvas1.mpl_connect('motion_notify_event', self.OnMouseMove)
        self.canvas1.mpl_connect('button_press_event', self.OnMousePress)
        self.canvas1.mpl_connect('button_release_event', self.OnMouseRelease)

    def ControlDockWidget(self):
        self.controlDockWidget = QDockWidget("Controls", self)
        self.controlDockWidget.setMaximumWidth(280)
        self.controlDockWidget.setMinimumWidth(280)
        self.controlDockWidget.setAllowedAreas(Qt.RightDockWidgetArea)

        # Controls
        self.resetRoiBtn = QPushButton("Reset")
        self.sc_dxc = QSpinBox(self)
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
        self.hkl_H = QLineEdit()
        self.hkl_K = QLineEdit()
        self.hkl_L = QLineEdit()
        self.energy = QLineEdit()
        self.mon = QLineEdit()
        self.trans = QLineEdit()
        spacer = QFrame()
        spacer.setFrameShape(QFrame.HLine)
        spacer1 = QFrame()
        spacer1.setFrameShape(QFrame.HLine)
        spacer2 = QFrame()
        spacer2.setFrameShape(QFrame.HLine)
        spacer3 = QFrame()
        spacer3.setFrameShape(QFrame.HLine)

        self.sl_dxc = QSlider(Qt.Horizontal)
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

        gLayout_control = QGridLayout()

        hBox_pln = QHBoxLayout()
        hBox_pln.addWidget(QLabel("Bkgd Fit Order1"))
        hBox_pln.addWidget(self.sc_pln_order1)
        hBox_pln.addWidget(QLabel("Bkgd Fit Order2"))
        hBox_pln.addWidget(self.sc_pln_order2)

        hBox_hkl1 = QHBoxLayout()
        hBox_hkl1.addWidget(QLabel("H"))
        hBox_hkl1.addWidget(self.hkl_H)
        hBox_hkl1.addWidget(QLabel("K"), alignment=Qt.AlignCenter)
        hBox_hkl1.addWidget(self.hkl_K)
        hBox_hkl1.addWidget(QLabel("L"), alignment=Qt.AlignCenter)
        hBox_hkl1.addWidget(self.hkl_L)

        hBox_hkl2 = QHBoxLayout()
        hBox_hkl2.addWidget(QLabel("Energy"), alignment=Qt.AlignCenter)
        hBox_hkl2.addWidget(self.energy)
        hBox_hkl2.addWidget(QLabel("MON"), alignment=Qt.AlignCenter)
        hBox_hkl2.addWidget(self.mon)
        hBox_hkl2.addWidget(QLabel("Trans"), alignment=Qt.AlignCenter)
        hBox_hkl2.addWidget(self.trans)

        dockLayout = QVBoxLayout()
        dockLayout.addLayout(vROI_Layout)
        dockLayout.addLayout(vPeak_Layout)
        dockLayout.addLayout(vBkgd_Layout)
        dockLayout.addLayout(hBox_pln)
        dockLayout.addLayout(hBox_hkl1)
        dockLayout.addLayout(hBox_hkl2)
        dockLayout.addWidget(self.resetRoiBtn)
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
        self.fileMenu.addAction(self.openImagesAction)
        self.fileMenu.addAction(self.readMetadataAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.nextAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addAction(self.saveAndNextAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)
        self.badPixelsMenu.addAction(self.badPixelsOnAction)
        self.badPixelsMenu.addAction(self.badPixelsOffAction)
        self.flatfieldMenu.addAction(self.flatfieldOnAction)
        self.flatfieldMenu.addAction(self.badPixelsOffAction)
        self.optionsMenu.addAction(self.selectNewDataColumnAction)


    def createActions(self):
        """Function that creates the actions used in the menu bar
        """
        self.openImagesAction = QAction('Open Images', self)
        self.openImagesAction.setStatusTip('List up the image files to open.')
        self.openImagesAction.triggered.connect(self.OnOpenImage)

        self.readMetadataAction = QAction('Read Metadata', self)
        self.readMetadataAction.setStatusTip('Read a metadata file.')
        self.readMetadataAction.triggered.connect(self.OnReadMetaData)

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

        self.selectNewDataColumnAction = QAction("Select New Data Column", self)
        self.selectNewDataColumnAction.setStatusTip("Select New Data Columns.")
        self.selectNewDataColumnAction.triggered.connect(self.OnSelectDataColumn)

    def OnOpenImage(self):
        dir = QFileDialog.getExistingDirectory(caption="Choose directory")

        if os.path.isdir(dir):
            images = os.listdir(dir)

            for img in images:
                self.fileListBox.addItem(img)
                if dir.find("/") == 0:
                    self.fileList.append(dir + '/' + img)
                elif dir.find("\\") == 0:
                    self.fileList.append(dir + '\\' + img)

                self.metadataList.append([])


    def OnReadMetaData(self):
        print "Not ready, yet."

    def OnSaveAs(self):
        print "Not ready, yet."

    def OnSave(self):
        print "Not ready, yet."

    def OnNext(self):
        print "Not ready, yet."

    def OnSaveNext(self):
        self.OnSave()
        self.OnNext()

    def OnExit(self):
        self.close()

    def OnBadPixelCorrection(self):
        print "Not ready, yet"

    def OffBadPixelCorrection(self):
        print "Not ready, yet"

    def OnFlatfieldCorrection(self):
        print "Not ready, yet"

    def OffFlatfieldCorrection(self):
        print "Not ready, yet"

    def OnSelectDataColumn(self):
        print "Not ready."

    def OnListSelected(self):
        self.imgIndx = self.fileListBox.currentRow()
        self.curimg = Image.open(self.fileList[self.imgIndx])
        self.imgArray = np.array(self.curimg)

        if self.efficiency_on == True:
            self.imgArray = self.imarray / self.efficiencyarray

        if self.bad_pixels_on == True:
            for i in range(len(self.bad_pixels)):
                self.imgArray[self.bad_pixels[i][1], self.bad_pixels[i][0]] = \
                    self.imgArray[self.replacing_pixels[i][1], self.replacing_pixels[i][0]]

        if self.metadataList[self.imgIndx]:
            self.hkl_H.setText(str('%4.3f' % self.metadataList[self.imgIndx][self.Hcol]))
            self.hkl_K.setText(str('%4.3f' % self.metadataList[self.imgIndx][self.Kcol]))
            self.hkl_L.setText(str('%4.3f' % self.metadataList[self.imgIndx][self.Lcol]))
            self.energy.setText(str('%6.4f' % self.metadataList[self.imgIndx][self.Ecol]))
            self.mon.setText(str('%12d' % self.metadataList[self.imgIndx][self.Mcol]))
            self.trans.setText(str('%6.5e' % self.metadataList[self.imgIndx][self.Tcol]))
        elif not self.metadataList[self.imgIndx]:
            self.hkl_H.setText("nan")
            self.hkl_K.setText("nan")
            self.hkl_L.setText("nan")
            self.energy.setText("nan")
            self.mon.setText("nan")
            self.trans.setText("nan")

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
                    self.RedrawImage()
                    return
                else:
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
                    ax = self.figure1.add_subplot(111)  # this is important line to make image visible
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


    def OnRemoveFile(self):
        if len(self.fileList) != 0:
            indx = self.fileListBox.currentRow()
            self.fileListBox.takeItem(indx)
            self.fileList.remove(self.fileList[indx])
            self.metadataList.remove(self.metadataList[indx])
            if len(self.fileList) == 0:
                self.is_metadata_read = False

    def OnRemoveAllFiles(self):
        if len(self.fileList) != 0:
            self.fileListBox.clear()
            self.fileList = []
            self.metadataList = []
            self.is_metadata_read = False

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
        print ih, iw
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

    def areaIntegrationShow(self,lum_img,droi,proi,broi):
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
        print event.inaxes
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
        print event.button
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
            if event.button == 1:
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


def main():
    """Main method.
    """
    app = QApplication(sys.argv)
    areaDetector = AreaDetectorAnalysisWindow()
    areaDetector.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()