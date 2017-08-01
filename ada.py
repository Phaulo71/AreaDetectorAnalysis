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

        self.fileList = []
        self.metadataList = []
        self.is_metadata_read = False
        self.imarray = []
        self.savedatafile = None
        self.bad_pixels_on = False
        self.bad_pixels = []
        self.replacing_pixels = []
        self.efficiency_on = False

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
            self.imarray = self.imarray / self.efficiencyarray

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
                ax = self.figure1.gca()  # this is important line to make image visible
                ax.imshow(self.imgArray, interpolation='none', vmin=vmin, vmax=vmax)
                ax.set_xlim(dxlim)
                ax.set_ylim(dylim)
                ax.plot(px, py, 'y-', linewidth=1.0)
                ax.plot(bx, by, 'g-', linewidth=1.0)
                self.canvas1.draw()
                if (0 in proi) or (0 in broi):
                    pass
                else:
                    self.areaIntegrationShow(self.imarray, droi, proi, broi)


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
            self.sc_dxc.setRange(0, iw)
            self.sc_dxc.setValue(iw / 2)
            self.sc_dyc.setRange(0, ih)
            self.sc_dyc.setValue(ih / 2)
            self.sc_dxw.setRange(0, iw)
            self.sc_dxw.setValue(iw)
            self.sc_dyw.setRange(0, ih)
            self.sc_dyw.setValue(ih)
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

    def areaIntegrationShow(self,lum_img,droi,proi,broi):
        pass

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
        print "Mouse moved."

    def OnMousePress(self, event):
        print "Mouse was pressed."

    def OnMouseRelease(self, event):
        print "Mouse was released."


def main():
    """Main method.
    """
    app = QApplication(sys.argv)
    areaDetector = AreaDetectorAnalysisWindow()
    areaDetector.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()