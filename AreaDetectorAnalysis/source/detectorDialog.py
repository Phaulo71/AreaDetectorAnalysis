#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""
# ---------------------------------------------------------------------------------------------------------------------#
from __future__ import unicode_literals

import os
import sys
import time

import matplotlib.pylab as plt
import numpy as np
from PIL import Image
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle

class DetectorDialog(QDialog):
    """Main window class"""
    def __init__(self, parent=None):
        super(DetectorDialog, self).__init__()
        self.readSpec = parent
        self.mainWindow = self.readSpec.ada
        self.setWindowTitle('Detector Dialog')
        self.mainVLayout1 = QVBoxLayout()
        self.mainVLayout2 = QVBoxLayout()
        self.mainHLayout = QHBoxLayout()
        self.finalMainVLayout = QVBoxLayout()
        self.finalMainHLayout = QHBoxLayout()

        self.sampleCircleInit()
        self.detectorCircleInit()
        self.referenceDirectionsInit()
        self.detectorInfoInit()

        buttonHLayout = QHBoxLayout()
        ok = QPushButton("Okay")
        ok.clicked.connect(self.okDetectorDialog)
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.cancelDetectorDialog)
        buttonHLayout.addWidget(cancel)
        buttonHLayout.addStretch(1)
        buttonHLayout.addWidget(ok)

        self.directoryName = QLineEdit()
        browseWorkDirectory = QPushButton("Browse")
        browseWorkDirectory.clicked.connect(self.mainWindow.OnOpenWorkDir)
        self.workDirHLayout = QHBoxLayout()
        self.workDirHLayout.addWidget(QLabel("Work directory: "))
        self.workDirHLayout.addWidget(self.directoryName)
        self.workDirHLayout.addWidget(browseWorkDirectory)

        self.mainVLayout1.addLayout(self.smpCircleVlayout)
        self.mainVLayout1.addSpacing(5)
        self.mainVLayout1.addLayout(self.dtcCircleVlayout)

        self.mainVLayout2.addLayout(self.refDirectionsForm)
        self.mainVLayout2.addSpacing(5)
        self.mainVLayout2.addLayout(self.detectorInfoGLayout)
        self.mainVLayout2.addStretch(1)

        self.mainHLayout.addLayout(self.mainVLayout1)
        self.mainHLayout.addSpacing(25)
        self.mainHLayout.addLayout(self.mainVLayout2)

        self.finalMainVLayout.addLayout(self.workDirHLayout)
        self.finalMainVLayout.addSpacing(15)
        self.finalMainVLayout.addLayout(self.mainHLayout)
        self.finalMainVLayout.addSpacing(15)
        self.finalMainVLayout.addLayout(buttonHLayout)

        self.finalMainHLayout.addStretch(1)
        self.finalMainHLayout.addLayout(self.finalMainVLayout)
        self.finalMainHLayout.addStretch(1)
        self.setLayout(self.finalMainHLayout)



    def cancelDetectorDialog(self):
        self.close()
        sys.exit()

    def okDetectorDialog(self):
        self.readSpec.getHKL()
        # self.close()

    def sampleCircleInit(self):

        titleHLayout = QHBoxLayout()
        posTitle = QLabel("Postition")
        specMotorTitle = QLabel("Spec Motor Name")
        axisTitle = QLabel("Direction Axis")

        titleHLayout.addWidget(posTitle)
        titleHLayout.addSpacing(20)
        titleHLayout.addWidget(specMotorTitle)
        titleHLayout.addSpacing(20)
        titleHLayout.addWidget(axisTitle)

        self.sampleCircleList = QListWidget()
        self.sampleCircleList.setSelectionMode(QAbstractItemView.NoSelection)
        self.sampleCircleList.setFocusPolicy(Qt.NoFocus)
        self.sampleCircleList.setMaximumHeight(150)
        self.sampleCircleList.setMinimumHeight(150)
        self.sampleCircleMotorList = []
        self.sampleCircleDirectionList = []
        self.sampleCircleNumberList = []

        addBtn = QPushButton('Add')
        addBtn.clicked.connect(self.addNewSampleCircle)
        removeBtn = QPushButton('Remove')
        removeBtn.clicked.connect(self.removeSampleCirlce)
        btnHLayout = QHBoxLayout()
        btnHLayout.addStretch(1)
        btnHLayout.addWidget(removeBtn)
        btnHLayout.addWidget(addBtn)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)

        self.smpCircleVlayout = QVBoxLayout()
        self.smpCircleVlayout.addWidget(QLabel("Sample Circles:"))
        self.smpCircleVlayout.addWidget(line)
        self.smpCircleVlayout.addLayout(titleHLayout)
        self.smpCircleVlayout.addWidget(self.sampleCircleList)
        self.smpCircleVlayout.addLayout(btnHLayout)

    def addNewSampleCircle(self):
        widget = QWidget()
        item = QListWidgetItem()
        newCircleHLayout = QHBoxLayout()

        position = QLabel(str(self.sampleCircleList.count()+1))
        self.sampleCircleNumberList.append(position)
        specMotorBox = QComboBox()
        specMotorBox.addItem('Eta')
        specMotorBox.addItem('Delta')
        specMotorBox.addItem('Chi')
        specMotorBox.addItem('Phi')
        specMotorBox.addItem('Mu')
        specMotorBox.addItem('Nu')
        self.sampleCircleMotorList.append(specMotorBox)

        axisDirection = QComboBox()
        axisDirection.addItem('x+')
        axisDirection.addItem('x-')
        axisDirection.addItem('y+')
        axisDirection.addItem('y-')
        axisDirection.addItem('z+')
        axisDirection.addItem('z-')
        self.sampleCircleDirectionList.append(axisDirection)
        newCircleHLayout.addWidget(position)
        newCircleHLayout.addStretch(30)
        newCircleHLayout.addWidget(specMotorBox)
        newCircleHLayout.addStretch(30)
        newCircleHLayout.addWidget(axisDirection)
        newCircleHLayout.setSizeConstraint(newCircleHLayout.SetMinimumSize)
        widget.setLayout(newCircleHLayout)
        item.setSizeHint(QSize(widget.sizeHint().width(), 27))


        self.sampleCircleList.addItem(item)
        self.sampleCircleList.setItemWidget(item, widget)

    def removeSampleCirlce(self):
        if len(self.sampleCircleNumberList) != 0:
            x = len(self.sampleCircleNumberList)
            self.sampleCircleList.takeItem(x-1)
            self.sampleCircleNumberList.pop(x-1)
            self.sampleCircleMotorList.pop(x-1)
            self.sampleCircleDirectionList.pop(x-1)

    def detectorCircleInit(self):

        titleHLayout = QHBoxLayout()
        posTitle = QLabel("Postition")
        specMotorTitle = QLabel("Spec Motor Name")
        axisTitle = QLabel("Direction Axis")

        titleHLayout.addWidget(posTitle)
        titleHLayout.addSpacing(20)
        titleHLayout.addWidget(specMotorTitle)
        titleHLayout.addSpacing(20)
        titleHLayout.addWidget(axisTitle)

        self.detectorCircleList = QListWidget()
        self.detectorCircleList.setSelectionMode(QAbstractItemView.NoSelection)
        self.detectorCircleList.setFocusPolicy(Qt.NoFocus)
        self.detectorCircleList.setMaximumHeight(100)
        self.detectorCircleList.setMinimumHeight(100)
        self.detectorCircleList.setMinimumHeight(100)
        self.detectorCircleMotorList = []
        self.detectorCircleDirectionList = []
        self.detectorCircleNumberList = []

        addBtn = QPushButton('Add')
        addBtn.clicked.connect(self.addNewDetectorCircle)
        removeBtn = QPushButton('Remove')
        removeBtn.clicked.connect(self.removeDetectorCirlce)
        btnHLayout = QHBoxLayout()
        btnHLayout.addStretch(1)
        btnHLayout.addWidget(removeBtn)
        btnHLayout.addWidget(addBtn)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)

        self.dtcCircleVlayout = QVBoxLayout()
        self.dtcCircleVlayout.addWidget(QLabel("Detector Circles:"))
        self.dtcCircleVlayout.addWidget(line2)
        self.dtcCircleVlayout.addLayout(titleHLayout)
        self.dtcCircleVlayout.addWidget(self.detectorCircleList)
        self.dtcCircleVlayout.addLayout(btnHLayout)

    def addNewDetectorCircle(self):
        widget = QWidget()
        item = QListWidgetItem()
        newCircleHLayout = QHBoxLayout()

        position = QLabel(str(self.detectorCircleList.count() + 1))
        self.detectorCircleNumberList.append(position)
        specMotorBox = QComboBox()
        specMotorBox.addItem('Eta')
        specMotorBox.addItem('Delta')
        specMotorBox.addItem('Chi')
        specMotorBox.addItem('Phi')
        specMotorBox.addItem('Mu')
        specMotorBox.addItem('Nu')
        self.detectorCircleMotorList.append(specMotorBox)

        axisDirection = QComboBox()
        axisDirection.addItem('x+')
        axisDirection.addItem('x-')
        axisDirection.addItem('y+')
        axisDirection.addItem('y-')
        axisDirection.addItem('z+')
        axisDirection.addItem('z-')
        self.detectorCircleDirectionList.append(axisDirection)
        newCircleHLayout.addWidget(position)
        newCircleHLayout.addStretch(30)
        newCircleHLayout.addWidget(specMotorBox)
        newCircleHLayout.addStretch(30)
        newCircleHLayout.addWidget(axisDirection)
        newCircleHLayout.setSizeConstraint(newCircleHLayout.SetMinimumSize)
        widget.setLayout(newCircleHLayout)
        item.setSizeHint(QSize(widget.sizeHint().width(), 27))

        self.detectorCircleList.addItem(item)
        self.detectorCircleList.setItemWidget(item, widget)

    def removeDetectorCirlce(self):
        if len(self.detectorCircleNumberList) != 0:
            x = len(self.detectorCircleNumberList)
            self.detectorCircleList.takeItem(x - 1)
            self.detectorCircleNumberList.pop(x - 1)
            self.detectorCircleMotorList.pop(x-1)
            self.detectorCircleDirectionList.pop(x-1)

    def referenceDirectionsInit(self):
        self.refDirectionsForm = QFormLayout()
        self.refDirectionsForm.setAlignment(Qt.AlignHCenter)
        self.primaryBeamDirBox = QComboBox()
        self.primaryBeamDirBox.setFixedWidth(45)
        self.primaryBeamDirBox.addItem("x")
        self.primaryBeamDirBox.addItem("y")
        self.primaryBeamDirBox.addItem("z")

        self.inplaneRefDirBox = QComboBox()
        self.inplaneRefDirBox.setFixedWidth(45)
        self.inplaneRefDirBox.addItem("x")
        self.inplaneRefDirBox.addItem("y")
        self.inplaneRefDirBox.addItem("z")

        self.sampleSurfaceNormalDirBox = QComboBox()
        self.sampleSurfaceNormalDirBox.setFixedWidth(45)
        self.sampleSurfaceNormalDirBox.addItem("x")
        self.sampleSurfaceNormalDirBox.addItem("y")
        self.sampleSurfaceNormalDirBox.addItem("z")

        self.projectionDirBox = QComboBox()
        self.projectionDirBox.setFixedWidth(45)
        self.projectionDirBox.addItem("x")
        self.projectionDirBox.addItem("y")
        self.projectionDirBox.addItem("z")
        line = QFrame()
        line.setFrameShape(QFrame.HLine)

        self.refDirectionsForm.addRow(QLabel("Reference Directions:"))
        self.refDirectionsForm.addRow(line)
        self.refDirectionsForm.addRow("Primary Beam Direction:", self.primaryBeamDirBox)
        self.refDirectionsForm.addRow("Inplane Reference Direction:", self.inplaneRefDirBox)
        self.refDirectionsForm.addRow("Sample Surface Normal Direction:", self.sampleSurfaceNormalDirBox)
        self.refDirectionsForm.addRow("Projection Direction:", self.projectionDirBox)

    def detectorInfoInit(self):
        self.detectorInfoGLayout = QGridLayout()

        self.pixelDirectionBox = QComboBox()
        self.pixelDirectionBox.setFixedWidth(45)
        self.pixelDirectionBox.addItem('x+')
        self.pixelDirectionBox.addItem('x-')
        self.pixelDirectionBox.addItem('y+')
        self.pixelDirectionBox.addItem('y-')
        self.pixelDirectionBox.addItem('z+')
        self.pixelDirectionBox.addItem('z-')

        self.detectorInfoGLayout.addWidget(QLabel("Pixel Direction 1:"), 0, 0)
        self.detectorInfoGLayout.addWidget(self.pixelDirectionBox,0,2)

    def getSampleMotorNames(self):
        names = []
        for s in self.sampleCircleMotorList:
            names.append(s.itemText(s.currentIndex()))
        return names

    def getDetectorMotorNames(self):
        names = []
        for d in self.detectorCircleMotorList:
            names.append(d.itemText(d.currentIndex()))
        return names

    def getAngles(self):
        angles = []
        smpAngles = self.getSampleMotorNames()
        for s in smpAngles:
            angles.append(s)

        dtcAngles = self.getDetectorMotorNames()
        for d in dtcAngles:
            angles.append(d)

        return angles

    def getSampleCircleDirections(self):
        directions = []
        for d in self.sampleCircleDirectionList:
            directions.append(d.itemText(d.currentIndex()))

        return directions

    def getDetectorCircleDirections(self):
        directions = []
        for d in self.detectorCircleDirectionList:
            directions.append(d.itemText(d.currentIndex()))

        return directions

    def getPrimaryBeamDirection(self):
        direction = self.primaryBeamDirBox.itemText(self.primaryBeamDirBox.currentIndex())
        return self.getDirectionCoordinates(direction)

    def getInplaneReferenceDirection(self):
        direction = self.inplaneRefDirBox.itemText(self.inplaneRefDirBox.currentIndex())
        return self.getDirectionCoordinates(direction)

    def getSampleSurfaceNormalDirection(self):
        direction = self.sampleSurfaceNormalDirBox.itemText(self.sampleSurfaceNormalDirBox.currentIndex())
        return self.getDirectionCoordinates(direction)

    def getDirectionCoordinates(self, direction):
        if direction == 'y':
            return [0, 1, 0]
        elif direction == 'x':
            return [1, 0, 0]
        else:
            return [0, 0, 1]








