#!/usr/bin/python

import pymongo
from pymongo import Connection
import numpy
from string import letters

import seaborn
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from random import randint



            

def fill_in_nodes():
    connection = Connection('localhost', 27017)
    db = connection.drip     
    docs = db.argoBenchmark.find({ "num_of_nodes" : { "$exists" : False } })
    for doc in docs:             
        db.argoBenchmark.update({'_id':  doc['_id']},{'$set': {'num_of_nodes': 1}}, upsert=False, multi=False)
        
        
        

#fill_in_nodes()
remove_duplicates()