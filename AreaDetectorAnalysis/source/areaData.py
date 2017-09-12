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
from scipy import interpolate

# ---------------------------------------------------------------------------------------------------------------------#

class ValidataionError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
        print("\nValidatiaonError has been raised. Check the Error message.")


class AreaData(object):
    def __init__(self, lum_img, droi, proi, broi):
        self.lum_img = np.array(lum_img)
        dxc = droi[0]
        dyc = droi[1]
        dxw = droi[2]
        dyw = droi[3]
        pxc = proi[0]
        pyc = proi[1]
        pxw = proi[2]
        pyw = proi[3]
        bxc = broi[0]
        byc = broi[1]
        bxw = broi[2]
        byw = broi[3]

        if pxc - pxw / 2 < bxc - bxw / 2 or pxc + pxw / 2 > bxc + bxw / 2 or pyc - pyw / 2 < byc - byw / 2 or pyc + pyw / 2 > byc + byw / 2:
            raise ValidataionError("Vertices of peak area box must stay within Background area.")
            return

        self.dx_ndx = [int(round(dxc - dxw / 2)), int(round(dxc + dxw / 2)) + 1]
        self.dy_ndx = [int(round(dyc - dyw / 2)), int(round(dyc + dyw / 2)) + 1]
        self.px_ndx = [int(round(pxc - pxw / 2)), int(round(pxc + pxw / 2)) + 1]
        self.py_ndx = [int(round(pyc - pyw / 2)), int(round(pyc + pyw / 2)) + 1]
        self.bx_ndx = [int(round(bxc - bxw / 2)), int(round(bxc + bxw / 2)) + 1]
        self.by_ndx = [int(round(byc - byw / 2)), int(round(byc + byw / 2)) + 1]
        self.peak_img = self.lum_img[self.py_ndx[0]:self.py_ndx[1],
                        self.px_ndx[0]:self.px_ndx[1]]  # note y is rows, x is colums
        self.back_img = self.lum_img[self.by_ndx[0]:self.by_ndx[1], self.bx_ndx[0]:self.bx_ndx[1]]

    def areaIntegral(self):
        """Return values of area integration
           I(A1) = I(P) + I(B1)
           I(A2) = I(P) + I(B2)
           B1:B2 = A1:A2          # background intensity ratio = area ratio
           B2 = B1*A2/A1
           I(A1)+I(A2) = 2*I(P) + I(B1) + I(B2)
           I(B2) = I(A2-A1)*A2/(A2-A1), sig_I(B2) = sig_I(A2-A1)*A2/A2-A1
           I(B1) = I(B2)*A1/A2, sig_I(B1) = sig_I(B2)*A1/A2
           I(P) = 1/2*[I(A1)+I(A2) - I(B1) - I(B2)]
           sig_I(P) = sqrt(sig_I(A1)^2 + sig_I(A2)^2 + sig_I(B1)^2 + sig_I(B2)^2)
        """
        try:
            AreaP = float(self.peak_img.size)  # AreaP = A1
            AreaB = float(self.back_img.size)  # AreaB = A2
            IAP = float(np.sum(self.peak_img.flatten()));
            sigIAP = np.sqrt(IAP)
            IAB = float(np.sum(self.back_img.flatten()));
            sigIAB = np.sqrt(IAB)
            IB2 = AreaB * (IAB - IAP) / (AreaB - AreaP)
            sigIB2 = np.sqrt(sigIAP ** 2 + sigIAB ** 2) * AreaB / (AreaB - AreaP)
            IB1 = IB2 * AreaP / AreaB
            sigIB1 = sigIB2 * AreaP / AreaB
            I = 0.5 * (IAP + IAB - IB1 - IB2)
            sigI = 0.5 * np.sqrt(sigIAP ** 2.0 + sigIAB ** 2.0 + sigIB1 ** 2.0 + sigIB2 ** 2.0)
        except (RuntimeWarning, RuntimeError) as e:
            print(e)
        return I, sigI

    def lineIntegral(self, direction, deg):
        try:
            bxw, byw = self.back_img.shape
            if direction == 0:
                xp = np.arange(self.px_ndx[0], self.px_ndx[1])
                xb = np.arange(self.bx_ndx[0], self.bx_ndx[1])
                yb = np.sum(self.back_img, 0)
                yb_err = np.sqrt(yb)
            elif direction == 1:
                xp = np.arange(self.py_ndx[0], self.py_ndx[1])
                xb = np.arange(self.by_ndx[0], self.by_ndx[1])
                yb = np.sum(self.back_img, 1)
                yb_err = np.sqrt(yb)
            xb_sub = xb
            yb_sub = yb
            yb_err_sub = yb_err
            argndx = []
            for x in xp:
                argndx.append(np.argmin(abs(xb_sub - x)))
            xb_sub = np.delete(xb_sub, argndx)
            yb_sub = np.delete(yb_sub, argndx)
            yb_err_sub = np.delete(yb_err_sub, argndx)
            pln = np.polyfit(xb_sub, yb_sub, deg)
            polynomial = np.poly1d(pln)
            yb_sub_pln = polynomial(xb_sub)
            yb_sub_pln_stderr = np.sqrt(sum((yb_sub - yb_sub_pln) ** 2) / len(yb_sub))
            yb_pln = polynomial(xb)

            I = sum(yb - yb_pln)
            sigI = np.sqrt(sum(yb_err ** 2 + yb_sub_pln_stderr ** 2))
        except (RuntimeWarning, RuntimeError) as e:
            print(e)
        return xb, yb, yb_err, yb_pln, I, sigI

    def Integral2d(self, kx, ky):
        try:
            xp = range(self.px_ndx[0], self.px_ndx[1])  # x positions in peak area
            yp = range(self.py_ndx[0], self.py_ndx[1])  # y positions in peak area
            xb = range(self.bx_ndx[0], self.bx_ndx[1])  # x positions in background area
            yb = range(self.by_ndx[0], self.by_ndx[1])  # y positions in background area
            # x,y,z for 2d spline interpolation
            x = []
            y = []
            z = [];
            z_w_peak = []
            for i in xb:
                for j in yb:
                    z_w_peak.append(self.lum_img[j, i])
                    if (i in xp) and (j in yp):
                        pass
                    else:
                        x.append(i)
                        y.append(j)
                        z.append(self.lum_img[j, i])
            tck = interpolate.bisplrep(x, y, z, w=1. / np.sqrt(z), kx=kx, ky=ky, s=None)
            z_back = interpolate.bisplev(xb, yb, tck)
            z_w_peak = np.array(z_w_peak)
            z_wo_back = z_w_peak - np.array(z_back).flatten()
            z_wo_back_stderr = np.sqrt(z_w_peak)
            I = np.sum(z_wo_back, 0)
            sigI = np.sqrt(np.sum(z_wo_back_stderr ** 2))
            X, Y = np.meshgrid(xb, yb)
        except (RuntimeWarning, RuntimeError) as e:
            print(e)
        return X, Y, z_back.T, self.back_img, I, sigI