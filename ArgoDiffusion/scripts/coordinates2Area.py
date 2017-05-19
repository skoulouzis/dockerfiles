#!/usr/bin/python

#Code from http://stackoverflow.com/questions/13148037/calculating-area-from-lat-lon-polygons-in-python

import sys
from pyproj import Proj
from shapely.geometry import shape
import math
import pyproj    
import shapely
import shapely.ops as ops
from shapely.geometry.polygon import Polygon
from functools import partial

coords = []
args = sys.argv


for i in range(len(args)-1):
    coords.append( float(args[i+1]) )



lat_min=float(coords[0])
lat_max=float(coords[1])
lon_min=float(coords[2])
lon_max=float(coords[3])

    
co = {"type": "Polygon", "coordinates": [
    [(lon_min, lat_max),
     (lon_min, lat_min),
     (lon_max, lat_min),
     (lon_max, lat_max)]]}    
    
lon, lat = zip(*co['coordinates'][0])
from pyproj import Proj
pa = Proj("+proj=cea +lon_0=0 +lat_ts=45 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs")


x, y = pa(lon, lat)
cop = {"type": "Polygon", "coordinates": [zip(x, y)]}
from shapely.geometry import shape
print shape(cop).area


