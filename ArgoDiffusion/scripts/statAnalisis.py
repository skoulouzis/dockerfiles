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
    
    
def getDataFrame():
    connection = Connection('localhost', 27017)
    db = connection.drip 
    area=[]
    time_coverage=[]
    num_of_params=[]
    execution_time=[]
    num_of_nodes = []
    timestamp_end = []

    docs = db.argoBenchmark.find({});
    #docs = db.argoBenchmark.find({ "num_of_nodes" : 1 })
    #print "area,time_coverage,num_of_params,execution_time,num_of_nodes,timestamp_end"
    for doc in docs:
        area.append(doc["area"])
        time_coverage.append(doc["time_coverage"])
        num_of_params.append(doc["num_of_params"])
        execution_time.append(doc["execution_time"])
        num_of_nodes.append(doc["num_of_nodes"])
        timestamp = datetime.strptime(doc["configuration"]["time_range"]["time_coverage_end"], "%Y-%m-%dT%H:%M:%SZ").strftime("%s")
        timestamp_end.append(timestamp)
        #print "%s,%s,%s,%s,%s,%s" % (doc["area"], doc["time_coverage"], doc["num_of_params"], doc["execution_time"], doc["num_of_nodes"], timestamp)
    
    data = {'area': area, 'time_coverage': time_coverage,'num_of_params':num_of_params,'execution_time':execution_time,'num_of_nodes':num_of_nodes,'timestamp_end':timestamp_end}
    return pandas.DataFrame(data)
    
    
    
dataframe = getDataFrame()
print dataframe.head
grouped = dataframe.groupby(['area', 'time_coverage','num_of_params','num_of_nodes','timestamp_end'], as_index=False)
#print grouped.describe()
#gm = grouped.mean()

#corr = dataframe.corr()
#corr.to_csv("correlation.csv")
##print corr 
##seaborn.heatmap(corr, 
            ##xticklabels=corr.columns.values,
            ##yticklabels=corr.columns.values)
###seaborn.plt.show()

##model = smf.ols(formula='execution_time ~ area + time_coverage + num_of_params', data=gm)
##model = smf.ols(formula='execution_time ~ time_coverage', data=gm)
#model = smf.ols(formula='execution_time ~ area + time_coverage + num_of_params + num_of_nodes + timestamp_end', data=dataframe)
##model = smf.ols(formula='execution_time ~ time_coverage', data=dataframe)
#results = model.fit()

##R-squared: how close the data are to the fitted regression line. Which % of the dependent variable can be explained by the independent. How the variability is exampled by the dependent variable. If you add more DF it gets higher. Look at adj. R-squared to get some meaning on relation 
##Adj. R-squared: Adjusts with the number of "useful" variables 
##Df Residuals: Residuals degrees of freedom 
##Df Model: Degrees of freedom 
##Residuals: Unexplained. Distance from model to regression line. Difference between what model predict and what actually happed  
##F-statistic: The F critical value is what is referred to as the F statistic
##Prob (F-statistic): The p-value
##print(results.summary())

##fig, ax = plt.subplots()
##fig = sm.graphics.plot_fit(results, 2, ax=ax)
##ax.set_ylabel("execution_time")
##ax.set_xlabel("time_coverage Level")
##ax.set_title("Linear Regression")
##plt.show()

