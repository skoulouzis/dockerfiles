#!/usr/bin/env python
import sys
import json
import csv
import time
import sys
import os.path
import psutil
import argo_model


lat_vals = []
lon_vals = []
def read_file(argofile):
    try:
        fargofile = open(argofile, 'r')
        csv.register_dialect('in', delimiter=',')
        reader = csv.reader(fargofile, dialect='in')
        rownum = 0
        for row in reader:
            rownum += 1
            #first line, header   
            if (rownum == 1) or (not row [3]):
                #nothing to do
                continue
            # test position
            lat = float(row [3])
            lon = float(row [4])
            lat_vals.append(lat)
            lon_vals.append(lon)
            
                            
    finally:
        fargofile.close()

def get_file_list(input_folder):
    list_files = []
    for ncfile in os.listdir(input_folder):
        if ncfile.endswith(".csv"):
            list_files.append(os.path.join(input_folder, ncfile))
    return list_files
            
            
            
list_files = get_file_list(sys.argv[1])


for argofile in list_files:
    read_file(argofile)
    
min_lat=min(lat_vals)
max_lat= max (lat_vals)
min_lon=min(lon_vals)
max_lon=max(lon_vals)

print "min_lat: %s, max_lat: %s, min_lon: %s, min_lat: %s" %(min_lat,max_lat,min_lon,max_lon)