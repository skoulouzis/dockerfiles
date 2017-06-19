from bson.objectid import ObjectId
from constants import *
from datetime import datetime
from datetime import timedelta
from functools import partial
import json
import math
import os
import pyproj
from pyproj import Proj
import random
import shapely
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon
import shapely.ops as ops
import string
import sys


class Util:
    
    def __init__(self):
        self.const = Constants()

    def get_time_delta(self, start, end):
        start_date = datetime.strptime(start, self.const.date_format)
        end_date = datetime.strptime(end, self.const.date_format)
        delta = end_date-start_date
        return delta.total_seconds()
    
    def get_time_delta(self, start, end):
        delta = end-start
        return delta    
    
    #Code from http://stackoverflow.com/questions/13148037/calculating-area-from-lat-lon-polygons-in-python
    def get_area(self, lat_min, lat_max, lon_min, lon_max):
        co = {"type": "Polygon", "coordinates": [
            [(float(lon_min), lat_max),
            (float(lon_min), float(lat_min)),
            (float(lon_max), float(lat_min)),
            (float(lon_max), float(lat_max))]]}   
            
        lon, lat = zip(*co['coordinates'][0])
        from pyproj import Proj
        pa = Proj("+proj=cea +lon_0=0 +lat_ts=45 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs")
        x, y = pa(lon, lat)
        cop = {"type": "Polygon", "coordinates": [zip(x, y)]}
        from shapely.geometry import shape
        return shape(cop).area
    
    def get_area(self, box):
        lon_min = float(box[self.const.lon_min_tag])
        lon_max = float(box[self.const.lon_max_tag])
        lat_min = float(box[self.const.lat_min_tag])
        lat_max = float(box[self.const.lat_max_tag])
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
        return shape(cop).area    
    
    
    def convert_dates_to_string(self, task):
        
        if not (isinstance(task[self.const.time_tag][self.const.time_start_tag], str) or isinstance(task[self.const.time_tag][self.const.time_start_tag], unicode)):
            time_start  = task[self.const.time_tag][self.const.time_start_tag].strftime(self.const.date_format) 
            task[self.const.time_tag][self.const.time_start_tag] = time_start
        if not (isinstance(task[self.const.time_tag][self.const.time_end_tag], str) or isinstance(task[self.const.time_tag][self.const.time_end_tag], unicode)):
            time_end  = task[self.const.time_tag][self.const.time_end_tag].strftime(self.const.date_format)
            task[self.const.time_tag][self.const.time_end_tag] = time_end
                    
        if not (isinstance(task[self.const.subs_date_tag], str) or isinstance(task[self.const.subs_date_tag], unicode)):
            subs_date  = task[self.const.subs_date_tag].strftime(self.const.date_format)
            task[self.const.subs_date_tag] = subs_date
        if not (isinstance(task[self.const.end_subs_date_tag], str) or isinstance(task[self.const.end_subs_date_tag], unicode)):
            end_subs_date  = task[self.const.end_subs_date_tag].strftime(self.const.date_format)
            task[self.const.end_subs_date_tag] = end_subs_date       
        if not (isinstance(task[self.const.deadline_date_tag], str) or isinstance(task[self.const.deadline_date_tag], unicode)):
            deadline_date  = task[self.const.deadline_date_tag].strftime(self.const.date_format)
            task[self.const.deadline_date_tag] = deadline_date                   
        return task
    
    
    def uid_to_string(self, task):
        task['_id'] = str(task['_id'])
        return task
    
    def build_output(self, task, elapsed, execution_date, num_of_nodes, executing_node, num_of_tasks, partition_type):
        out_data = {}
        if (isinstance(task[self.const.bounding_box_tag][self.const.lon_min_tag], str)):
            area = self.get_area(task[self.const.bounding_box_tag][self.const.lat_min_tag], task[self.const.bounding_box_tag][self.const.lat_min_tag], task[self.const.bounding_box_tag][self.const.lon_min_tag], task[self.const.bounding_box_tag][self.const.lon_max_tag])
        else:
            area = self.get_area(task[self.const.bounding_box_tag])
        out_data['area'] = area


        if (isinstance(task[self.const.time_tag][self.const.time_start_tag], str) or isinstance(task[self.const.time_tag][self.const.time_start_tag], unicode)):
            start_date = datetime.strptime(task[self.const.time_tag][self.const.time_start_tag], self.const.date_format)
        else:
            start_date = task[self.const.time_tag][self.const.time_start_tag]
        if (isinstance(task[self.const.time_tag][self.const.time_end_tag], str) or isinstance(task[self.const.time_tag][self.const.time_end_tag], unicode)):
            end_date = datetime.strptime(task[self.const.time_tag][self.const.time_end_tag], self.const.date_format)
        else:
            end_date = task[self.const.time_tag][self.const.time_end_tag]

        out_data['time_coverage'] = self.get_time_delta(start_date, end_date).total_seconds()

        out_data['num_of_params'] = len(task[self.const.parameters_tag])
        out_data['dataset_size'] = self.get_size(task[self.const.input_folder_tag])
        out_data['execution_time'] = elapsed #'%.3f' % elapsed.total_seconds()
        out_data['execution_date'] = execution_date.strftime(self.const.date_format)
        task = self.convert_dates_to_string(task)
        task = self.uid_to_string(task)
        out_data['configuration'] = task #json.dumps(task)
        out_data['num_of_nodes'] = num_of_nodes
        out_data['executing_node'] = executing_node
        out_data['num_of_tasks'] = num_of_tasks        
        if partition_type != None or not partition_type:
            out_data['partition_type'] = partition_type
        return json.dumps(out_data)    
    
    def get_size(self, start_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size
    

    def randomword(self):
        return ''.join(random.choice(string.lowercase) for i in range(5))
    
    def build_deadline_output(self, task, sub_tasks, threshold):
        time_coverage = 0
        last_exec_date = datetime(10, 1, 1)
        if (isinstance(task[self.const.bounding_box_tag][self.const.lon_min_tag], str)):
            area = self.get_area(task[self.const.bounding_box_tag][self.const.lat_min_tag], task[self.const.bounding_box_tag][self.const.lat_min_tag], task[self.const.bounding_box_tag][self.const.lon_min_tag], task[self.const.bounding_box_tag][self.const.lon_max_tag])
        else:
            area = self.get_area(task[self.const.bounding_box_tag])
        num_of_params = len(task[self.const.parameters_tag])
        if (isinstance(task[self.const.time_tag][self.const.time_start_tag], str) or isinstance(task[self.const.time_tag][self.const.time_start_tag], unicode)):
            start_date = datetime.strptime(task[self.const.time_tag][self.const.time_start_tag], self.const.date_format)
        else:
            start_date = task[self.const.time_tag][self.const.time_start_tag]
        if (isinstance(task[self.const.time_tag][self.const.time_end_tag], str) or isinstance(task[self.const.time_tag][self.const.time_end_tag], unicode)):
            end_date = datetime.strptime(task[self.const.time_tag][self.const.time_end_tag], self.const.date_format)
        else:
            end_date = task[self.const.time_tag][self.const.time_end_tag]

        time_coverage = self.get_time_delta(start_date, end_date).total_seconds()

        for sub in sub_tasks:
            exec_date = datetime.strptime(sub['execution_date'], self.const.date_format)
        if exec_date > last_exec_date:
            last_exec_date = exec_date
            deadline = sub['configuration']['deadline_date']
        if (isinstance(deadline, str) or isinstance(deadline, unicode)): 
            deadline = datetime.strptime(deadline, self.const.date_format)
            execution_rank = sub['configuration']['execution_rank']
            
        diff = deadline - last_exec_date
        out_data = {}
        _id = task['_id']
        out_data['_id'] = str(_id)
        out_data['execution_date'] = last_exec_date.strftime(self.const.date_format)
        out_data['deadline_date'] = deadline.strftime(self.const.date_format)
        out_data['time_to_deadline'] = diff.total_seconds()
        out_data['execution_rank']  = execution_rank
        out_data['area']  = area
        out_data['num_of_params']  = num_of_params
        out_data['time_coverage']  = time_coverage  
        if not (threshold is None):
            out_data['threshold']  = threshold
        return out_data
    
    def get_num_of_lines_in_file(self, file_path):
        with open(file_path) as f:
            return sum(1 for _ in f)    