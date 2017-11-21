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
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import xml.etree.ElementTree as ET
from InstForXrayutilsReader import InstForXrayutilsReader


class DetectorDialog(QDialog):
    """Main window class"""
    def __init__(self, parent=None):
        super(DetectorDialog, self).__init__()
        self.readSpec = parent
        self.mainWindow = self.readSpec.mainWindow
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

        self.xmlFileName = QLineEdit()
        loadXMLFile = QPushButton("Load")
        loadXMLFile.clicked.connect(self.loadXMLFile)
        self.xmlFileHLayout = QHBoxLayout()
        self.xmlFileHLayout.addWidget(QLabel("Xml Data File:  "))
        self.xmlFileHLayout.addWidget(self.xmlFileName)
        self.xmlFileHLayout.addWidget(loadXMLFile)

        self.mainVLayout1.addLayout(self.smpCircleVlayout)
        self.mainVLayout1.addSpacing(5)
        self.mainVLayout1.addLayout(self.dtcCircleVlayout)

        self.mainVLayout2.addLayout(self.refDirectionsForm)
        self.mainVLayout2.addSpacing(25)
        self.mainVLayout2.addLayout(self.detectorInfoGLayout)
        self.mainVLayout2.addStretch(1)

        self.mainHLayout.addLayout(self.mainVLayout1)
        self.mainHLayout.addSpacing(25)
        self.mainHLayout.addLayout(self.mainVLayout2)

        self.finalMainVLayout.addLayout(self.workDirHLayout)
        self.finalMainVLayout.addLayout(self.xmlFileHLayout)
        self.finalMainVLayout.addSpacing(15)
        self.finalMainVLayout.addLayout(self.mainHLayout)
        self.finalMainVLayout.addSpacing(15)
        self.finalMainVLayout.addLayout(buttonHLayout)

        self.finalMainHLayout.addStretch(1)
        self.finalMainHLayout.addLayout(self.finalMainVLayout)
        self.finalMainHLayout.addStretch(1)
        self.setLayout(self.finalMainHLayout)

    def loadXMLFile(self):
        self.xmlFile, self.xmlFilter = QFileDialog.getOpenFileName(parent=self.mainWindow, caption="Open XML file", filter="*.xml")

        print ("Hello1")
        print (self.xmlFile)
        print (os.path.isfile(str(self.xmlFile)))

        if self.xmlFile != None and os.path.isfile(str(self.xmlFile)):
            print ("Hello")
            InstForXrayutilsReader(self, self.xmlFile)

    def createDetectorDialog(self):
        self.detectorDialog = QDialog()

    def cancelDetectorDialog(self):
        self.close()
        sys.exit()

    def okDetectorDialog(self):
        self.createXMLFile()
        #self.readSpec.rawMap()
        #self.close()

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

        line = QFrame()
        line.setFrameShape(QFrame.HLine)

        self.pixelDirectionBox1 = QComboBox()
        self.pixelDirectionBox1.setFixedWidth(45)
        self.pixelDirectionBox1.addItem('x+')
        self.pixelDirectionBox1.addItem('x-')
        self.pixelDirectionBox1.addItem('y+')
        self.pixelDirectionBox1.addItem('y-')
        self.pixelDirectionBox1.addItem('z+')
        self.pixelDirectionBox1.addItem('z-')

        self.pixelDirectionBox2 = QComboBox()
        self.pixelDirectionBox2.setFixedWidth(45)
        self.pixelDirectionBox2.addItem('x+')
        self.pixelDirectionBox2.addItem('x-')
        self.pixelDirectionBox2.addItem('y+')
        self.pixelDirectionBox2.addItem('y-')
        self.pixelDirectionBox2.addItem('z+')
        self.pixelDirectionBox2.addItem('z-')

        self.centerChannelLnEdit1 = QLineEdit()
        self.centerChannelLnEdit1.setFixedWidth(55)
        self.centerChannelLnEdit1.setValidator(QDoubleValidator())
        self.centerChannelLnEdit2 = QLineEdit()
        self.centerChannelLnEdit2.setFixedWidth(55)
        self.centerChannelLnEdit2.setValidator(QDoubleValidator())

        self.nPixelsLnEdit1 = QLineEdit()
        self.nPixelsLnEdit1.setFixedWidth(55)
        self.nPixelsLnEdit1.setValidator(QDoubleValidator())
        self.nPixelsLnEdit2 = QLineEdit()
        self.nPixelsLnEdit2.setFixedWidth(55)
        self.nPixelsLnEdit2.setValidator(QDoubleValidator())

        self.detectorSizeLnEdit1 = QLineEdit()
        self.detectorSizeLnEdit1.setFixedWidth(55)
        self.detectorSizeLnEdit1.setValidator(QDoubleValidator())
        self.detectorSizeLnEdit2 = QLineEdit()
        self.detectorSizeLnEdit2.setFixedWidth(55)
        self.detectorSizeLnEdit2.setValidator(QDoubleValidator())

        self.distanceLnEdit = QLineEdit()
        self.distanceLnEdit.setFixedWidth(55)
        self.distanceLnEdit.setValidator(QDoubleValidator())
        self.detectorIDBox = QComboBox()
        self.detectorIDBox.addItem('Pilatus')

        self.detectorInfoGLayout.addWidget(QLabel("Detector Geometry:"), 0, 0)
        self.detectorInfoGLayout.addWidget(line, 1, 0, 1, 3)
        self.detectorInfoGLayout.addWidget(QLabel("Pixels:"), 2, 0)
        self.detectorInfoGLayout.addWidget(self.nPixelsLnEdit1, 2, 1)
        self.detectorInfoGLayout.addWidget(self.nPixelsLnEdit2, 2, 2)
        self.detectorInfoGLayout.addWidget(QLabel("Center Channel Pixel:"), 3, 0)
        self.detectorInfoGLayout.addWidget(self.centerChannelLnEdit1, 3, 1)
        self.detectorInfoGLayout.addWidget(self.centerChannelLnEdit2, 3, 2)
        self.detectorInfoGLayout.addWidget(QLabel("Distance (mm):"), 4, 0)
        self.detectorInfoGLayout.addWidget(self.distanceLnEdit, 4, 2)
        self.detectorInfoGLayout.addWidget(QLabel("Size (mm):"), 5, 0)
        self.detectorInfoGLayout.addWidget(self.detectorSizeLnEdit1, 5, 1)
        self.detectorInfoGLayout.addWidget(self.detectorSizeLnEdit2, 5, 2)
        self.detectorInfoGLayout.addWidget(QLabel("Pixel Direction 1:"), 6, 0)
        self.detectorInfoGLayout.addWidget(self.pixelDirectionBox1, 6, 2, alignment=Qt.AlignRight)
        self.detectorInfoGLayout.addWidget(QLabel("Pixel Direction 2:"), 7, 0)
        self.detectorInfoGLayout.addWidget(self.pixelDirectionBox2, 7, 2, alignment=Qt.AlignRight)
        self.detectorInfoGLayout.addWidget(QLabel("Detector ID:"), 8, 0)
        self.detectorInfoGLayout.addWidget(self.detectorIDBox, 8, 2, alignment=Qt.AlignRight)

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


    def getDetectorROI(self):
        """Gets the detector ROI (Npixels)
        :return:
        """
        n1 = float(self.nPixelsLnEdit1.text())
        n2 = float(self.nPixelsLnEdit2.text())
        return [0, n1, 0, n2]

    def getNumPixelsToAverage(self):
        return [1, 1]

    def getDetectorPixelDirection1(self):
        """Gets the detector pixel direction from the detector dialog input.
        :return: pixel direction 1
        """
        return self.pixelDirectionBox1.itemText(self.pixelDirectionBox1.currentIndex())

    def getDetectorPixelDirection2(self):
        """Gets the detector pixel direction from the detector dialog input.
        :return: pixel direction 2
        """
        return self.pixelDirectionBox2.itemText(self.pixelDirectionBox2.currentIndex())

    def getDetectorCenterChannel(self):
        """Gets the detector center channel from the detector dialog input
        :return: list w/ detector center channels
        """
        n1 = float(self.centerChannelLnEdit1.text())
        n2 = float(self.centerChannelLnEdit2.text())
        return [n1, n2]

    def getDetectorDimensions(self):
        """Returns the Npixels from the detector dialog
        :return: list of pixels
        """
        n1 = float(self.nPixelsLnEdit1.text())
        n2 = float(self.nPixelsLnEdit2.text())
        return [n1, n2]

    def getDetectorPixelWidth(self):
        """Returns the width of the detector by dividing the size with the pixels
        :return:
        """
        p1 = float(self.nPixelsLnEdit1.text())
        p2 = float(self.nPixelsLnEdit2.text())

        s1 = float(self.detectorSizeLnEdit1.text())
        s2 = float(self.detectorSizeLnEdit2.text())

        s = s1 / p1
        f = s2 / p2
        return [s, f]

    def getDistanceToDetector(self):
        return float(self.distanceLnEdit.text())

    def createXMLFile(self):
        """Creates an xml file from the date input to the detector dialog.
        """
        dataForXrayutils = ET.Element("dataForXrayutils",
                                attrib={'xmlns':"https://subversion.xray.aps.anl.gov/RSM/dataForXrayutils"})

        #  Instrument xml tag
        instForXrayutils = ET.SubElement(dataForXrayutils, "instForXrayutils")
        sampleCircles = ET.SubElement(instForXrayutils, "sampleCircles",
                                           attrib={"numCircles": str(len(self.sampleCircleList))})
        detectorCircles = ET.SubElement(instForXrayutils, "detectorCircles",
                                           attrib={"numCircles": str(len(self.detectorCircleList))})
        primaryBeamDirection = ET.SubElement(instForXrayutils, "primaryBeamDirection")
        inplaneReferenceDirection = ET.SubElement(instForXrayutils, "inplaneReferenceDirection")
        sampleSurfaceNormalDirection = ET.SubElement(instForXrayutils, "sampleSurfaceNormalDirection")
        projectionDirection = ET.SubElement(instForXrayutils, "projectionDirection")

        for i in xrange(len(self.sampleCircleList)):
            ET.SubElement(sampleCircles, "circleAxis",
                          attrib={"number": str(i+1),
                                  "specMotorName": str(self.sampleCircleMotorList[i].itemText(
                                      self.sampleCircleMotorList[i].currentIndex())),
                                  "directionAxis": str(self.sampleCircleDirectionList[i].itemText(
                                      self.sampleCircleDirectionList[i].currentIndex()))})

        for i in xrange(len(self.detectorCircleList)):
            ET.SubElement(detectorCircles, "circleAxis",
                          attrib={"number": str(i + 1),
                                  "specMotorName": str(self.detectorCircleMotorList[i].itemText(
                                      self.detectorCircleMotorList[i].currentIndex())),
                                  "directionAxis": str(self.detectorCircleDirectionList[i].itemText(
                                      self.detectorCircleDirectionList[i].currentIndex()))})
        pbdirection = self.getDirectionCoordinates(
            self.primaryBeamDirBox.itemText(self.primaryBeamDirBox.currentIndex()))
        irdirection = self.getDirectionCoordinates(
            self.inplaneRefDirBox.itemText(self.inplaneRefDirBox.currentIndex()))
        ssndirection = self.getDirectionCoordinates(
            self.sampleSurfaceNormalDirBox.itemText(self.sampleSurfaceNormalDirBox.currentIndex()))
        pdirection = self.getDirectionCoordinates(
            self.projectionDirBox.itemText(self.projectionDirBox.currentIndex()))

        for j in xrange(3):
            ET.SubElement(primaryBeamDirection, "axis",
                          attrib={"number": str(j + 1)}).text = str(pbdirection[j])

            ET.SubElement(inplaneReferenceDirection, "axis",
                          attrib={"number": str(j + 1)}).text = str(irdirection[j])

            ET.SubElement(sampleSurfaceNormalDirection, "axis",
                          attrib={"number": str(j + 1)}).text = str(ssndirection[j])

            ET.SubElement(projectionDirection, "axis",
                          attrib={"number": str(j + 1)}).text = str(pdirection[j])

        #  Detector xml tag
        detectorGeometryForXrayutils = ET.SubElement(dataForXrayutils, "detectorGeometryForXrayutils")
        detector = ET.SubElement(detectorGeometryForXrayutils, "Detector")

        ET.SubElement(detector, "pixelDirection1").text = \
            self.pixelDirectionBox1.itemText(self.pixelDirectionBox1.currentIndex())
        ET.SubElement(detector, "pixelDirection2").text = \
            self.pixelDirectionBox1.itemText(self.pixelDirectionBox2.currentIndex())
        ET.SubElement(detector, "centerChannelPixel").text = (self.centerChannelLnEdit1.text() + " " +
                                                              self.centerChannelLnEdit2.text())
        ET.SubElement(detector, "Npixels").text = (self.nPixelsLnEdit1.text() + " " + self.nPixelsLnEdit2.text())
        ET.SubElement(detector, "size", attrib={"unit": "mm"}).text = (self.detectorSizeLnEdit1.text() + " " +
                                                                       self.detectorSizeLnEdit2.text())
        ET.SubElement(detector, "distance", attrib={"unit": "mm"}).text = self.distanceLnEdit.text()
        ET.SubElement(detector, "ID").text = self.detectorIDBox.itemText(self.detectorIDBox.currentIndex())
        ET.SubElement(detector, "notes").text = " "



        tree = ET.ElementTree(dataForXrayutils)
        tree.write("filename.xml", xml_declaration=True, encoding="UTF-8", method="xml")








