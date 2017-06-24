import wx

class ImagePanel(wx.Panel):
    def __init__(self, parent, image=None):
        wx.Panel.__init__(self, parent, -1)
        self.SetBackgroundColour(wx.WHITE)
        self.SetImage(image)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        
    def SetImage(self, image):
        self.image  = image
        self.scaled = None
        self.OnSize(None)
        
    def OnEraseBackground(self, event):
        pass
        
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
        if not self.scaled:
            return
        dc.DrawBitmap(self.scaled, 0, 0)       

