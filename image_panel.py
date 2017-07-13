import wx
from wx.lib.pubsub import pub
import numpy as np

class ImagePanel(wx.Panel):
    def __init__(self, parent, image=None):
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_SIMPLE)
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.SetImage(image)
        self.hide = False

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_LEFT_DOWN, self.onClick)

        pub.subscribe(self.SetImage, 'Image')
        pub.subscribe(self.onHide, 'Hide Image')
        
    def SetImage(self, image):
        self.image  = image
        self.scaled = None
        self.OnSize(None)
        
    def OnEraseBackground(self, event):
        pass

    def onHide(self):
        self.hide = True
        
    def onClick(self, event):
        self.hide = not self.hide
        self.Refresh()
        event.Skip()
        
    def OnSize(self, event):
        if not self.image:
            return
        w, h = self.GetClientSize()

        width = self.image.GetWidth()
        height = self.image.GetHeight()
        sx = float(w)/width
        sy = float(h)/height
        scale = min(sx, sy)
        
        self.scaled = wx.Bitmap(self.image.Scale(scale*width, scale*height, wx.IMAGE_QUALITY_HIGH))
        self.Refresh(True)
        self.Update()
        
    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        if not self.hide:
            if not self.scaled:
                return
            dc.DrawBitmap(self.scaled, 0, 0)       
        else:
            text = 'Image Hidden'
            cw, ch = dc.GetTextExtent(text)
            w, h = self.GetClientSize()
            dc.DrawText(text, (w-cw)//2, (h-ch)//2)
            

