# -*- coding: utf-8 -*-
"""
Area Data Analysis software version 1.3

main:
    ada.py

local class module:
    areadata.py

compatible with:
    Python 2.7.9
    wxPython 3.0.2.0 msw (classic)
    NumPy 1.9.2
    SciPy 0.15.1
    Matplotlib 1.4.3
    Pillow 2.7.0

copyright: Changyong Park (cpark@ciw.edu), February 13, 2015
license: Free 

changes from the previous version:
    1. wxPython, NumPy, SciPy, Matplotlib, Pillow versions are updated
    2. For image library, use "from PIL import Image" instead of "import Image"

last modified:
    February 15, 2015
"""
import os
import sys
import time
import glob
import matplotlib
matplotlib.use('WXAgg')
matplotlib.rcParams.update({'font.size': 9})
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.patches import Rectangle
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import wx

from areadataOriginal import AreaData


class RedirectText(object):
    def __init__(self, aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self,string):
        self.out.WriteText(string)
        
class ColumnSelectionDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, id=-1, title="Select Columns from Meta Data", style=wx.DEFAULT_DIALOG_STYLE)
        self.hkl_H = wx.TextCtrl(self, -1, "1", style=wx.TE_CENTER, size=(1, .5))
        self.hkl_K = wx.TextCtrl(self, -1, "2", style=wx.TE_CENTER)        
        self.hkl_L = wx.TextCtrl(self, -1, "3", style=wx.TE_CENTER)        
        self.energy = wx.TextCtrl(self, -1, "4", style=wx.TE_CENTER)  
        self.mon = wx.TextCtrl(self, -1, "5", style=wx.TE_CENTER) 
        self.trans = wx.TextCtrl(self, -1, "6", style=wx.TE_CENTER) 
        okbutton = wx.Button(self, wx.ID_OK, "OK")
        cancelbutton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        
        gbox_ctrls=wx.GridSizer(rows=2,cols=6,hgap=1,vgap=1)
        gbox_ctrls.Add(wx.StaticText(self,-1,"H", style=wx.ALIGN_CENTER, size=.5))
        gbox_ctrls.Add(wx.StaticText(self,-1,"K", style=wx.ALIGN_CENTER), 1, wx.EXPAND, 0)
        gbox_ctrls.Add(wx.StaticText(self,-1,"L", style=wx.ALIGN_CENTER), 1, wx.EXPAND, 0)
        gbox_ctrls.Add(wx.StaticText(self,-1,"Energy", style=wx.ALIGN_CENTER), 1, wx.EXPAND, 0)
        gbox_ctrls.Add(wx.StaticText(self,-1,"Monitor", style=wx.ALIGN_CENTER), 1, wx.EXPAND, 0)
        gbox_ctrls.Add(wx.StaticText(self,-1,"Trans", style=wx.ALIGN_CENTER), 1, wx.EXPAND, 0)
        gbox_ctrls.Add(self.hkl_H, .5, wx.EXPAND, 0)
        gbox_ctrls.Add(self.hkl_K, 1, wx.EXPAND, 0)
        gbox_ctrls.Add(self.hkl_L, 1, wx.EXPAND, 0)
        gbox_ctrls.Add(self.energy, 1, wx.EXPAND, 0)
        gbox_ctrls.Add(self.mon, 1, wx.EXPAND, 0)
        gbox_ctrls.Add(self.trans, 1, wx.EXPAND, 0)
                        
        hbox_buttons=wx.BoxSizer(wx.HORIZONTAL)        
        hbox_buttons.Add(okbutton, 0, wx.CENTRE|wx.ALL, 1)
        hbox_buttons.Add(cancelbutton, wx.CENTRE|wx.ALL, 1)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(gbox_ctrls, 0, wx.GROW, .5)
        # sizer.Add(hbox_buttons, 0, wx.CENTRE|wx.ALL, 1)
        sizer.Fit(self)
        self.SetSizer(sizer)
        self.Layout()
        
    def getColumns(self):
        Hcol=int(self.hkl_H.GetValue())
        Kcol=int(self.hkl_K.GetValue())
        Lcol=int(self.hkl_L.GetValue())
        Ecol=int(self.energy.GetValue())
        Mcol=int(self.mon.GetValue())
        Tcol=int(self.trans.GetValue())
        return [Hcol,Kcol,Lcol,Ecol,Mcol,Tcol]
        
        
class AreaDetectorAnalysisFrame(wx.Frame):
    """Frame class"""
    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=-1, title="Area Data Analysis v1.3", pos=wx.DefaultPosition, size=(1024,720))
        self.panel = wx.Panel(self, -1)   # </
        self.createMenubar()  # </
        self.filelisttitle = wx.StaticText(self.panel, -1, label="Image files to load")  # </
        self.filelist = []  # </
        self.metadatalist = []  # </
        self.is_metadata_read = False  # </
        self.imarray = []  # </
        self.savedatafile = None  # </
        self.bad_pixels_on = False  # </
        self.bad_pixels = []  # </
        self.replacing_pixels = []  # </
        self.efficiency_on = False  # </

        self.filelistbox = wx.ListBox(self.panel, -1, wx.DefaultPosition, (250,350), [], wx.LB_SINGLE|wx.LB_NEEDED_SB|wx.HSCROLL) # </
        self.removefilebutton = wx.Button(self.panel, -1, "Re&move", wx.DefaultPosition, wx.DefaultSize)  # </
        self.removeallfilebutton = wx.Button(self.panel, -1, "Remove &All", wx.DefaultPosition, wx.DefaultSize)  # </
        self.resetdataroi = wx.Button(self.panel, -1, "Reset", wx.DefaultPosition, wx.DefaultSize)  # </
        self.saveandnext = wx.Button(self.panel, -1, "Save and Next", wx.DefaultPosition, wx.DefaultSize)  # </
        self.save = wx.Button(self.panel, -1, "Save", wx.DefaultPosition, wx.DefaultSize)  # </
        self.next = wx.Button(self.panel, -1, "Next", wx.DefaultPosition, wx.DefaultSize)  # </
        self.saveas = wx.Button(self.panel, -1, "Save As", wx.DefaultPosition, wx.DefaultSize)  # </
        self.log = wx.TextCtrl(self.panel, -1, pos=wx.DefaultPosition, size=(300,140),
                               style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)  # </
        self.sc_dxc = wx.SpinCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize)  # </
        self.sc_dyc = wx.SpinCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize)  # </
        self.sc_dxw = wx.SpinCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize)  # </
        self.sc_dyw = wx.SpinCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize)  # </
        self.sc_pxc = wx.SpinCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize)  # </
        self.sc_pyc = wx.SpinCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize)  # </
        self.sc_pxw = wx.SpinCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize)  # </
        self.sc_pyw = wx.SpinCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize)  # </
        self.sc_bxc = wx.SpinCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize)  # </
        self.sc_byc = wx.SpinCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize)  # </
        self.sc_bxw = wx.SpinCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize)  # </
        self.sc_byw = wx.SpinCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize)  # </
        self.sc_pln_order1 = wx.SpinCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize, 1,1,5)  # </
        self.sc_pln_order2 = wx.SpinCtrl(self.panel, -1, "", wx.DefaultPosition, wx.DefaultSize, 1,1,5)  # </
        self.sc_pln_order1.SetRange(1,5); self.sc_pln_order1.SetValue(1)  # </
        self.sc_pln_order2.SetRange(1,5); self.sc_pln_order2.SetValue(1)  # </
        self.hkl_H = wx.TextCtrl(self.panel, -1, "", style=wx.TE_CENTER)  # </
        self.hkl_K = wx.TextCtrl(self.panel, -1, "", style=wx.TE_CENTER)  # </
        self.hkl_L = wx.TextCtrl(self.panel, -1, "", style=wx.TE_CENTER)  # </
        self.energy = wx.TextCtrl(self.panel, -1, "", style=wx.TE_RIGHT)  # </
        self.mon = wx.TextCtrl(self.panel, -1, "", style=wx.TE_RIGHT)     # </
        self.trans = wx.TextCtrl(self.panel, -1, "", style=wx.TE_RIGHT)   # </
        self.figure1 = plt.figure(1, figsize=(4,2.5), dpi=100)  # </
        self.figure2 = plt.figure(2, figsize=(4,2.5), dpi=100)  # </
        self.figure3 = plt.figure(3, figsize=(4,2.5), dpi=100)  # </
        self.canvas1 = FigureCanvas(self.panel, -1, self.figure1)  # </
        self.canvas2 = FigureCanvas(self.panel, -1, self.figure2)  # </
        self.canvas3 = FigureCanvas(self.panel, -1, self.figure3)  # </
        # Sizers        
        # File List
        vbox_file=wx.BoxSizer(wx.VERTICAL)                                      
        vbox_file.Add(self.filelisttitle, 0, wx.ALIGN_CENTRE, 0)  # </
        vbox_file.Add(self.filelistbox, 1, wx.EXPAND|wx.ALL, 1)  # </
        vbox_file.Add(self.removefilebutton, 0, wx.EXPAND, 0)  # </
        vbox_file.Add(self.removeallfilebutton, 0, wx.EXPAND, 0)  # </
        # Various Controls
        gbox_roi=wx.GridSizer(rows=4, cols=5, hgap=2, vgap=2)  # </
        gbox_roi.Add(self.resetdataroi, 1, wx.EXPAND, 0)  # </
        gbox_roi.Add(wx.StaticText(self.panel,-1,"x_cen", style=wx.ALIGN_CENTER),0, wx.GROW, 0)  # </
        gbox_roi.Add(wx.StaticText(self.panel,-1,"y_cen", style=wx.ALIGN_CENTER),0, wx.GROW, 0)  # </
        gbox_roi.Add(wx.StaticText(self.panel,-1,"x_width", style=wx.ALIGN_CENTER),0, wx.GROW, 0)  # </
        gbox_roi.Add(wx.StaticText(self.panel,-1,"y_width", style=wx.ALIGN_CENTER),0, wx.GROW, 0)  # </
        gbox_roi.Add(wx.StaticText(self.panel,-1,"Data ROI"),1, wx.EXPAND, 0)  # </
        gbox_roi.Add(self.sc_dxc, 1, wx.EXPAND, 0)  # </
        gbox_roi.Add(self.sc_dyc, 1, wx.EXPAND, 0)  # </
        gbox_roi.Add(self.sc_dxw, 1, wx.EXPAND, 0)  # </
        gbox_roi.Add(self.sc_dyw, 1, wx.EXPAND, 0)  # </
        gbox_roi.Add(wx.StaticText(self.panel,-1,"Peak Area"),1, wx.EXPAND, 0)  # </
        gbox_roi.Add(self.sc_pxc, 1, wx.EXPAND, 0)  # </
        gbox_roi.Add(self.sc_pyc, 1, wx.EXPAND, 0)  # </
        gbox_roi.Add(self.sc_pxw, 1, wx.EXPAND, 0)  # </
        gbox_roi.Add(self.sc_pyw, 1, wx.EXPAND, 0)  # </
        gbox_roi.Add(wx.StaticText(self.panel,-1,"Bkgd Area"),1, wx.EXPAND|wx.BOTTOM, 0)  # </
        gbox_roi.Add(self.sc_bxc, 1, wx.EXPAND|wx.BOTTOM, 0)  # </
        gbox_roi.Add(self.sc_byc, 1, wx.EXPAND|wx.BOTTOM, 0)  # </
        gbox_roi.Add(self.sc_bxw, 1, wx.EXPAND|wx.BOTTOM, 0)  # </
        gbox_roi.Add(self.sc_byw, 1, wx.EXPAND|wx.BOTTOM, 0)  # </
        gbox_roi.Fit(self.panel)  # </
        hbox_pln=wx.BoxSizer(wx.HORIZONTAL)  # </
        hbox_pln.Add(wx.StaticText(self.panel,-1,"Bkgd Fit Order1"),1, wx.EXPAND, 0)   # </
        hbox_pln.Add(self.sc_pln_order1, 1, wx.EXPAND|wx.ALL, 0)  # </
        hbox_pln.Add(wx.StaticText(self.panel,-1,"Bkgd Fit Order2"),1, wx.EXPAND, 0)  # </
        hbox_pln.Add(self.sc_pln_order2, 1, wx.EXPAND|wx.ALL, 0)  # </
        hbox_pln.Fit(self.panel)  # </
        hbox_hkl1=wx.BoxSizer(wx.HORIZONTAL)  # </
        hbox_hkl1.Add(wx.StaticText(self.panel,-1,"H", style=wx.ALIGN_CENTER),1, wx.EXPAND, 0)  # </
        hbox_hkl1.Add(wx.StaticText(self.panel,-1,"K", style=wx.ALIGN_CENTER),1, wx.EXPAND, 0)  # </
        hbox_hkl1.Add(wx.StaticText(self.panel,-1,"L", style=wx.ALIGN_CENTER),1, wx.EXPAND, 0)  # </
        hbox_hkl1.Add(wx.StaticText(self.panel,-1,"Energy", style=wx.ALIGN_CENTER),2, wx.EXPAND, 0)  # </
        hbox_hkl1.Add(wx.StaticText(self.panel,-1,"MON", style=wx.ALIGN_CENTER),2, wx.EXPAND, 0)  # </
        hbox_hkl1.Add(wx.StaticText(self.panel,-1,"Trans", style=wx.ALIGN_CENTER),2, wx.EXPAND, 0)  # </
        hbox_hkl2=wx.BoxSizer(wx.HORIZONTAL)   # </
        hbox_hkl2.Add(self.hkl_H, 5, wx.EXPAND|wx.ALL, 1)  # </
        hbox_hkl2.Add(self.hkl_K, 5, wx.EXPAND|wx.ALL, 1)  # </
        hbox_hkl2.Add(self.hkl_L, 5, wx.EXPAND|wx.ALL, 1)  # </
        hbox_hkl2.Add(self.energy, 9, wx.EXPAND|wx.ALL, 1)  # </
        hbox_hkl2.Add(self.mon, 9, wx.EXPAND|wx.ALL, 1)  # </
        hbox_hkl2.Add(self.trans, 9, wx.EXPAND|wx.ALL, 1)  # </
        gbox_hkl=wx.BoxSizer(wx.VERTICAL)  # </
        gbox_hkl.Add(hbox_hkl1, 1, wx.EXPAND, 0)  # </
        gbox_hkl.Add(hbox_hkl2, 1, wx.EXPAND, 0)  # </
        hbox_save=wx.BoxSizer(wx.HORIZONTAL)  # </
        hbox_save.Add(self.saveandnext, 1, wx.EXPAND|wx.ALL, 0)  # </
        hbox_save.Add(self.save, 1, wx.EXPAND|wx.ALL, 0)  # </
        hbox_save.Add(self.next, 1, wx.EXPAND|wx.ALL, 0)  # </
        hbox_save.Add(self.saveas, 1, wx.EXPAND|wx.ALL, 0)  # </
        # Layout the Sizers
        vbox_control=wx.BoxSizer(wx.VERTICAL)  # </
        vbox_control.Add(gbox_roi, 20, wx.EXPAND|wx.BOTTOM, 4)  # </
        vbox_control.Add(wx.StaticLine(self.panel,-1,style=wx.LI_HORIZONTAL), 0, wx.EXPAND, 0)  # </
        vbox_control.Add(hbox_pln, 5, wx.EXPAND|wx.TOP|wx.BOTTOM, 4)  # </
        vbox_control.Add(wx.StaticLine(self.panel,-1,style=wx.LI_HORIZONTAL), 0, wx.EXPAND, 0)  # </
        vbox_control.Add(gbox_hkl, 8, wx.EXPAND|wx.TOP|wx.BOTTOM, 4)  # </
        gbox_fnc=wx.GridSizer(rows=2, cols=2, hgap=2, vgap=2)  # </
        gbox_fnc.Add(self.canvas1, 1, wx.EXPAND, 0)  # </
        gbox_fnc.Add(self.canvas2, 1, wx.EXPAND, 0)  # </
        gbox_fnc.Add(self.canvas3, 1, wx.EXPAND, 0)  # </
        gbox_fnc.Add(vbox_control, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 0)  # </
        vbox2=wx.BoxSizer(wx.VERTICAL)  # </
        vbox2.Add(gbox_fnc, 13, wx.EXPAND, 0)  # </
        vbox2.Add(self.log, 3, wx.EXPAND, 0)  # </
        vbox2.Add(hbox_save, 0, wx.EXPAND|wx.TOP, 2)  # </
        sizer=wx.BoxSizer(wx.HORIZONTAL)  # </
        sizer.Add(vbox_file, 0, wx.EXPAND|wx.ALL, 0)  # </
        sizer.Add(wx.StaticLine(self.panel,-1,style=wx.LI_VERTICAL), 0, wx.EXPAND, 10)  # </
        sizer.Add(vbox2, 3, wx.EXPAND|wx.ALL, 0)  # </
        sizer.Fit(self.panel)  # </
        self.panel.SetSizer(sizer)  # </
        self.panel.Layout()  # </

        self.Bind(wx.EVT_LISTBOX, self.OnListSelected, self.filelistbox)  # </
        self.Bind(wx.EVT_BUTTON, self.OnRemoveFileButton, self.removefilebutton)  # </
        self.Bind(wx.EVT_BUTTON, self.OnRemoveAllFileButton, self.removeallfilebutton)  # </
        self.Bind(wx.EVT_BUTTON, self.OnResetDataROI, self.resetdataroi)  # </
        self.Bind(wx.EVT_BUTTON, self.OnSaveNext, self.saveandnext)  # </
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.save)  # </
        self.Bind(wx.EVT_BUTTON, self.OnNext, self.next)  # </
        self.Bind(wx.EVT_BUTTON, self.OnSaveAs, self.saveas)  # </
        self.Bind(wx.EVT_SPINCTRL, self.RedrawImage)  # </
        self.canvas1.mpl_connect('motion_notify_event', self.OnMouseMove)  # </
        self.canvas1.mpl_connect('button_press_event', self.OnMousePress)  # </
        self.canvas1.mpl_connect('button_release_event', self.OnMouseRelease)  # </

        redir = RedirectText(self.log)
        sys.stdout=redir
        redir2 = RedirectText(self.log)
        sys.stderr=redir2
        
    def menuData(self): 
        return (    # </
        ("&File", (  # </
            ("&Open Image Files", "List up the image files to open", self.OnOpenImageFiles),  # </
            ("&Read Metadata File", "Read a metadata file", self.OnReadMetaDataFile),  # </
            ("","",""),  # </
            ("&Save and Next", "Save the result and go to the next image", self.OnSaveNext),  # </
            ("&Save", "Save the result", self.OnSave),  # </
            ("Ne&xt", "Go to next image ...", self.OnNext),  # </
            ("&Save As", "Save as a new file", self.OnSaveAs),  # </
            ("","",""),  # </
            ("E&xit", "Close window and exit program", self.OnFileExit))),  # </
        ("&Options", (  # </
            ("Bad Fixels", (  # </
                ("On", "Toggle on bad pixel correction", self.OnBadpixelCorrectionOn),  # </
                ("Off", "Toggle off bad pixel correction", self.OnBadpixelCorrectionOff))),  # </
            ("Flatfiled Correction", (
                ("On", "Toggle on pixel by pixel efficiency correction", self.OnFlatfieldCorrectionOn),  # </
                ("Off", "Toggle off pixel by pixel efficiency correction", self.OnFlatfieldCorrectionOff))),  # </
            ("","",""),  # </
            ("Select New Data Column", "Select New Data Columns", self.OnSelectDataColumn))))  # </
             
    def createMenubar(self):
        print self.menuData()  # </
        menuBar = wx.MenuBar()  # </
        for eachMenuData in self.menuData():  # </
            menuLabel = eachMenuData[0]  # </
            menuItems = eachMenuData[1]  # </
            menuBar.Append(self.createMenu(menuItems), menuLabel)  # </
        self.SetMenuBar(menuBar)  # </
       
    def createMenu(self, menuItems):  # </
        menu = wx.Menu()  # </
        for eachItem in menuItems:  # </
            if len(eachItem) == 2:  # </
                label = eachItem[0]  # </
                subMenu = self.createMenu(eachItem[1])  # </
                menu.AppendMenu(-1, label, subMenu)  # </
            else:  # </
                self.createMenuItem(menu, *eachItem)  # </
        return menu  # </

    def createMenuItem(self, menu, label, status, handler,   # </
                       kind=wx.ITEM_NORMAL):  # </
        if not label:  # </
            menu.AppendSeparator()  # </
            return  # </
        menuItem = menu.Append(-1, label, status, kind)  # </
        self.Bind(wx.EVT_MENU, handler, menuItem)  # </
        
    def OnOpenImageFiles(self, event):
        dlg = wx.DirDialog(self, "Choose directory", name="Directory")  # </
        if dlg.ShowModal() == wx.ID_OK:  # </
            path = dlg.GetPath()  # </

            images = os.listdir(path)  # </
            print path
            print os.path.abspath(images[1])  # </

            for img in images:  # </
                self.filelistbox.Append(img)  # wxPython ListBox method  # </
                if path.find("/") == 0:  # </
                    self.filelist.append(path + '/' + img)  # </
                elif path.find("\\") == 0:  # </
                    self.filelist.append(path + '\\'+img)  # </

                self.metadatalist.append([])  # </

        dlg.Destroy()  # </

    def OnReadMetaDataFile(self, event): 
        dlg = wx.FileDialog(self, "Open a metadata file...", os.getcwd(), 
                            style=wx.CHANGE_DIR, wildcard="*.*")
        if dlg.ShowModal() == wx.ID_OK: 
            newpath = dlg.GetPath()
            newpath = newpath.replace(newpath.split('\\')[-1],'')
            newfile = dlg.GetFilename()
            lines = np.genfromtxt(newfile,dtype=None)
            if self.is_metadata_read == False:
                scdlg = ColumnSelectionDialog()
                if scdlg.ShowModal() == wx.ID_OK:
                    cols = scdlg.getColumns()
                    self.Hcol = cols[0]
                    self.Kcol = cols[1]
                    self.Lcol = cols[2]
                    self.Ecol = cols[3]
                    self.Mcol = cols[4]
                    self.Tcol = cols[5]
                scdlg.Destroy() 
                self.is_metadata_read = True
            for line in lines:
                line = list(line)
                self.filelistbox.Append(line[0])
                self.filelist.append(newpath+line[0])    
                self.metadatalist.append(line)
            print("\nChange working directory to: "+newpath)
            print("Read metadata file: "+newfile)
        dlg.Destroy()
        
    def OnSave(self, event): 
        if self.savedatafile == None:
            savedlg = wx.FileDialog(self, "Save the data into a file", os.getcwd(), 
                            style=wx.SAVE|wx.OVERWRITE_PROMPT, 
                            wildcard="Text File (*.txt)|*.txt|All File (*.*)|*.*")
            if savedlg.ShowModal() == wx.ID_OK: 
                self.savedatafile = savedlg.GetFilename()
                self.is_savedatafile_new = True
            savedlg.Destroy()
            self.fileSave()
        else:
            self.fileSave()
    
    def fileSave(self):
        try:
            H = float(self.hkl_H.GetValue())
            K = float(self.hkl_K.GetValue())
            L = float(self.hkl_L.GetValue())
            E = float(self.energy.GetValue())
            M = float(self.mon.GetValue())
            T = float(self.trans.GetValue())
            dataout = {'H':H, 'K':K, 'L':L, 'E':E, 'M':M, 'T':T,\
                        'I1d0':self.I1d0, 'sigI1d0':self.sigI1d0, 'I1d1':self.I1d1, 'sigI1d1':self.sigI1d1, 'I2d':self.I2d, 'sigI2d':self.sigI2d}
            saveline = '%(H)6.3f %(K)6.3f %(L)6.3f %(E)8.4f %(M)12.5e %(T)12.5e %(I1d0)16.4f %(sigI1d0)16.4f %(I1d1)16.4f %(sigI1d1)16.4f %(I2d)16.4f %(sigI2d)16.4f\n'
            if self.is_savedatafile_new == True:
                with open(self.savedatafile, 'a+') as f:
                    f.write("# 0:H, 1:K, 2:L, 3:E, 4:M, 5:T, 6:I1d_inplane, 7:sigI1d_inplne, 8:I1d_transverse, 9:sigI1d_transverse, 10:I2d, 11:sigI2d\n")
                    f.write(saveline % dataout)
                self.is_savedatafile_new = False
            else:
                with open(self.savedatafile,'a+') as f:
                    f.write(saveline % dataout)
            print("\n# The result has been appended to \""+self.savedatafile+"\"")
        except ValueError:
            pass
    
    def OnNext(self, event): 
        try:
            newndx = self.filendx + 1
            self.filelistbox.Select(newndx)
            self.filendx = self.filelistbox.GetSelection()
            if self.filendx == newndx-1:
                print("# The last line of list has been reached.")
            else:
                self.OnListSelected(event)
        except (AttributeError, IndexError):
            event.Skip()
    
    def OnSaveNext(self, event):
        self.OnSave(event)  # </
        self.OnNext(event)  # </
    
    def OnSaveAs(self, event): 
        savedlg = wx.FileDialog(self, "Save the data into a file", os.getcwd(), 
                               style=wx.SAVE|wx.OVERWRITE_PROMPT, 
                               wildcard="Text File (*.txt)|*.txt|All File (*.*)|*.*")
        if savedlg.ShowModal() == wx.ID_OK: 
            self.savedatafile = savedlg.GetFilename()
            self.is_savedatafile_new = True
            self.OnSave(event)
        savedlg.Destroy()

    def OnFileExit(self, event):
        self.Close(True)  # </

    def OnColor(self, event):
        dlg = wx.ColourDialog(self)
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            self.linecolor = dlg.GetColourData().GetColour()
        dlg.Destroy()
        
    def OnSelectDataColumn(self, event):
        scdlg = ColumnSelectionDialog()
        if scdlg.ShowModal() == wx.ID_OK:
            cols = scdlg.getColumns()
            self.Hcol = cols[0]
            self.Kcol = cols[1]
            self.Lcol = cols[2]
            self.Ecol = cols[3]
            self.Mcol = cols[4]
            self.Tcol = cols[5]
        scdlg.Destroy()
        self.is_metadata_read = True 
        
    def OnRemoveFileButton(self, event):
        try:  # </
            ndx = self.filelistbox.GetSelection()  # </
            self.filelistbox.Delete(ndx) # wxPython ListBox method  # </
            self.filelist.remove(self.filelist[ndx]) # Python list method  # </
            self.metadatalist.remove(self.metadatalist[ndx])   # </
            if len(self.filelist) == 0:    # </
                self.is_metadata_read = False   # </
        except IndexError:   # </
            event.Skip()   # </

    def OnRemoveAllFileButton(self, event):
        try:  # </
            self.filelistbox.Clear() # wxPython ListBox method  # </
            self.filelist = [] # Python list method  # </
            self.metadatalist = []  # </
            self.is_metadata_read = False  # </
        except IndexError as e:  # </
            print(e)  # </
            event.Skip()  # </
        
    def OnListSelected(self, event):
        try:  # </
            self.filendx = self.filelistbox.GetSelection()  # </
            self.curimg = Image.open(self.filelist[self.filendx])  # </
            self.imarray = np.array(self.curimg)  # </
            if self.efficiency_on == True:  # </
                self.imarray = self.imarray/self.efficiencyarray  # </
            if self.bad_pixels_on == True:  # </
                for i in range(len(self.bad_pixels)):  # </
                    self.imarray[self.bad_pixels[i][1],self.bad_pixels[i][0]] = \
                    self.imarray[self.replacing_pixels[i][1],self.replacing_pixels[i][0]]    # </
            if self.metadatalist[self.filendx]:  # </
                self.hkl_H.SetValue(str('%4.3f' % self.metadatalist[self.filendx][self.Hcol]))  # </
                self.hkl_K.SetValue(str('%4.3f' % self.metadatalist[self.filendx][self.Kcol]))  # </
                self.hkl_L.SetValue(str('%4.3f' % self.metadatalist[self.filendx][self.Lcol]))  # </
                self.energy.SetValue(str('%6.4f' % self.metadatalist[self.filendx][self.Ecol]))  # </
                self.mon.SetValue(str('%12d' % self.metadatalist[self.filendx][self.Mcol]))  # </
                self.trans.SetValue(str('%6.5e' % self.metadatalist[self.filendx][self.Tcol]))  # </
            elif not self.metadatalist[self.filendx]:  # </
                self.hkl_H.SetValue("nan")  # </
                self.hkl_K.SetValue("nan")  # </
                self.hkl_L.SetValue("nan")  # </
                self.energy.SetValue("nan")  # </
                self.mon.SetValue("nan")  # </
                self.trans.SetValue("nan")  # </
            self.RedrawImage(event)  # </
        except IndexError as e:  # </
            print(e)  # </
            event.Skip()  # </

    def OnMousePress(self, event):  # </
        if event.button == 1 and event.xdata and event.ydata:  # </
            self.mouse1_is_pressed = True   # </
            self.mousex0 = event.xdata  # </
            self.mousey0 = event.ydata  # </
        elif event.button == 3 and event.xdata and event.ydata:  # </
            self.mouse3_is_pressed = True  # </
        else:  # </
            pass  # </
        
    def OnMouseMove(self, event):
        """Get image coordinates and display"""
        try:  # </
            if self.imarray.any():  # </
                if event.inaxes:  # </
                    ix,iy = event.xdata, event.ydata  # </
                    iz = self.imarray[np.int(round(iy)),np.int(round(ix))]  # </
                    self.SetStatusText("p=("+str(int(round(ix)))+', '+str(int(round(iy)))+"), I="+str(iz))  # </
                    if self.mouse1_is_pressed == True:  # </
                        xw = ix-self.mousex0  # </
                        yw = iy-self.mousey0  # </
                        ax = self.figure1.gca()  # </
                        rect=Rectangle((self.mousex0,self.mousey0),xw,yw,linestyle='solid',color='magenta',fill=True,alpha=0.4)  # </
                        ax.add_patch(rect)  # </
                        for item in ax.findobj(match=Rectangle)[:-2]:  # </
                           item.remove()  # </
                        self.canvas1.draw()       # </
                else:  # </
                    self.SetStatusText("")  # </
        except (AttributeError, IndexError):  # </
            pass
                        
    def OnMouseRelease(self, event):
        try:   # </
            if event.button == 1:  # </
                self.mouse1_is_pressed = False  # </
                self.mousex1 = event.xdata  # </
                self.mousey1 = event.ydata  # </
                self.sc_dxc.SetValue(int(abs(self.mousex1+self.mousex0)/2))  # </
                self.sc_dyc.SetValue(int(abs(self.mousey1+self.mousey0)/2))  # </
                self.sc_pxc.SetValue(int(abs(self.mousex1+self.mousex0)/2))  # </
                self.sc_pyc.SetValue(int(abs(self.mousey1+self.mousey0)/2))  # </
                self.sc_bxc.SetValue(int(abs(self.mousex1+self.mousex0)/2))  # </
                self.sc_byc.SetValue(int(abs(self.mousey1+self.mousey0)/2))      # </
                if abs(self.mousex1-self.mousex0) < 1 or abs(self.mousey1-self.mousey0) < 1:  # </
                    pass  # </
                else:  # </
                    self.sc_dxw.SetValue(int(abs(self.mousex1-self.mousex0)))  # </
                    self.sc_dyw.SetValue(int(abs(self.mousey1-self.mousey0)))  # </
                    self.sc_pxw.SetValue(int(abs(self.mousex1-self.mousex0)*0.3))  # </
                    self.sc_pyw.SetValue(int(abs(self.mousey1-self.mousey0)*0.3))  # </
                    self.sc_bxw.SetValue(int(abs(self.mousex1-self.mousex0)*0.6))  # </
                    self.sc_byw.SetValue(int(abs(self.mousey1-self.mousey0)*0.6))  # </
            elif event.button == 3:  # </
                self.mouse3_is_pressed = False  # </
                self.sc_dxw.SetValue(self.sc_dxw.GetValue()*1.25)  # </
                self.sc_dyw.SetValue(self.sc_dyw.GetValue()*1.25)  # </
            self.RedrawImage(event)  # </
        except AttributeError:  # </
            pass  # </

    def OnBadpixelCorrectionOn(self, event):
        dlg = wx.FileDialog(self, "Open a bad pixel file...", os.getcwd(), 
                            style=wx.CHANGE_DIR, wildcard="*.*")
        if dlg.ShowModal() == wx.ID_OK: 
            newpath = dlg.GetPath()
            f = open(newpath, 'r')
            lines = f.readlines()
            f.close()
            print(lines)
        try:
            for line in lines:
                if len(line)>6:
                    bp = int(line.split()[0].split(',')[0]),int(line.split()[0].split(',')[1])
                    rp = int(line.split()[1].split(',')[0]),int(line.split()[1].split(',')[1])
                    self.bad_pixels.append(bp)
                    self.replacing_pixels.append(rp)
            print("Bad pixels: ")
            print(self.bad_pixels)
            print("\nare replaced with: ")
            print(self.replacing_pixels)
            self.bad_pixels_on = True
        except IndexError as e:
            print("In OnBadpixelCorrection: ")
            print(e)

    def OnBadpixelCorrectionOff(self, event):
        self.bad_pixels_on = False
            
    def OnFlatfieldCorrectionOn(self, event):
        dlg = wx.FileDialog(self, "Open a flatfield efficiency file...", os.getcwd(), 
                            style=wx.CHANGE_DIR, wildcard="*.*")
        if dlg.ShowModal() == wx.ID_OK:
            newpath = dlg.GetPath()
            self.efficiencyarray = np.array(Image.open(newpath))
            self.efficiency_on = True
            
    def OnFlatfieldCorrectionOff(self, event):
        self.efficiency_on = False

    def RedrawImage(self, event):
        """Resize and draw a numpy array image on the events of image mode 
           change, resizing the frame, and choosing a file from the list. 
           There must be only one choice for the image mode and one current 
           size of figure canvas to determine the image size. 
        """
        try:  # </
            if self.imarray.any():  # </
                self.resetRoiRange()  # </
                ih,iw = self.imarray.shape  # </
                droi,proi,broi = self.getRoiValues()  # </
                if droi == (0,0,0,0):  # </
                    self.sc_dxc.SetValue(iw/2)  # </
                    self.sc_dyc.SetValue(ih/2)  # </
                    self.sc_dxw.SetValue(iw)   # </
                    self.sc_dyw.SetValue(ih)  # </
                    self.RedrawImage(event)  # </
                    return    # </
                else:  # </
                    h,bins = np.histogram(self.imarray)  # </
                    vmin = bins[0]  # </
                    vmax = bins[-1]   # </
                    dxlim = [droi[0]-droi[2]/2.-0.5,droi[0]+droi[2]/2.+0.5]  # </
                    dylim = [droi[1]+droi[3]/2.-0.5,droi[1]-droi[3]/2.+0.5]  # </
                    px = [proi[0]-proi[2]/2., proi[0]+proi[2]/2., proi[0]+proi[2]/2., proi[0]-proi[2]/2., proi[0]-proi[2]/2.]  # </
                    py = [proi[1]-proi[3]/2., proi[1]-proi[3]/2., proi[1]+proi[3]/2., proi[1]+proi[3]/2., proi[1]-proi[3]/2.]  # </
                    bx = [broi[0]-broi[2]/2., broi[0]+broi[2]/2., broi[0]+broi[2]/2., broi[0]-broi[2]/2., broi[0]-broi[2]/2.]  # </
                    by = [broi[1]-broi[3]/2., broi[1]-broi[3]/2., broi[1]+broi[3]/2., broi[1]+broi[3]/2., broi[1]-broi[3]/2.]  # </
                    self.figure1.clear()   # </
                    ax = self.figure1.gca() # this is important line to make image visible  # </
                    ax.imshow(self.imarray,interpolation='none',vmin=vmin,vmax=vmax)  # </
                    ax.set_xlim(dxlim)  # </
                    ax.set_ylim(dylim)  # </
                    ax.plot(px,py,'y-',linewidth=1.0)  # </
                    ax.plot(bx,by,'g-',linewidth=1.0)  # </
                    self.canvas1.draw()  # </
                    if (0 in proi) or (0 in broi):  # </
                        pass  # </
                    else:  # </
                        self.areaIntegrationShow(self.imarray, droi, proi, broi)  # </
        except AttributeError:
            pass
            
    def areaIntegrationShow(self,lum_img,droi,proi,broi):  # </
        areadata = AreaData(lum_img, droi, proi, broi)  # </
        self.I2d, self.sigI2d = areadata.areaIntegral()  # </
        xb2,yb2,yb2_err,yb2_pln,self.I1d1, self.sigI1d1 = areadata.lineIntegral(1,self.sc_pln_order2.GetValue())  # </
        xb3,yb3,yb3_err,yb3_pln,self.I1d0, self.sigI1d0 = areadata.lineIntegral(0,self.sc_pln_order1.GetValue())  # </
        # plot in canvas2          # </
        self.figure2.clear()  # </
        self.figure2.add_subplot(111)  # </
        ax2 = self.figure2.gca()  # </
        ax2.errorbar(xb2,yb2,yerr=yb2_err,fmt='ro-',capsize=2.0)  # </
        ax2.plot(xb2,yb2_pln,'bo--', markerfacecolor='none')  # </
        ax2.set_title("1D Integration(2)",fontsize=10)  # </
        ax2.set_xlabel("y (pixel)")  # </
        ax2.set_ylabel("Int. (counts)")  # </
        self.figure2.tight_layout()  # </
        self.canvas2.draw()  # </
        # plot in canvas3  # </
        self.figure3.clear()  # </
        self.figure3.add_subplot(111)  # </
        ax3 = self.figure3.gca()  # </
        ax3.errorbar(xb3,yb3,yerr=yb3_err,fmt='ro-',capsize=2.0)  # </
        ax3.plot(xb3,yb3_pln,'bo--',markerfacecolor='none')  # </
        ax3.set_title("1D Integration(1)",fontsize=10)  # </
        ax3.set_xlabel("x (pixel)")  # </
        ax3.set_ylabel("Int. (counts)")  # </
        self.figure3.tight_layout()  # </
        self.canvas3.draw()  # </
        # output        
        print("\nImage file: "+self.filelist[self.filendx].split('\\')[-1])
        print("\n%18s %18s %18s %18s %18s %18s" % ("Int_1d(1)","sigInt_1d(1)","Int_1d(2)","sigInt_1d(2)","Int_2d","sigInt_2d"))
        print("%16.4f %16.4f %16.4f %16.4f %16.4f %16.4f" % (self.I1d0, self.sigI1d0, self.I1d1, self.sigI1d1, self.I2d, self.sigI2d))
    
    def OnResetDataROI(self, event):
        try:
            if self.imarray.any():  # </
                ih,iw = self.imarray.shape  # </
                self.sc_dxc.SetRange(0,iw); self.sc_dxc.SetValue(iw/2)  # </
                self.sc_dyc.SetRange(0,ih); self.sc_dyc.SetValue(ih/2)  # </
                self.sc_dxw.SetRange(0,iw); self.sc_dxw.SetValue(iw)  # </
                self.sc_dyw.SetRange(0,ih); self.sc_dyw.SetValue(ih)  # </
                self.RedrawImage(event)  # </
        except AttributeError:  # </
            event.Skip()  # </
           
    def resetRoiRange(self):        
        ih,iw = self.imarray.shape  # </
        self.sc_dxc.SetRange(0,iw)  # </
        self.sc_dyc.SetRange(0,ih)  # </
        self.sc_dxw.SetRange(0,iw)  # </
        self.sc_dyw.SetRange(0,ih)  # </
        self.sc_pxc.SetRange(0,iw)  # </
        self.sc_pyc.SetRange(0,ih)  # </
        self.sc_pxw.SetRange(0,iw)  # </
        self.sc_pyw.SetRange(0,ih)  # </
        self.sc_bxc.SetRange(0,iw)  # </
        self.sc_byc.SetRange(0,ih)  # </
        self.sc_bxw.SetRange(0,iw)  # </
        self.sc_byw.SetRange(0,ih)  # </
            
    def getRoiValues(self):
        dxc=self.sc_dxc.GetValue()  # </
        dyc=self.sc_dyc.GetValue()  # </
        dxw=self.sc_dxw.GetValue()  # </
        dyw=self.sc_dyw.GetValue()  # </
        pxc=self.sc_pxc.GetValue()  # </
        pyc=self.sc_pyc.GetValue()  # </
        pxw=self.sc_pxw.GetValue()  # </
        pyw=self.sc_pyw.GetValue()  # </
        bxc=self.sc_bxc.GetValue()  # </
        byc=self.sc_byc.GetValue()  # </
        bxw=self.sc_bxw.GetValue()  # </
        byw=self.sc_byw.GetValue()  # </
        return (dxc,dyc,dxw,dyw), (pxc,pyc,pxw,pyw), (bxc,byc,bxw,byw)      # </
            
class App(wx.App):
    """Application class"""
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
    
    def OnInit(self):
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self.frame = AreaDetectorAnalysisFrame()
        self.frame.Show()
        self.frame.CreateStatusBar()
        self.SetTopWindow(self.frame)
        self.frame.Bind(wx.EVT_CLOSE, self.OnExitApp)
        print("AreaDetectorAnalysis OnInit:"+time.ctime())        
        return True
    
    def OnExitApp(self, event):
        # print("AreaDetectorAnalysis OnExit:"+time.ctime())
        self.Destroy()
    
if __name__ == '__main__':
    app = App(redirect=False, filename="ADA_log.txt")
    app.MainLoop()
    sys.exit(0)
