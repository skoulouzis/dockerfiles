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

    docs = db.argoBenchmark.find({});
    print "area,time_coverage,num_of_params,execution_time"
    for doc in docs:
        area.append(doc["area"])
        time_coverage.append(doc["time_coverage"])
        num_of_params.append(doc["num_of_params"])
        execution_time.append(doc["execution_time"])
        print "%s,%s,%s,%s" % (doc["area"], doc["time_coverage"], doc["num_of_params"], doc["execution_time"])
    
    data = {'area': area, 'time_coverage': time_coverage,'num_of_params':num_of_params,'execution_time':execution_time}
    return pandas.DataFrame(data)
    #return numpy.corrcoef([area, time_coverage, num_of_params, execution_time])

    
dataframe = getDataFrame()
corr = dataframe.corr()
corr.to_csv("correlation.csv")
#print corr 
#seaborn.heatmap(corr, 
            #xticklabels=corr.columns.values,
            #yticklabels=corr.columns.values)
#seaborn.plt.show()
#

#gradient, intercept, r_value, p_value, std_err = stats.linregress(dataframe['time_coverage'].values,dataframe['execution_time'].values)
#print "Gradient and intercept", gradient, intercept
#print "R-squared", r_value**2
#print "p-value", p_value
#plotData(corr)


#print dataframe.head()
model = smf.ols(formula='execution_time ~ time_coverage', data=dataframe)
results = model.fit()
#print(results.summary())
fig, ax = plt.subplots()
fig = sm.graphics.plot_fit(results, 1, ax=ax)
#ax.set_ylabel("execution_time")
#ax.set_xlabel("time_coverage Level")
#ax.set_title("Linear Regression")
plt.show()


#df = sm.datasets.get_rdataset("Guerry", "HistData").data
#df = df[['Lottery', 'Literacy', 'Wealth', 'Region']].dropna()
#print df.head()

#mod = smf.ols(formula='Lottery ~ Literacy + Wealth + Region', data=df)
#results = mod.fit()
#print(results.summary())

#fig, ax = plt.subplots()
#fig = sm.graphics.plot_fit(results, 5, ax=ax)
#ax.set_ylabel("execution_time")
#ax.set_xlabel("time_coverage Level")
#ax.set_title("Linear Regression")
#plt.show()


