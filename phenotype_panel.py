import wx
from wx.lib.pubsub import pub

class PhenotypePanel(wx.Panel):
    def __init__(self, parent, image=None):
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_SIMPLE)
        self.SetBackgroundColour(wx.LIGHT_GREY)
        
        self.genome     = None
        self.image_size = None

        pub.subscribe(self.SetGenome, 'Genome')
        pub.subscribe(self.SetImage, 'Image')

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        
    def SetImage(self, image):
        self.SetSize(*image.GetSize())
        
    def SetSize(self, width, height):
        self.image_size = (width, height)
        self.OnSize(None)
        
    def SetGenome(self, genome):
        # interpret the genome as triangle vertices and colors
        self.genome = genome.copy()
        self.Refresh()

    def OnEraseBackground(self, event):
        pass
        
    def OnSize(self, event):
        if self.image_size:
            w, h          = self.GetClientSize()
            width, height = self.image_size
            self.scale    = min(w/width, h/height)
            
            self.Refresh(True)
            self.Update()
        
    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        if self.genome is None:
            return
        w, h = self.image_size
        points = self.genome[:, 0:6].copy().reshape(-1,3,2)
        points[:,:] *= self.image_size
        points[:,:] *= self.scale
        brushes = [wx.Brush(wx.Colour(r,g,b,a)) for (r,g,b,a) in self.genome[:,6:]*255]

        dc.Clear()
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.SetPen(wx.WHITE_PEN)
        dc.DrawRectangle(0, 0, w*self.scale, h*self.scale)    
        # use the Graphics Device Context to support alpha channel drawing
        gdc = wx.GCDC(dc)
        gdc.SetPen(wx.NullPen)
        gdc.DrawPolygonList(points, brushes=brushes)

