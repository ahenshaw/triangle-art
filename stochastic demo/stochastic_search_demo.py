import sys
import random
import time

import wx
from wx.lib.pubsub import pub

import numpy as np
from numpy import cos, sin, radians, pi


from OpenGL.GL   import *
from OpenGL.GLUT import *
from OpenGL.GLU  import *

import stochastic_search_GA as GA

from canvasbase import CanvasBase
APP_NAME = 'Python Atlanta Meetup - Stochastic Search'

N = 1
def f(x, y):
    return ((10*x*y*(1-x)*(1-y)*sin(N*pi*x)*sin(N*pi*y))**2.0)

def ga_f(individual):
    return (f(*individual),)
    
class MainCanvas(CanvasBase):
    def InitGL(self):
        # set viewing projection
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, 1.5, 0.1, 10.0)

        # position viewer
        glMatrixMode(GL_MODELVIEW)
        glTranslatef(0.0, 0.0, -3.0)

        # position objects
        glRotatef(self.y, 1.0, 0.0, 0.0)
        glRotatef(self.x, 0.0, 0.50, 0.0)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND);
        glEnable(GL_LINE_SMOOTH)
        glShadeModel(GL_SMOOTH)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        self.InitGenLists()
        
        # setup search
        self.ga_results = []
        self.markers = []
        self.timer = wx.Timer()
        self.timer.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(100)

        self.search_method  = None
        pub.subscribe(self.OnSingle, 'Single')
        pub.subscribe(self.OnMulti, 'Multi')

        pub.subscribe(self.OnRandomWalk, 'Random Walk')
        pub.subscribe(self.OnHillClimbing, 'Hill Climbing')
        pub.subscribe(self.OnGA, 'Genetic\nAlgorithm')
    
    def OnSingle(self, pop_size):
        global N
        N = 1
        self.InitGenLists()
        self.ga_results = []
        self.markers = []

    def OnMulti(self, pop_size):
        global N
        N = 3
        self.InitGenLists()
        self.ga_results = []
        self.markers = []
        
    def OnRandomWalk(self, pop_size):
        self.search_method = self.RandomWalk
        self.markers = [(random.random(), random.random()) for i in range(pop_size)]

    def OnHillClimbing(self, pop_size):
        self.search_method = self.HillClimbing
        self.markers = [(random.random(), random.random()) for i in range(pop_size)]

    def OnGA(self, pop_size):
        wait = wx.BusyCursor()
        self.ga_results = GA.run(ga_f, pop_size)
        self.search_method = self.GA
        self.markers = []
        
    def HillClimbing(self):
        markers = []
        for x, y in self.markers:
            x_new = x + (random.random()-0.5)/30
            y_new = y + (random.random()-0.5)/30
            x_new = max(min(x_new, 1), 0)
            y_new = max(min(y_new, 1), 0)
            if f(x_new, y_new) > f(x, y):
                markers.append((x_new, y_new))
                pub.sendMessage('Best',x=x,y=y,z=f(x,y))
            else:
                markers.append((x, y))
        self.markers = markers

    def RandomWalk(self):
        markers = []
        for x, y in self.markers:
            x += (random.random()-0.5)/30
            y += (random.random()-0.5)/30
            x = max(min(x, 1), 0)
            y = max(min(y, 1), 0)
            pub.sendMessage('Best',x=x,y=y,z=f(x,y))
            markers.append((x, y))
        self.markers = markers
        
    def GA(self):
        z = -1e200
        if self.ga_results:
            self.markers = self.ga_results.pop(0)
            for x,y in self.markers:
                if f(x,y) > z:
                    z = f(x,y)
                    pub.sendMessage('Best',x=x,y=y,z=z)
                    
        self.Refresh()
        
    def OnTimer(self, event):
        if self.search_method is not None:
            self.search_method()
        self.Refresh()
        
    def InitGenLists(self):
        self.surface = glGenLists(1)
        self.marker = glGenLists(1)
        
        X = np.linspace(0, 1, 101)
        Z = np.linspace(0, 1, 101)
        # pre-draw the function surface
        glNewList(self.surface, GL_COMPILE)
        glBegin(GL_QUADS)
        for i in range(len(X)-1):
            x0 = X[i]
            x1 = X[i+1]
            for j in range(len(Z)-1):
                z0 = Z[j]
                z1 = Z[j+1]
                glColor4f(1.5*f(x0,z0)+0.2, 0.2, 3*f(x0,z0)+0.2, 1.0);
                glVertex3f(x0, f(x0, z0), z0)
                glVertex3f(x0, f(x0, z1), z1)
                glVertex3f(x1, f(x1, z1), z1)
                glVertex3f(x1, f(x1, z0), z0)
        glEnd()
        
        # draw the mesh
        glColor4f(0.1, 0.1, 0.4, 1);
        glLineWidth(1)
        glBegin(GL_LINES)
        off = 0.001
        for i in range(len(X)-1):
            x0 = X[i]
            x1 = X[i+1]
            for j in range(len(Z)-1):
                z0 = Z[j]
                z1 = Z[j+1]
                
                glVertex3f(x0, f(x0, z0)+off, z0)
                glVertex3f(x0, f(x0, z1)+off, z1)
                
                glVertex3f(x1, f(x1, z1)+off, z1)
                glVertex3f(x1, f(x1, z0)+off, z0)
                
                glVertex3f(x0, f(x0, z0)+off, z0)
                glVertex3f(x1, f(x1, z0)+off, z0)
        glEnd()
        glEndList()

        # pre-draw a marker
        glNewList(self.marker, GL_COMPILE)
        glColor4f(1, 0.7, 0.1, 1);
        glPushMatrix()
        glRotate(-90, 1, 0, 0)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluCylinder(quadric, 0.0, 0.002, .02, 16, 16);
        glTranslate(0, 0, .02)
        gluSphere(quadric, 0.005, 50, 50)
        gluDeleteQuadric(quadric)
        glPopMatrix()
        glEndList()

    def OnDraw(self):
        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        w, h = self.GetClientSize()
        w = max(w, 1.0)
        # rotate to reflect mouse drag
        glRotatef((self.x - self.lastx) * (180.0 / w), 0.0, 1.0, 0.0);
        
        # draw the objects
        glPushMatrix()
        glScale(2, 2, 2)
        glTranslatef(-0.5, 0.0, -0.5)

        glCallList(self.surface)
        self.DrawMarkers()
        glPopMatrix()
        self.SwapBuffers()
        
    def DrawMarkers(self):
        for x, y in self.markers:
            glPushMatrix()
            glTranslate(x, f(x, y), y)
            #~ glScale(0.01, 0.01*self.aspect, 0.01)
            glCallList(self.marker)
            glPopMatrix()


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, size=(1280, 1024), title=APP_NAME)
        
        self.Reset()
        self.panel = MainCanvas(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel, 1, flag=wx.EXPAND)
        self.SetSizer(sizer)
        self.InitToolBar()
        self.Show(True)
        pub.subscribe(self.OnSetBest, 'Best')
        
    def InitToolBar(self):
        self.toolbar = tb = self.CreateToolBar()
        dpi_x, dpi_y = wx.ScreenDC().GetPPI()
        size = int(dpi_y/2)
        tb.SetToolBitmapSize((size, size))
        
        tb.AddControl(wx.StaticText(tb, -1, ' Function: '))
        tb.AddControl(wx.Button(tb, -1, 'Single', size=(-1, size)))
        tb.AddControl(wx.Button(tb, -1, 'Multi', size=(-1, size)))
        
        tb.AddControl(wx.StaticText(tb, -1, '    Search Method: '))
        tb.AddControl(wx.Button(tb, -1, 'Random Walk', size=(-1, size)))
        tb.AddControl(wx.Button(tb, -1, 'Hill Climbing', size=(-1, size)))
        tb.AddControl(wx.Button(tb, -1, 'Genetic\nAlgorithm', size=(-1, size)))
        tb.AddControl(wx.StaticText(tb, -1, '    # Searchers: '))
        self.slider = wx.Slider(tb, -1, value=6, minValue=1, maxValue=30, style=wx.SL_VALUE_LABEL)
        tb.AddControl(self.slider)
        tb.AddStretchableSpace()
        
        self.best = wx.StaticText(tb, -1, '')
        self.OnSetBest(0, 0, 0.0001)
        tb.AddControl(self.best)
        
        tb.Realize()
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        
    def OnButton(self, event):
        # generate event based on button label
        self.Reset()
        pop_size = self.slider.GetValue()
        pub.sendMessage(event.GetEventObject().GetLabel(), pop_size=pop_size)
        
    def Reset(self):
        self.best_z = 0.0
        
    def OnSetBest(self, x, y, z):
        if z > self.best_z:
            self.best_z = z
            self.best.SetLabel('x: {:0.3f} | y: {:0.3f}  | z: {:0.3f}'.format(x,y,z))
            
    def OnRandom(self, event):
        pass
        
        
        

app = wx.App(redirect=False)
frame = MainFrame()
app.SetTopWindow(frame)
frame.Show()
app.MainLoop()
