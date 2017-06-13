#!/usr/bin/python

import getDelta
from getDelta import *
import json
import os
from datetime import datetime
from datetime import timedelta


def get_time_range(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
        return data['time_range']




def get_num_of_nodes(nodes_file):
    with open(nodes_file) as f:
        return sum(1 for _ in f)
    
    
def create_time_range_configuration(time_coverage_start,time_coverage_end,json_file):
    with open(json_file, "r") as jsonFile:
        data = json.load(jsonFile)
        time_range = data['time_range']
        time_range['time_coverage_start'] = time_coverage_start
        time_range['time_coverage_end'] = time_coverage_end
        data['time_range'] = time_range
        return data
    
    


if __name__ == '__main__':
    conf_file =  sys.argv[1]
    time_range = get_time_range(conf_file)

    problem_size = calculateDatesDelta(time_range['time_coverage_start'], time_range['time_coverage_end'])
    number_of_nodes = int(sys.argv[2])
    chunk_size = (problem_size)//(number_of_nodes)
    #print problem_size%number_of_nodes

    node_index=0
    start_date = datetime.strptime(time_range['time_coverage_start'], "%Y-%m-%dT%H:%M:%SZ")
    for i in range(0,int(problem_size),int(chunk_size+1)):
        start=i
        end=i+chunk_size
        if end > problem_size:
            end = problem_size
        #print "Node: %s Chunk: %s - %s" %(node_index,start,end)
        end_date =  start_date + timedelta(seconds=end)
        #print "Node: %s Chunk: %s - %s" %(node_index,start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),end_date.strftime("%Y-%m-%dT%H:%M:%SZ"))
        new_conf = create_time_range_configuration(start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),conf_file)
        with open(str(node_index)+"_"+conf_file, "w") as jsonFile:
            json.dump(new_conf, jsonFile)
        start_date = end_date
        node_index+=1
        
    
    