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
INPLANE_REFERENCE_DIRECTION = NAMESPACE + 'inplaneReferenceDirection'
MONITOR_NAME = NAMESPACE + 'monitorName'
PRIMARY_BEAM_DIRECTION = NAMESPACE + 'primaryBeamDirection'
PROJECTION_DIRECTION = NAMESPACE + 'projectionDirection'
SAMPLE_CIRCLES = NAMESPACE + 'sampleCircles'
SAMPLE_SURFACE_NORMAL_DIRECTION = NAMESPACE + 'sampleSurfaceNormalDirection'

DETECTORS_FOR_XRAYUTILS = NAMESPACE + "detectorGeometryForXrayutils"
DETECTOR = NAMESPACE + "Detector"
DETECTOR_ID = NAMESPACE +"ID"
PIXEL_DIRECTION1 = NAMESPACE + 'pixelDirection1'
PIXEL_DIRECTION2 = NAMESPACE + 'pixelDirection2'
CENTER_CHANNEL_PIXEL = NAMESPACE + 'centerChannelPixel'
NUMBER_OF_PIXELS = NAMESPACE + 'Npixels'
DETECTOR_SIZE = NAMESPACE + 'size'
DETECTOR_DISTANCE = NAMESPACE + 'distance'

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
        self.detectorDialog = parent
        self.root = None
        try:
            tree = ET.parse(filename)
            self.root = tree.getroot()
            self.instForXray = self.root.find(INST_FOR_XRAYUTILS)
            self.detectorForXrayutils = self.root.find(DETECTORS_FOR_XRAYUTILS)
            self.detectorGeometry = self.detectorForXrayutils.find(DETECTOR)
            self.sampleCirPosList = []
            self.sampleCirMotorList = []
            self.sampleCirAxisList = []
            self.loadFileIntoDialog(filename)
        except IOError as ex:
            QMessageBox.Warning("Please submit a valid Instrument Configuration File. \n\n Exception: " + ex)

    def loadFileIntoDialog(self, file):
        """Calls on the methods to fill the dialog with information.
        :param file: XML File
        :return:
        """
        self.detectorDialog.xmlFileName.setText(str(file))
        self.getDetectorCircles()
        self.getSampleCircles()
        self.setPrimaryBeamDiriction()
        self.setInplaneReferenceDirection()
        self.setSampleSurfaceNormalDirection()
        self.setProjectDirection()

        #  Calls on the method for the Detector Geometry information
        self.setPixelDirection()
        self.setCenterChannelPixel()
        self.setPixels()
        self.setSize()
        self.setDistance()

    def getSampleCircles(self):
        """Gets the circles from the XML file
        :return:
        """
        sampleCircles = self.instForXray.find(SAMPLE_CIRCLES)
        circles = sampleCircles.findall(NAMESPACE + "circleAxis")

        if circles is not None:

            for circle in circles:
                axis = circle.attrib[DIRECTION_AXIS]
                motor = circle.attrib[SPEC_MOTOR_NAME]
                self.setSampleCircles(axis, motor)

    def setSampleCircles(self, axis, motor):
        """Sets the sample circles in the Input Dialog.
        :param axis: Direction axis
        :param motor: Spec motor name
        :return:
        """
        self.detectorDialog.addNewSampleCircle()

        indx = len(self.detectorDialog.sampleCircleList) - 1
        for n in xrange(0, 6):
            if axis == self.detectorDialog.sampleCircleDirectionList[indx].itemText(n):
                self.detectorDialog.sampleCircleDirectionList[indx].setCurrentIndex(n)
            if motor == self.detectorDialog.sampleCircleMotorList[indx].itemText(n):
                self.detectorDialog.sampleCircleMotorList[indx].setCurrentIndex(n)

    def getDetectorCircles(self):
        """Gets the detector circles from the XML file.
        :return:
        """
        detectorCircles = self.instForXray.find(DETECTOR_CIRCLES)
        circles = detectorCircles.findall(NAMESPACE + "circleAxis")

        if circles is not None:

            for circle in circles:
                axis = circle.attrib[DIRECTION_AXIS]
                motor = circle.attrib[SPEC_MOTOR_NAME]
                self.setDetectorCircles(axis, motor)

    def setDetectorCircles(self, axis, motor):
        """Set the detector dialogs in the input dialog.
        :param axis: Direction axis
        :param motor: Spec motor name
        :return:
        """
        self.detectorDialog.addNewDetectorCircle()

        indx = len(self.detectorDialog.detectorCircleList) - 1
        for n in xrange(0, 6):
            if axis == self.detectorDialog.detectorCircleDirectionList[indx].itemText(n):
                self.detectorDialog.detectorCircleDirectionList[indx].setCurrentIndex(n)
            if motor == self.detectorDialog.detectorCircleMotorList[indx].itemText(n):
                self.detectorDialog.detectorCircleMotorList[indx].setCurrentIndex(n)

    def setPrimaryBeamDiriction(self):
        """Sets the primary direction based on the axis from the xml file.
        :return:
        """
        axisList = []
        primaryBeamDirection = self.instForXray.find(PRIMARY_BEAM_DIRECTION)
        axis = primaryBeamDirection.findall(NAMESPACE + "axis")

        if axis is not None:
            for x in axis:
                axisList.append(x.text.strip())

            if int(axisList[0]) == 0 and int(axisList[1]) == 1 and int(axisList[2]) == 0:
                 currentAxis = 'y'
            elif int(axisList[0]) == 1 and int(axisList[1]) == 1 and int(axisList[2]) == 0:
                currentAxis = 'x'
            else:
                currentAxis = 'z'

            for i in xrange(3):
                if self.detectorDialog.primaryBeamDirBox.itemText(i) == currentAxis:
                    self.detectorDialog.primaryBeamDirBox.setCurrentIndex(i)

    def setInplaneReferenceDirection(self):
        axisList = []
        inplaneRefDirBox = self.instForXray.find(INPLANE_REFERENCE_DIRECTION)
        axis = inplaneRefDirBox.findall(NAMESPACE + "axis")

        if axis is not None:
            for x in axis:
                axisList.append(x.text.strip())

            if int(axisList[0]) == 0 and int(axisList[1]) == 1 and int(axisList[2]) == 0:
                currentAxis = 'y'
            elif int(axisList[0]) == 1 and int(axisList[1]) == 1 and int(axisList[2]) == 0:
                currentAxis = 'x'
            else:
                currentAxis = 'z'

            for i in xrange(3):
                if self.detectorDialog.inplaneRefDirBox.itemText(i) == currentAxis:
                    self.detectorDialog.inplaneRefDirBox.setCurrentIndex(i)

    def setSampleSurfaceNormalDirection(self):
        axisList = []
        sampleSurfaceNormalDirBox = self.instForXray.find(SAMPLE_SURFACE_NORMAL_DIRECTION)
        axis = sampleSurfaceNormalDirBox.findall(NAMESPACE + "axis")

        if axis is not None:
            for x in axis:
                axisList.append(x.text.strip())

            if int(axisList[0]) == 0 and int(axisList[1]) == 1 and int(axisList[2]) == 0:
                currentAxis = 'y'
            elif int(axisList[0]) == 1 and int(axisList[1]) == 1 and int(axisList[2]) == 0:
                currentAxis = 'x'
            else:
                currentAxis = 'z'

            for i in xrange(3):
                if self.detectorDialog.sampleSurfaceNormalDirBox.itemText(i) == currentAxis:
                    self.detectorDialog.sampleSurfaceNormalDirBox.setCurrentIndex(i)

    def setProjectDirection(self):
        axisList = []
        projectionDirBox = self.instForXray.find(PROJECTION_DIRECTION)
        axis = projectionDirBox.findall(NAMESPACE + "axis")

        if axis is not None:
            for x in axis:
                axisList.append(x.text.strip())

            if int(axisList[0]) == 0 and int(axisList[1]) == 1 and int(axisList[2]) == 0:
                currentAxis = 'y'
            elif int(axisList[0]) == 1 and int(axisList[1]) == 1 and int(axisList[2]) == 0:
                currentAxis = 'x'
            else:
                currentAxis = 'z'

            for i in xrange(3):
                if self.detectorDialog.projectionDirBox.itemText(i) == currentAxis:
                    self.detectorDialog.projectionDirBox.setCurrentIndex(i)

    def setPixelDirection(self):
        pixelDirection1 = self.detectorGeometry.find(PIXEL_DIRECTION1)
        if pixelDirection1 is not None:
            for i in xrange(6):
                if self.detectorDialog.pixelDirectionBox1.itemText(i) == pixelDirection1.text.strip():
                    self.detectorDialog.pixelDirectionBox1.setCurrentIndex(i)

        pixelDirection2 = self.detectorGeometry.find(PIXEL_DIRECTION2)
        if pixelDirection2 is not None:
            for i in xrange(6):
                if self.detectorDialog.pixelDirectionBox2.itemText(i) == pixelDirection2.text.strip():
                    self.detectorDialog.pixelDirectionBox2.setCurrentIndex(i)

    def setCenterChannelPixel(self):
        centerChannel = self.detectorGeometry.find(CENTER_CHANNEL_PIXEL)
        text = centerChannel.text.split()

        if len(text) == 2:
            self.detectorDialog.centerChannelLnEdit1.setText(text[0].strip())
            self.detectorDialog.centerChannelLnEdit2.setText(text[1].strip())

    def setPixels(self):
        pixels = self.detectorGeometry.find(NUMBER_OF_PIXELS)
        text = pixels.text.split()

        if len(text) == 2:
            self.detectorDialog.nPixelsLnEdit1.setText(text[0].strip())
            self.detectorDialog.nPixelsLnEdit2.setText(text[1].strip())

    def setSize(self):
        size = self.detectorGeometry.find(DETECTOR_SIZE)
        text = size.text.split()

        if len(text) == 2:
            self.detectorDialog.detectorSizeLnEdit1.setText(text[0].strip())
            self.detectorDialog.detectorSizeLnEdit2.setText(text[1].strip())

    def setDistance(self):
        distance = self.detectorGeometry.find(DETECTOR_DISTANCE)
        text = distance.text

        if text.strip() != "":
            self.detectorDialog.distanceLnEdit.setText(text.strip())





