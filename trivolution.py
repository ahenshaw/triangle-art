# standard library
import random

# third-party libraries
import wx
import wx.adv
import numpy as np
from wx.lib.pubsub import pub
import ObjectListView

# custom modules
import database
from version         import VERSION, APP_NAME, FANCY_APP_NAME
from image_panel     import ImagePanel
from phenotype_panel import PhenotypePanel
from control_panel   import ControlPanel
from open_db_dlg     import OpenInfoDialog

DATABASE_FN = 'data/results.db'


class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.reference = ImagePanel(self, None)
        self.triangles = PhenotypePanel(self, None)
        self.control   = ControlPanel(self)
        self.SetBackgroundColour(wx.WHITE)
        self.doLayout()
        
    def doLayout(self):
        images = wx.BoxSizer(wx.HORIZONTAL)
        images.Add(self.reference, 1, flag=wx.EXPAND|wx.ALL, border=5)
        images.Add(self.triangles, 1, flag=wx.EXPAND|wx.ALL, border=5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(images, 1, flag=wx.EXPAND)
        sizer.Add(self.control, 0, flag=wx.EXPAND|wx.ALL, border=5)
        self.SetSizer(sizer)
    
class MainFrame(wx.Frame):
    def __init__(self, **kwargs):
        wx.Frame.__init__(self, None, **kwargs)
        self.db = database.Database(DATABASE_FN)
        self.main = MainPanel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.main, 1, flag=wx.EXPAND)
        self.SetSizer(sizer)
        
        self.doMenu()
        
    def doMenu(self):
        menubar = wx.MenuBar()

        # File Menu
        file_menu = wx.Menu()
                
        #~ mi_new = file_menu.Append(-1, "&New...")
        #~ self.Bind(wx.EVT_MENU, self.onNew, mi_new)

        mi_open = file_menu.Append(-1, "&Open...")
        self.Bind(wx.EVT_MENU, self.onOpen, mi_open)

        file_menu.AppendSeparator()

        mi_export_svg = file_menu.Append(-1, "Export As SVG...")
        self.Bind(wx.EVT_MENU, self.onExportAsSVG, mi_export_svg)

        mi_export_img = file_menu.Append(-1, "Export As PNG...")
        self.Bind(wx.EVT_MENU, self.onExportAsPNG, mi_export_img)
        
        file_menu.AppendSeparator()
        mi_exit = file_menu.Append(-1, "E&xit")
        self.Bind(wx.EVT_MENU, self.onExit, mi_exit)

        menubar.Append(file_menu, "&File")
        
        # Help Menu
        help_menu = wx.Menu()
        
        mi_about = help_menu.Append(-1, '&About %s' % APP_NAME)
        self.Bind(wx.EVT_MENU, self.onAbout, mi_about)
        
        menubar.Append(help_menu, '&Help')

        self.SetMenuBar(menubar)
                       
    def onOpen(self, event):
        info = self.db.readAllInfo()
        dlg = OpenInfoDialog(info)
        if dlg.ShowModal() == wx.ID_OK:
            info = dlg.lb.GetSelectedObject()
            reference_image = wx.Image(info['width'], info['height'], info['reference'])
            pub.sendMessage('Info', db=self.db, info=info)
            pub.sendMessage('Image', image=reference_image)
        dlg.Destroy()
       
    def onNew(self, event):
        pass
        
    def onExportAsSVG(self, event):
        save_dlg = wx.FileDialog(self, 'Save as SVG', '', '',
                                 'SVG files (*.svg)|*.svg', 
                                 wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if save_dlg.ShowModal() == wx.ID_CANCEL:
            return

        pub.sendMessage('SVG', save_dlg.GetPath())
        
    def onExportAsPNG(self, event):
        save_dlg = wx.FileDialog(self, 'Save as PNG', '', '',
                                 'PNG files (*.png)|*.png', 
                                 wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if save_dlg.ShowModal() == wx.ID_CANCEL:
            return

        pub.sendMessage('PNG', filename)
        
    def onExit(self, event):
        self.Close()

    def onAbout(self, evt):
        info = wx.adv.AboutDialogInfo()
        info.SetName(FANCY_APP_NAME)
        info.SetVersion(VERSION)
        info.SetDescription('')
        info.SetDevelopers(['Andrew Henshaw\nandrew@henshaw.us'])
        info.SetCopyright('2017')
        
        wx.adv.AboutBox(info)        
        

def main():
    app = wx.App(redirect=False)
    frame = MainFrame(title=FANCY_APP_NAME, size=(1024, 600))
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    main()