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

from spec2nexus.spec import SpecDataFile

# ---------------------------------------------------------------------------------------------------------------------#

class ReadSpec:
    """Loads spec file and gets appropriate information from it for a certain image
    """

    def __init__(self, parent=None):
        self.ada = parent
        self.mon = []

    def loadSpec(self, specFile, directory):
        self.chambers = []
        self.specFile = SpecDataFile(specFile)
        self.scans = self.specFile.scans
        self.scan = str(int(os.path.basename(directory)))
        self.specFileOpened = True

        # Gets possible normalizer values
        for key in self.scans[str(self.scan)].data.keys():
            if key.find("Ion_Ch_") == 0:
                self.chambers.append(key)

        self.chambers.sort()
        self.MonDialog()
        self.ada.controlDockWidget.close()
        self.ada.ControlDockWidget()

    def MonDialog(self):
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
        if self.buttonGroup != -1:
            self.monDialog.close()
            for cham in self.chambers:
                if cham.endswith(str(self.buttonGroup.checkedId())):
                    self.mon = self.scans[str(self.scan)].data[cham]

    def DataControlLabels(self):
        controls = []
        for key in self.scans[self.scan].L:
            if key == 'L':
                controls.append(key)
                break
            else:
                controls.append(key)

        return controls

    def setSpecData(self):
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
        data = self.scans[str(self.scan)].raw
        UE = data.split("#UE")
        ue = UE[1].split(" ")
        energy = ue[1]
        return energy


