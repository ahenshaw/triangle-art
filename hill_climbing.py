
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from random import randint

N = 1

# Make function data.
X = np.linspace(0, 1, 200)
Y = np.linspace(0, 1, 200)
X, Y = np.meshgrid(X, Y)

Z = (100*X*Y*(1-X)*(1-Y)*np.sin(N*np.pi*X)*np.sin(N*np.pi*Y))**2


class HillClimbingData:
    def __init__(self, axes):
        '''Compute the entire hill-climbing path.'''
        data = []
        u = len(X)//2
        v = 0 
        peak = 0
        EXTRA_ATTEMPTS = 50
        attempts = EXTRA_ATTEMPTS
        while attempts:
            # randomly look at neighboring cells
            ut = u + randint(-1, 1)
            vt = v + randint(-1, 1)
            ut = max(0, min(ut, len(X)-1))
            vt = max(0, min(vt, len(Y)-1))
            value =  Z[ut, vt]
            if value > peak:
                # replace the best, if this is better
                peak = value
                u, v = ut, vt
                # if we've found a better solution, reset the attempts counter
                attempts = EXTRA_ATTEMPTS
            else:
                # plot a failed attempt (but use a different color)
                data.append([[X[ut,ut]], [Y[vt,vt]], [value], [0]])
            data.append([[X[u,u]], [Y[v,v]], [peak], [1]])
            attempts -= 1
        # keep the data to for later playback (in the update function)
        self.data = np.array(data)
        
        # create a list with a single point
        self.points = [ax.plot(self.data[0, 0], self.data[0, 1], self.data[0, 2], 'o', markersize=10, color='r')[0]]

    def __len__(self):
        return len(self.data)
        
    def update(self, num):
        '''Select the next point in the path to plot in the animation.'''
        xyz = self.data[num]
        point = self.points[0]
        point.set_data([xyz[0]], [xyz[1]])
        point.set_3d_properties([xyz[2]])
        color = ['#FF0000', '#00FF00', '#FFFFFF'][int(xyz[3][0])]
        point.set_markerfacecolor(color)
        point.set_markeredgecolor(color)
        return self.points

# prepare the plot figure
fig = plt.figure(figsize=(10, 10),)

# reduce the margins
plt.subplots_adjust(left=0, right=1, top=1, bottom=0.0)
ax = fig.gca(projection='3d')

# Plot the surface.
ax.plot_surface(X, Y, Z, linewidth=2, antialiased=False)
dataset = HillClimbingData(ax)
ani = animation.FuncAnimation(fig, dataset.update, len(dataset), interval=30, blit=True)

plt.show()

