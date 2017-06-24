import wx
import numpy as np

class Arena:
    def __init__(self, reference):
        self.reference = wx.Bitmap(reference)
        # init self.scratch to the same bitmap just to get correct size and bit depth
        self.scratch   = wx.Bitmap(reference)
        
        # create numpy array from the reference bitmap 
        bpp = 4  # bytes per pixel
        buffer_length = self.scratch.Width * self.scratch.Height * bpp
        
        self.ref_array     = np.zeros(buffer_length, dtype=np.byte)
        buffer = memoryview(self.ref_array)
        self.reference.CopyToBuffer(buffer, wx.BitmapBufferFormat_ARGB32)
        
        # promote the reference array to INT64 to support calculations
        self.ref_array = self.ref_array.astype(np.int64)

        # now, also create numpy array for the scratch bitmap 
        self.scratch_array = np.zeros(buffer_length, dtype=np.byte)
        
    def GetLastImage(self):
        return self.scratch.ConvertToImage()
        
    def Render(self, genome):
        w = self.scratch.Width
        h = self.scratch.Height
        points = genome[:, 0:6].copy().reshape(-1,3,2)
        points[:,:] *= (w, h)
        brushes = [wx.Brush(wx.Colour(r,g,b,a)) for (r,g,b,a) in genome[:,6:]*255]

        dc = wx.MemoryDC()
        dc.SelectObject(self.scratch)
        dc.SetBackground(wx.GREY_BRUSH)
        dc.Clear()
        gdc = wx.GCDC(dc)
        gdc.SetPen(wx.NullPen)
        gdc.DrawPolygonList(points, brushes=brushes)
        dc.SelectObject(wx.NullBitmap)
        
    def CalcFitness(self, genome):
        self.Render(genome)
        # use the buffer interface to efficiently convert bitmap to numpy array
        buffer = memoryview(self.scratch_array)
        self.scratch.CopyToBuffer(buffer, wx.BitmapBufferFormat_RGB32)
        return np.sum((self.ref_array - self.scratch_array)**2)
