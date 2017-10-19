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
import xrayutilities as xu

from spec2nexus.spec import SpecDataFile, SpecDataFileHeader
from AreaDetectorAnalysis.source.detectorDialog import DetectorDialog

# ---------------------------------------------------------------------------------------------------------------------#

class ReadSpec:
    """Loads spec file and gets appropriate information from it for a certain image.
    """

    def __init__(self, parent=None):
        self.ada = parent
        self.detectorDialog = DetectorDialog(self)
        self.mon = []

    def loadSpec(self, specFile, directory):
        """This method loads the spec file and creates the widgets on the control QDockWidget.
        """
        self.chambers = []
        self.specFile = SpecDataFile(specFile)
        self.specHeader = SpecDataFileHeader(specFile)
        self.scans = self.specFile.scans
        self.scan = str(int(os.path.basename(directory)))
        self.specFileOpened = True

        # Gets possible normalizer values
        for key in self.scans[self.scan].data.keys():
            if key.find("Ion_Ch_") == 0:
                self.chambers.append(key)

        self.chambers.sort()
        self.MonDialog()
        self.ada.controlDockWidget.close()
        self.ada.ControlDockWidget()

    def MonDialog(self):
        """Dialog produce for the user to select the mon value.
        """
        self.monDialog = QDialog(self.ada)
        dialogBox = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        vBox = QVBoxLayout()

        groupBox = QGroupBox("Mon")
        self.buttonGroup = QButtonGroup(groupBox)

        for norm in self.chambers:
            chamberRB = QRadioButton(norm)
            self.buttonGroup.addButton(chamberRB, int(norm[-1]))
            vBox.addWidget(chamberRB)

        groupBox.setLayout(vBox)

        ok = QPushButton("Ok")

        ok.clicked.connect(self.SetMon)

        buttonLayout.addStretch(1)
        buttonLayout.addWidget(ok)

        dialogBox.addWidget(groupBox)
        dialogBox.addLayout(buttonLayout)

        self.monDialog.setWindowTitle("Select chamber")
        self.monDialog.setLayout(dialogBox)
        self.monDialog.resize(250, 250)
        self.monDialog.exec_()

    def SetMon(self):
        """Sets the mon.
        """
        if self.buttonGroup != -1:
            self.monDialog.close()
            for cham in self.chambers:
                if cham.endswith(str(self.buttonGroup.checkedId())):
                    self.mon = self.scans[str(self.scan)].data[cham]

    def DataControlLabels(self):
        """Gets the appropriate labels for the spec file info display in the control's QDockWidget.
        """
        controls = []
        for key in self.scans[self.scan].L:
            if key == 'L':
                controls.append(key)
                break
            else:
                controls.append(key)

        return controls

    def setSpecData(self):
        """Sets the spec data into the self.specInfoValue.
        """
        try:
            self.specInfoValue = []

            for n in self.specInfo:
                if n == "E":
                    self.specInfoValue.append(self.getEnergy())
                elif n == "MON":
                    self.specInfoValue.append(self.mon)
                elif n == "Trans":
                    self.specInfoValue.append(self.scans[self.scan].data["transm"])
                else:
                    self.specInfoValue.append(self.scans[self.scan].data[str(n)])
        except:
            QMessageBox.warning(self.ada, "Warning", "Error loading the values from the spec. Please make sure "
                                                     "they follow the appropriate format.")


    def getSpecData(self, i):
        """Gets the appropriate spec value for the selected image.
        """
        try:
            specValue = []

            for n in self.specInfoValue:
                if isinstance(n, list):
                    specValue.append(n[i])
                else:
                    specValue.append(n)

            j = 0
            for n in specValue:
                self.specInfoBoxes[j].setText(str(n))
                j += 1
        except IndexError:
            QMessageBox.warning(self.ada, "Error", 'Please make sure you have the correct spec file, and/or have have the '
                                           'images folder named properly with the scan number.')

    def SpecDataInfo(self):
        """Creates the labels and text boxes for the spec info display in the Controls QDockWidget.
        """
        self.specInfo = []
        self.specInfoLabels = []
        self.specInfoBoxes = []
        self.specInfoLayout = []

        self.specInfo = self.DataControlLabels()
        self.specInfo.append("E")
        self.specInfo.append("MON")
        self.specInfo.append("Trans")

        for s in self.specInfo:
            label = QLabel(str(s), alignment=Qt.AlignCenter)
            textBox = QLineEdit()
            textBox.setReadOnly(True)
            textBox.setMaximumWidth(50)
            self.specInfoLabels.append(label)
            self.specInfoBoxes.append(textBox)
        j = 0
        vBoxLayout = QVBoxLayout()
        while j < len(self.specInfo):
            if len(self.specInfo) - j >= 3:
                s = 0
                hBox = QHBoxLayout()
                while s < 3:
                    hBox.addWidget(self.specInfoLabels[j])
                    hBox.addWidget(self.specInfoBoxes[j])
                    j += 1
                    s += 1
                vBoxLayout.addLayout(hBox)
            else:
                hBox1 = QHBoxLayout()
                while len(self.specInfo) - j > 0:
                    hBox1.addWidget(self.specInfoLabels[j])
                    hBox1.addWidget(self.specInfoBoxes[j])
                    j += 1
                hBox1.addStretch(1)
                vBoxLayout.addLayout(hBox1)
        self.setSpecData()

        return vBoxLayout

    def getEnergy(self):
        """Gets the energy from the spec file.
        """
        data = self.scans[str(self.scan)].raw
        UE = data.split("#UE")
        ue = UE[1].split(" ")
        energy = ue[1]
        return float(energy)

    def getUBMatrix(self):
        """Read UB matrix from the #G3 line from the spec file.
        :return: 2D array, with 1D arrays size 3
        """
        try:
            g3 = self.scans[self.scan].G["G3"].strip().split()
            g3 = np.array(map(float, g3))
            ub = g3.reshape(-1, 3)
            return ub

        except:
            print ("Unable to read the UB Matrix from G3.")

    def getListSpecDataForAngles(self):
        """Gets the eta, chi and phi from the spec file.
        :return: returns eta, chi and phi
        """
        angleListInfo = []
        angles = self.detectorDialog.getAngles()
        for angle in angles:
            try:
                angleListInfo.append(self.specFile.scans[self.scan].data[angle])
            except KeyError:
                #try:
                #  angList = np.zeros((0, self.totalScans))
                motorValue = self.motorSpecInfoDic[angle]
                angList = np.full((self.totalScans, 1), float(motorValue), dtype=float)
                angleListInfo.append(angList)
                #except:
                    #print "Something went wrong."
        return angleListInfo

    def getSpecHeaderO(self, specFile):
        """Gets the values for the spec motors/angles input by the user.
        :param specFile:
        :return: Dictionary with spec anlge and value
        """
        self.totalScans = 0
        self.motorSpecInfoDic = {}
        buf = open(specFile, 'r').read()
        buf.replace('\r\n', '\n').replace('\r', '\n')

        lines = buf.splitlines()

        for line in lines:
            if line.startswith("#O0"):
                lineO = line
                break

        O = lineO.split()
        O.pop(0)
        lineP = self.specFile.scans[self.scan].P[0]
        P = lineP.split()

        if len(O) != len(P):
            raise Exception ("Please make sure the spec file contains matching information in the header #O0 and under"
                             " the scan #P0.\n\n" "#O0: " + O + "\n#P0: " + P)
        else:
            for i in xrange(len(P)):
                self.motorSpecInfoDic.update({O[i]: P[i]})

        try:
            s = self.scans[self.scan].S.split()
            self.totalScans = int(s[len(s)-2])
        except:
            pass
            # Make the user input the total scans.

    def getDetectorROI(self):
        """Gets the detector ROI (Npixels)
        :return:
        """
        return [0, 487, 0, 195]

    def getNumPixelsToAverage(self):
        return [1, 1]

    def getDetectorPixelDirection1(self):
        """Gets the detector pixel direction from the detector dialog input.
        :return: pixel direction
        """
        # I need to get this from the dialog
        return 'z-'

    def getDetectorPixelDirection2(self):
        """Gets the detector pixel direction from the detector dialog input.
        :return: pixel direction
        """
        # I need to get this from the dialog
        return 'x-'

    def getDetectorCenterChannel(self):
        """Gets the detector center channel from the detector dialog input
        :return: list w/ detector center channels
        """
        return [173, 101]

    def getDetectorDimensions(self):
        """Returns the Npixels from the detector dialog
        :return: list of pixels
        """
        return [487, 195]

    def getDetectorPixelWidth(self):
        """Returns the width of the detector by dividing the size with the pixels
        :return:
        """
        s = 83.764/487  #  size/Npixels
        f = 33.54/195  #  size/Npixels
        return [s, f]

    def getDistanceToDetector(self):
        return 1193.8

    def getHKL(self):
        angleList = self.getListSpecDataForAngles()
        qconv = xu.experiment.QConversion(self.detectorDialog.getSampleCircleDirections(),
                                          self.detectorDialog.getDetectorCircleDirections(),
                                          self.detectorDialog.getPrimaryBeamDirection())

        en = self.getEnergy()
        hxrd = xu.HXRD(self.detectorDialog.getInplaneReferenceDirection(),
                       self.detectorDialog.getSampleSurfaceNormalDirection(),
                       en=en,
                       qconv=qconv)
        if (self.getDetectorPixelWidth() != None) and \
                (self.getDistanceToDetector() != None):
            hxrd.Ang2Q.init_area(self.getDetectorPixelDirection1(),
                                 self.getDetectorPixelDirection2(),
                                 cch1=self.getDetectorCenterChannel()[0],
                                 cch2=self.getDetectorCenterChannel()[1],
                                 Nch1=self.getDetectorDimensions()[0],
                                 Nch2=self.getDetectorDimensions()[1],
                                 pwidth1=self.getDetectorPixelWidth()[0],
                                 pwidth2=self.getDetectorPixelWidth()[1],
                                 distance=self.getDistanceToDetector(),
                                 Nav=self.getNumPixelsToAverage(),
                                 roi=self.getDetectorROI())
        else:
            hxrd.Ang2Q.init_area(self.getDetectorPixelDirection1(),
                                 self.getDetectorPixelDirection2(),
                                 cch1=self.getDetectorCenterChannel()[0],
                                 cch2=self.getDetectorCenterChannel()[1],
                                 Nch1=self.getDetectorDimensions()[0], \
                                 Nch2=self.getDetectorDimensions()[1], \
                                 chpdeg1=self.getDetectorChannelsPerDegree()[0],  # Can't find where you give this value
                                 chpdeg2=self.getDetectorChannelsPerDegree()[1],  # Can't find where you give this value
                                 Nav=self.getNumPixelsToAverage(),
                                 roi=self.getDetectorROI())

        h, k, l = hxrd.Ang2Q.area(*angleList,
                            roi=self.getDetectorROI(),
                            Nav=self.getNumPixelsToAverage(),
                            UB = self.getUBMatrix())

        print 'H'
        print h
        print 'k'
        print k
        print 'L'
        print l










