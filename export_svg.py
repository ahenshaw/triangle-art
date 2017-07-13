import numpy

SVG_TEMPLATE = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ev="http://www.w3.org/2001/xml-events"
version="1.1" baseProfile="full"
width="{}mm" height="{}mm">
{}
</svg>'''

def writeSVG(filename, width, height, genome): 
    polys = []
    for triangle in genome:
        points = triangle[:6].reshape(3, 2) * (width, height)
        polygon = []
        for x, y in points:
            polygon.extend([str(int(x)), str(int(y))])
        pts =' '.join(polygon)
        rgb = tuple((triangle[6:9]*255).astype(int))
        alpha = triangle[9]
        poly = '<polygon points="{}" fill="rgb{}" opacity="{:4f}"/>'.format(pts, rgb, alpha)
        polys.append(poly)
    polys = '\n'.join(polys)
    open(filename, 'w').write(SVG_TEMPLATE.format(width, height, polys))

