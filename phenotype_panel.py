import wx
from wx.lib.pubsub import pub
import numpy as np

from export_svg import writeSVG

class PhenotypePanel(wx.Panel):
    def __init__(self, parent, image=None):
        wx.Panel.__init__(self, parent, -1, style=wx.BORDER_SIMPLE)
        self.SetBackgroundColour(wx.LIGHT_GREY)
        
        self.genome     = None
        self.image_size = None
        self.scale      = None

        pub.subscribe(self.setGenome, 'Genome')
        pub.subscribe(self.setImage, 'Image')
        pub.subscribe(self.onSVG, 'SVG')
        pub.subscribe(self.onPNG, 'PNG')

        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)
        
    def setImage(self, image):
        self.image_size = image.GetSize()
        self.onSize(None)
        
    def setGenome(self, genome):
        # interpret the genome as triangle vertices and colors
        self.genome = genome.copy()
        self.Refresh()
        self.Update()

    def onEraseBackground(self, event):
        pass
        
    def onSize(self, event):
        if self.image_size is not None:
            w, h          = self.GetClientSize()
            width, height = self.image_size
            self.scale    = min(w/width, h/height)
            
            self.Refresh(True)
            self.Update()
        
    def onPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        if self.genome is None:
            return
        if self.image_size is None:
            return
        memDC = wx.MemoryDC()
        w, h = self.image_size
        bitmap = wx.Bitmap(w, h)
        memDC.SelectObject(bitmap)
        self.draw(memDC, 1.0)
        memDC.SelectObject(wx.NullBitmap)
        image = bitmap.ConvertToImage()
        image = image.Scale(w*self.scale, h*self.scale, wx.IMAGE_QUALITY_BICUBIC)
        dc.DrawBitmap(image.ConvertToBitmap(), 0, 0)

    def draw(self, dc, scale=1):
        ''' Draw the genome into the provided DC (memoryDC or PaintDC)'''
        if self.image_size is None:
            return
        w, h = self.image_size
        points  = np.floor(self.genome[:, 0:6].reshape(-1,3,2)*self.image_size)
        #~ points  *= scale
        brushes = [wx.Brush(wx.Colour(r,g,b,a)) for (r,g,b,a) in self.genome[:,6:]*255]

        dc.SetBrush(wx.WHITE_BRUSH)
        dc.SetPen(wx.WHITE_PEN)
        #~ dc.DrawRectangle(0, 0, w*scale, h*scale)    
        dc.DrawRectangle(0, 0, w, h)    
        
        # use the Graphics Device Context to support alpha channel drawing
        gdc = wx.GCDC(dc)
        gdc.SetPen(wx.NullPen)
        gdc.DrawPolygonList(points, brushes=brushes)
        
        
    def onSVG(self, filename):
        if self.genome is not None:
            width, height = self.image_size
            writeSVG(filename, width, height, self.genome)
            
    def onPNG(self, filename):
        dc = wx.MemoryDC()
        w, h = self.image_size
        
        # bind a bitmap to the display context
        bitmap = wx.Bitmap(w, h)
        dc.SelectObject(bitmap)
        
        self.draw(dc)
        
        # release the bitmap
        dc.SelectObject(wx.NullBitmap)
        
        image = bitmap.ConvertToImage()
        image.SaveFile(filename, wx.BITMAP_TYPE_PNG)

        
