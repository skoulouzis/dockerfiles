#!/usr/bin/python

import pymongo
from pymongo import Connection
import numpy
from string import letters

import pandas
import seaborn
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from random import randint
from datetime import datetime
import json

med_box = {'geospatial_lon_min': -6,'geospatial_lon_max':37,
       'geospatial_lat_min':30,'geospatial_lat_max':46}

def plotData(corr):
    seaborn.set(style="white")

    # Generate a mask for the upper triangle
    mask = numpy.zeros_like(corr, dtype=numpy.bool)
    mask[numpy.triu_indices_from(mask)] = True

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = seaborn.diverging_palette(220, 10, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    seaborn.heatmap(corr, mask=mask, cmap=cmap, vmax=.3,
                square=True, xticklabels=5, yticklabels=5,
                linewidths=.5, cbar_kws={"shrink": .5}, ax=ax)
    
    #seaborn.savefig("output.png")
    seaborn.plt.show()
    

def get_distinct_area(bounding_box):
    connection = Connection('localhost', 27017)
    db = connection.drip    
    distinct_area = db.argoBenchmark.find({
    "configuration.bounding_box.geospatial_lon_max":{ "$lte":bounding_box['geospatial_lon_max']},
    "configuration.bounding_box.geospatial_lon_min":{ "$gte":bounding_box['geospatial_lon_min']},
    "configuration.bounding_box.geospatial_lat_min":{ "$gte":bounding_box['geospatial_lat_min']},
    "configuration.bounding_box.geospatial_lat_max":{ "$lte":bounding_box['geospatial_lat_max']}
    }).distinct("area")  
    
    return distinct_area

def getDistinct_num_of_params(bounding_box):
    connection = Connection('localhost', 27017)
    db = connection.drip    
    distinct_num_of_params = db.argoBenchmark.find({
    "configuration.bounding_box.geospatial_lon_max":{ "$lte":bounding_box['geospatial_lon_max']},
    "configuration.bounding_box.geospatial_lon_min":{ "$gte":bounding_box['geospatial_lon_min']},
    "configuration.bounding_box.geospatial_lat_min":{ "$gte":bounding_box['geospatial_lat_min']},
    "configuration.bounding_box.geospatial_lat_max":{ "$lte":bounding_box['geospatial_lat_max']}
    }).distinct("num_of_params")  
    
    return distinct_num_of_params

def getDistinct_time_coverage(bounding_box):
    connection = Connection('localhost', 27017)
    db = connection.drip    
    distinct_time_coverage = db.argoBenchmark.find({
    "configuration.bounding_box.geospatial_lon_max":{ "$lte":bounding_box['geospatial_lon_max']},
    "configuration.bounding_box.geospatial_lon_min":{ "$gte":bounding_box['geospatial_lon_min']},
    "configuration.bounding_box.geospatial_lat_min":{ "$gte":bounding_box['geospatial_lat_min']},
    "configuration.bounding_box.geospatial_lat_max":{ "$lte":bounding_box['geospatial_lat_max']}
    }).distinct("time_coverage")  
    
    return distinct_time_coverage
    

def get_area(bounding_box,area,max_distinct_num_of_params,max_distinct_time_coverage):
    connection = Connection('localhost', 27017)
    db = connection.drip
    execution_time=[]
    num_of_nodes = []
    
    square = db.argoBenchmark.find({
        "configuration.bounding_box.geospatial_lon_max":{ "$lte":bounding_box['geospatial_lon_max']},
        "configuration.bounding_box.geospatial_lon_min":{ "$gte":bounding_box['geospatial_lon_min']},
        "configuration.bounding_box.geospatial_lat_min":{ "$gte":bounding_box['geospatial_lat_min']},
        "configuration.bounding_box.geospatial_lat_max":{ "$lte":bounding_box['geospatial_lat_max']},
        "area":{ "$eq":area},
        "num_of_params":{ "$eq": max_distinct_num_of_params},
        "time_coverage":{ "$eq":max_distinct_time_coverage}
        })
    
    for doc in square:
        execution_time.append(doc["execution_time"])
        num_of_nodes.append(doc["num_of_nodes"])
        #print "%s , %s , %s , %s" % (doc["_id"],doc["num_of_nodes"],doc["execution_time"],doc["time_coverage"])
    
    data = {'execution_time':execution_time,'num_of_nodes':num_of_nodes}
    return pandas.DataFrame(data)
    
def getDataFrame():
    connection = Connection('localhost', 27017)
    db = connection.drip 
    area=[]
    time_coverage=[]
    num_of_params=[]
    execution_time=[]
    num_of_nodes = []
    timestamp_end = []
    timestamp_start = []
                                         

    
    #docs = db.argoBenchmark.find({});
    docs = db.argoBenchmark.find({ "num_of_nodes" : 1 })
    #print "area,time_coverage,num_of_params,execution_time,num_of_nodes,timestamp_end"
    for doc in docs:
        area.append(doc["area"])
        time_coverage.append(doc["time_coverage"])
        num_of_params.append(doc["num_of_params"])
        execution_time.append(doc["execution_time"])
        num_of_nodes.append(doc["num_of_nodes"])
        timestamp = datetime.strptime(doc["configuration"]["time_range"]["time_coverage_end"], "%Y-%m-%dT%H:%M:%SZ").strftime("%s")
        timestamp_end.append(int(timestamp))
        
        timestamp = datetime.strptime(doc["configuration"]["time_range"]["time_coverage_start"], "%Y-%m-%dT%H:%M:%SZ").strftime("%s")
        timestamp_start.append(int(timestamp))        
        #print "%s,%s,%s,%s,%s,%s" % (doc["area"], doc["time_coverage"], doc["num_of_params"], doc["execution_time"], doc["num_of_nodes"], timestamp)
    
    #data = {'area': area, 'time_coverage': time_coverage,'num_of_params':num_of_params,'execution_time':execution_time,'num_of_nodes':num_of_nodes,'timestamp_end':timestamp_end,'timestamp_start':timestamp_start}   
    data = {'area': area, 'time_coverage': time_coverage,'num_of_params':num_of_params,'execution_time':execution_time}       
    return pandas.DataFrame(data)
    
    

distinct_area = get_distinct_area(med_box)
max_distinct_area = max(distinct_area)
distinct_num_of_params = getDistinct_num_of_params(med_box)
max_distinct_num_of_params = max(distinct_num_of_params)
distinct_time_coverage = getDistinct_time_coverage(med_box)
max_distinct_time_coverage = max(distinct_time_coverage)
med = get_area(med_box,max_distinct_area,max_distinct_num_of_params,max_distinct_time_coverage)
grouped = med.groupby(['num_of_nodes'], as_index=False)
gm = grouped.mean()
gm.to_csv("speed_up.csv")
print gm

#for area in distinct_area:
    #for params in distinct_num_of_params:
        #for time_coverage in distinct_time_coverage:
            ##print "area: %s params: %s time_coverage:%s" %(area,params,time_coverage) 
            #med = get_area(med_box,area,params,time_coverage)
            #grouped = med.groupby(['num_of_nodes'], as_index=False)
            #gm = grouped.mean()
            #gm.to_csv("speed_up.csv")











    



#dataframe = getDataFrame()
#grouped = dataframe.groupby(['area', 'time_coverage','num_of_params'], as_index=False)
#print grouped.describe()
#gm = grouped.mean()
#print gm

#corr = gm.corr()
#corr.to_csv("correlation.csv")
##seaborn.heatmap(corr, 
            ##xticklabels=corr.columns.values,
            ##yticklabels=corr.columns.values)
###seaborn.plt.show()

#model = smf.ols(formula='execution_time ~ area + time_coverage + num_of_params', data=gm)
#model = smf.ols(formula='execution_time ~ time_coverage', data=gm)
#model = smf.ols(formula='execution_time ~ area + time_coverage + num_of_params + num_of_nodes + timestamp_end', data=dataframe)
#model = smf.ols(formula='execution_time ~ time_coverage', data=dataframe)
#results = model.fit()

#R-squared: how close the data are to the fitted regression line. Which % of the dependent variable can be explained by the independent. How the variability is exampled by the dependent variable. If you add more DF it gets higher. Look at adj. R-squared to get some meaning on relation 
#Adj. R-squared: Adjusts with the number of "useful" variables 
#Df Residuals: Residuals degrees of freedom 
#Df Model: Degrees of freedom 
#Residuals: Unexplained. Distance from model to regression line. Difference between what model predict and what actually happed  
#F-statistic: The F critical value is what is referred to as the F statistic
#Prob (F-statistic): The p-value
#print(results.summary())

##fig, ax = plt.subplots()
##fig = sm.graphics.plot_fit(results, 2, ax=ax)
##ax.set_ylabel("execution_time")
##ax.set_xlabel("time_coverage Level")
##ax.set_title("Linear Regression")
##plt.show()

