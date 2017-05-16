#!/usr/bin/python

#Code from http://stackoverflow.com/questions/13148037/calculating-area-from-lat-lon-polygons-in-python

import sys
from pyproj import Proj
from shapely.geometry import shape

def getArea(coords):
    c = {"type": "Polygon",
    "coordinates": [[ (coords[0], coords[2]), (coords[1], coords[2]),
                      (coords[0], coords[3]), (coords[1], coords[3]) ]]}
    lon, lat = zip(*c['coordinates'][0])
    pro = Proj("+proj=aea")
    x, y = pro(lon, lat)
    poly = {"type": "Polygon", "coordinates": [zip(x, y)]}
    return shape(poly).area


coords = []
args = sys.argv


for i in range(len(args)-1):
    coords.append( float(args[i+1]) )
     
    
area =getArea(coords)
print area



#coords[1] = args[2]
#coords[2] = args[3]
#coords[3] = args[4]
     
    
#area =getArea(coords)
#print area