import numpy as np

def radial(w, h, depth):
    x, y = np.meshgrid(np.linspace(-1,1,w), np.linspace(-1,1,h))
    d = np.sqrt(x*x+y*y)
    sigma, mu = 1.0, 0.0
    g = np.exp(-( (d-mu)**2 / ( 2.0 * sigma**2 ) ) )
    g = g**3
    g = g.reshape(w, h, 1).repeat(depth,2)

    return g
    
    
if __name__ == '__main__':
    print(radial(3,3, 3))

    