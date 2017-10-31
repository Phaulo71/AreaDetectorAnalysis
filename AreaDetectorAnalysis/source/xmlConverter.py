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
import xml.etree.ElementTree as ET
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pylab as plt
from PIL import Image
import numpy as np
from matplotlib.patches import Rectangle
import xrayutilities as xu
import matplotlib.pyplot as plt
from spec2nexus.spec import SpecDataFile, SpecDataFileHeader
from AreaDetectorAnalysis.source.detectorDialog import DetectorDialog

# ---------------------------------------------------------------------------------------------------------------------#

class ConvertToXML():
    """Class that writes the information from the detector dialog to an xml file.
    """
    def __init__(self):
        super(ConvertToXML, self).__init__(self)

    def createXMLFile(self):
        self.instForXrayutils = ET.Element("{https://subnersion.xray.aps.anl.gov/RSM/instForXrayutils}instForXrayutils")
        self.sampleCircles = ET.SubElement("sampleCircles", attrib={"numCircles":str(len(self.sampleCircleList))})

        for i in xrange(1, len(self.sampleCircleList)):
            ET.SubElement(self.sampleCircles, "circleAxis",
                          attrib={"number": str(i), "specMotorName": str(self.sampleCircleMotorList[i]),
                                  "directionAxis": str(self.sampleCircleDirectionList[i])})

        tree = ET.ElementTree(self.instForXrayutils)
        tree.write("filename.xml")