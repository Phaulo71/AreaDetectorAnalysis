'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import xml.etree.ElementTree as ET
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

NAMESPACE = '{https://subversion.xray.aps.anl.gov/RSM/dataForXrayutils}'

#  Element Names
INST_FOR_XRAYUTILS = NAMESPACE + 'instForXrayutils'
DETECTOR_CIRCLES = NAMESPACE + 'detectorCircles'
INPLANE_REFERENCE_DIRECTION = 'inplaneReferenceDirection'
MONITOR_NAME = 'monitorName'
PRIMARY_BEAM_DIRECTION = 'primaryBeamDirection'
PROJECTION_DIRECTION = 'projectionDirection'
SAMPLE_CIRCLES = 'sampleCircles'
SAMPLE_SURFACE_NORMAL_DIRECTION = 'sampleSurfaceNormalDirection'

DETECTORS = NAMESPACE + "Detector"
DETECTOR_ID = "ID"
PIXEL_DIRECTION1 = 'pixelDirection1'
PIXEL_DIRECTION2 = 'pixelDirection2'
CENTER_CHANNEL_PIXEL = 'centerChannelPixel'
NUMBER_OF_PIXELS = 'Npixels'
DETECTOR_SIZE = 'size'
DETECTOR_DISTANCE = 'distance'

#Attribute Names
AXIS_NUMBER = 'number'
DIRECTION_AXIS = 'directionAxis'
NAME = 'name'
NUM_CIRCLES = 'numCircles'
REFERENCE_AXIS = 'axis'
SPEC_MOTOR_NAME = 'specMotorName'

class InstForXrayutilsReader():
    """Class reads the xml xRayUtilities instrument file.
    """

    def __init__(self, parent, filename):
        self.detector = parent
        self.root = None
        try:
            print ("Welcome")
            tree = ET.parse(filename)
            self.root = tree.getroot()
            self.instForXray = self.root.find(INST_FOR_XRAYUTILS)
            self.sampleCirPosList = []
            self.sampleCirMotorList = []
            self.sampleCirAxisList = []
            self.loadFileIntoDialog()
        except IOError as ex:
            QMessageBox.Warning("Please submit a valid Instrument Configuration File. \n\n Exception: " + ex)

    def loadFileIntoDialog(self):
        self.setDetectorCircles()

    def getDetectorCircles(self):
        """
        :return:
        """
        detectorCircles = self.instForXray.find(DETECTOR_CIRCLES)
        circles = detectorCircles.findall(NAMESPACE + "circleAxis")

        for circle in circles:
            print (circle.attrib[SPEC_MOTOR_NAME])



    def setDetectorCircles(self):
        self.getDetectorCircles()
