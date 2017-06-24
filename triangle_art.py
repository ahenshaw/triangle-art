import wx
from wx.lib.pubsub import pub
import numpy as np
import random

from image_panel import ImagePanel
from evolve      import Arena

NUM_TRIANGLES = 100

        
    
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=(1024, 768))
        reference_image = wx.Image('mona_lisa_crop.jpg')
        self.reference = ImagePanel(self, reference_image,)
        self.triangles = ImagePanel(self, None)
        self.best      = None
        self.count     = 0
        self.Layout()
        
        self.genome = np.random.random((NUM_TRIANGLES, 10))
        self.score  = np.Inf
        self.timer  = wx.Timer(self)
        self.timer.Start(100)
        self.arena = Arena(reference_image)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
       
    def Layout(self):
        self.SetBackgroundColour(wx.WHITE)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.reference, 1, flag=wx.EXPAND|wx.ALL, border=10)
        sizer.Add(self.triangles, 1, flag=wx.EXPAND|wx.ALL, border=10)
        self.SetSizer(sizer)
        
    def OnTimer(self, event):
        phenome = None
        for i in range(10):
            self.count += 1
            offspring = self.genome.copy()
            #~ for j in range(3):
            if True:
                gene = random.randint(0, len(offspring)-1)
                chromosome = random.randint(0, 9)
                offspring[gene][chromosome] = random.random()
            result = self.arena.CalcFitness(offspring) 
            if result < self.score:
                #~ print('--', result)
                self.score = result
                self.genome = offspring
                phenome = self.arena.GetLastImage()
        if phenome:
            self.triangles.SetImage(phenome)
            self.triangles.Update()
        if not (self.count % 1000):
            print(self.count)


def main():
    app = wx.App(redirect=False)
    frame = MainFrame()
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
    
if __name__ == '__main__':
    main()