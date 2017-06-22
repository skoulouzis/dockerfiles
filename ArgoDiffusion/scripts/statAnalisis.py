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

date_format = "%Y-%m-%dT%H:%M:%SZ"

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



def get_deadlines():
    connection = Connection('localhost', 27017)
    db = connection.drip    
    
    #exec_start = datetime.strptime("2017-06-19T21:14:53Z", date_format)
    #exec_end = datetime.strptime("2017-06-19T21:35:43Z", date_format)

    
    square = db.argo_deadline.find({
        #"execution_date":{ "$lte":exec_end }  ,
        #"execution_date":{ "$gte":exec_start }       
    
        })
    
    print "time_to_deadline,execution_rank,area,execution_date,time_coverage,deadline_date,num_of_params,threshold,nodes_started"
    for doc in square:        
        print "%s,%s,%s,%s,%s,%s,%s,%s,%s" % (doc["time_to_deadline"],
                                     doc['execution_rank'],
                                     doc['area'],
                                     doc["execution_date"],
                                     doc['time_coverage'],
                                     doc["deadline_date"],
                                     doc["num_of_params"],
                                     doc["threshold"],
                                     doc['nodes_started'])
    



def get_area(bounding_box,area,max_distinct_num_of_params,max_distinct_time_coverage):
    connection = Connection('localhost', 27017)
    db = connection.drip
    execution_time=[]
    num_of_nodes = []
    
   
    #exec_start = datetime.strptime("2017-06-18T23:40:00Z", date_format)
    #exec_end = datetime.strptime("2017-06-18T00:00:00Z", date_format)

    
    square = db.argoBenchmark.find({
        #"configuration.bounding_box.geospatial_lon_max":{ "$lte":bounding_box['geospatial_lon_max']},
        #"configuration.bounding_box.geospatial_lon_min":{ "$gte":bounding_box['geospatial_lon_min']},
        #"configuration.bounding_box.geospatial_lat_min":{ "$gte":bounding_box['geospatial_lat_min']},
        #"configuration.bounding_box.geospatial_lat_max":{ "$lte":bounding_box['geospatial_lat_max']},
        #"area":{ "$eq":area},
        #"num_of_params":{ "$eq": max_distinct_num_of_params},
        #"time_coverage":{ "$eq":max_distinct_time_coverage},
        #"num_of_nodes":{ "$eq":1},
        #"execution_date":{ "$lte":exec_end }  ,
        #"execution_date":{ "$gte":exec_start }       
    
        })
    
    print "num_of_nodes,execution_time,time_coverage,area,num_of_params,time_coverage_start,time_coverage_end,execution_date"
    for doc in square:
        execution_time.append(doc["execution_time"])
        num_of_nodes.append(doc["num_of_nodes"])
        time_key='time_coverage'
        if 'time_coverage' in doc:
            time_key = 'time_coverage'
        elif 'time_range' in doc:
            time_key = 'time_range'
        num_of_params_key = 'num_of_params'
        if 'parameters' in doc:
            num_of_params_key = 'parameters'
        elif 'num_of_params' in doc:
            num_of_params_key = 'num_of_params'
        
        print "%s,%s,%s,%s,%s,%s,%s,%s" % (doc["num_of_nodes"],
                                     doc["execution_time"],
                                     doc[time_key],
                                     doc["area"],
                                     doc[num_of_params_key],
                                     doc["configuration"]["time_range"]["time_coverage_start"],
                                     doc["configuration"]["time_range"]["time_coverage_end"],
                                     doc["execution_date"])
    
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
    timestamp_array_end = []
    timestamp_array_start = []
                                         

    date = datetime.strptime("2017-06-16T00:00:00Z", date_format) # Before that date we where making a lot of mistakes in measurments 
    #docs = db.argoBenchmark.find({});
    docs = db.argoBenchmark.find({ "num_of_nodes":{ "$eq":1},
                                   "execution_date":{ "$gte":date }  
        
        })
    
   
    print "num_of_nodes,execution_time,time_coverage,area,num_of_params,time_coverage_start,time_coverage_end,timestamp_end,execution_date"
    for doc in docs:
        time_key='time_coverage'
        if 'time_coverage' in doc:
            time_key = 'time_coverage'
        elif 'time_range' in doc:
            time_key = 'time_range'    
        num_of_params_key = 'num_of_params'
        if 'parameters' in doc:
            num_of_params_key = 'parameters'
        elif 'num_of_params' in doc:
            num_of_params_key = 'num_of_params'            
        area.append(doc["area"])
        time_coverage.append(doc[time_key])
        num_of_params.append(doc[num_of_params_key])
        execution_time.append(doc["execution_time"])
        num_of_nodes.append(doc["num_of_nodes"])
        timestamp_end = (doc["configuration"]["time_range"]["time_coverage_end"]-datetime(1970,1,1)).total_seconds()
        timestamp_array_end.append(int(timestamp_end))
        timestamp_start = doc["configuration"]["time_range"]["time_coverage_start"].strftime("%s")
        timestamp_array_start.append(int(timestamp_start))
        
        print "%s,%s,%s,%s,%s,%s,%s,%s,%s" % (doc["num_of_nodes"],
                                     doc["execution_time"],
                                     doc[time_key],
                                     doc["area"],
                                     doc[num_of_params_key],
                                     doc["configuration"]["time_range"]["time_coverage_start"],
                                     doc["configuration"]["time_range"]["time_coverage_end"],
                                     timestamp_end,
                                     doc["execution_date"])
    
    print len(execution_time)
    data = {'area': area, 'time_coverage': time_coverage,'num_of_params':num_of_params,'execution_time':execution_time,'num_of_nodes':num_of_nodes,'timestamp_end':timestamp_end,'timestamp_start':timestamp_start}   
    #data = {'area': area, 'time_coverage': time_coverage,'num_of_params':num_of_params,'time_coverage_end':timestamp_array_end,'execution_time':execution_time}       
    #return pandas.DataFrame(data)
    
    

distinct_area = get_distinct_area(med_box)
#max_distinct_area = max(distinct_area)
max_distinct_area = 122423334.10417336
distinct_num_of_params = getDistinct_num_of_params(med_box)
#max_distinct_num_of_params = max(distinct_num_of_params)
max_distinct_num_of_params = 412
distinct_time_coverage = getDistinct_time_coverage(med_box)
#max_distinct_time_coverage = max(distinct_time_coverage)
max_distinct_time_coverage = 252460800

med = get_area(med_box,max_distinct_area,max_distinct_num_of_params,max_distinct_time_coverage)
#grouped = med.groupby(['num_of_nodes'], as_index=False)
#gm = grouped.mean()
#gm.to_csv("speed_up.csv")
#print gm


#dataframe = getDataFrame()
#grouped = dataframe.groupby(['area', 'time_coverage','time_coverage_end','num_of_params'], as_index=False)
#print grouped.describe()
#gm = grouped.mean()
#print gm

#corr = dataframe.corr()
#corr.to_csv("correlation.csv")
#print corr
#seaborn.heatmap(corr, 
            #xticklabels=corr.columns.values,
            #yticklabels=corr.columns.values)
##seaborn.plt.show()

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


#get_deadlines()

