import wx
from wx.lib.pubsub import pub
import numpy as np
import time
import os.path

class ControlPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        
        self.slider = wx.Slider(self, -1, style=wx.SL_AUTOTICKS)
        self.slider.SetTickFreq(100)
        self.auto   = wx.CheckBox(self, -1, 'Auto')
        self.timer  = wx.Timer(self)
        self.db = None

        box1  = wx.BoxSizer(wx.HORIZONTAL)
        box1.Add(self.slider, 1, flag=wx.EXPAND|wx.ALL|wx.ALIGN_CENTRE, border=10)
        box1.Add(self.auto, 0, flag=wx.ALIGN_CENTRE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(box1, 0, flag=wx.EXPAND)
        self.SetSizer(sizer)

        pub.subscribe(self.onInfo, 'Info')
        self.Bind(wx.EVT_SLIDER, self.onSlider)
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.Bind(wx.EVT_CHECKBOX, self.onAuto)
        pub.subscribe(self.onBatch, 'Batch')

        
    def onAuto(self, event):
        if self.auto.IsChecked():
            self.timer.Start(1000)
        else:
            self.timer.Stop()
    
    def onTimer(self, event):
        self.readIndices()
        self.slider.SetValue(len(self.indices)-1)
        self.onSlider(None)
        
    def onInfo(self, db, info):
        self.db = db
        self.info = info
        # worst fitness for RGB bytes (delta is squared)
        # using 128 instead of 255 to represent an average delta
        self.worst = info['width'] * info['height'] * 128 * 128 * 3
        self.info_id = info[0]
        self.readIndices()
        self.slider.SetValue(0)
        self.onSlider(None)
    
    def readIndices(self):
        self.indices = []
        self.generations = []
        data = self.db.readIndices(self.info_id)
        for index, generation in data:
            self.indices.append(index)
            self.generations.append(generation)
        self.slider.SetRange(0, len(self.indices)-1)
        self.slider.SetTickFreq(len(self.indices)//2)
        
    def onSlider(self, event):
        if not self.db:
            return

        index = self.indices[self.slider.GetValue()]
        elapsed, generation, fitness, genome = self.db.readGenome(index)
        genome = np.fromstring(genome).reshape(-1, 10)
        fitness = 100*(1 - fitness / self.worst)

        pub.sendMessage('Genome', genome=genome)
        pub.sendMessage('Stats', elapsed=elapsed, generation=generation, fitness=fitness)
        
    def onBatch(self, folder):
        stop = False
        indices = [int(round(x))-1 for x in np.geomspace(1, len(self.indices))]
        for index in indices:
            self.slider.SetValue(index)
            self.onSlider(None)
            time.sleep(0.1) #hack
            filename = os.path.join(folder, '%s%06d.png' % (self.info['description'], self.generations[index]))
            pub.sendMessage('PNG', filename=filename)

    
    
        
