from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import rrule
import json
import os
import pymongo
from pymongo import Connection
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir) 
from util.constants import *
import numpy as np



class ConfigurationGenerator:
    
    def __init__(self):
        self.const = Constants()
        
    def create_conf(self, input_folder_path, output_file_path, metadata_file_path, 
                    subscription_date, end_subscription_date, bounding_box, 
                    time_range, deadline_date, parameters, subscription_user_id, subscription_id):
        conf_data = {}
        conf_data[self.const.input_folder_tag] = input_folder_path
        conf_data[self.const.output_file_tag] = output_file_path
        conf_data[self.const.metadata_file_tag] = metadata_file_path
        conf_data[self.const.subs_date_tag] = subscription_date
        conf_data[self.const.end_subs_date_tag] = end_subscription_date   
            
        conf_data[self.const.bounding_box_tag] = bounding_box
        conf_data[self.const.time_tag] = time_range
        conf_data[self.const.parameters_tag] = parameters
        conf_data[self.const.subs_user_id_tag] = subscription_user_id
        conf_data[self.const.subs_id_tag] = subscription_id
        conf_data[self.const.deadline_date_tag] = deadline_date
            
        # json_str = json.dumps(conf_data,ensure_ascii=False)
        return conf_data
    
    def write_file(self, file_name, data):
        with open(file_name, 'w') as outfile:
            json.dump(data, outfile)
        outfile.close
        
    def frange(self, x, y, jump):
        while x < y:
            yield x
            x += jump        
        
    def generate_conf_range(self, 
                            input_folder_path,
                            output_file_path,
                            metadata_file_path, 
                            subscription_date, 
                            end_subscription_date,
                            bounding_box, 
                            coordinates_step, 
                            time_range, 
                            deadline_date_str,
                            subscription_id, 
                            subscription_user_id):
        start_date = datetime.strptime(time_range[self.const.time_start_tag], self.const.date_format)
        end_date = datetime.strptime(time_range[self.const.time_end_tag], self.const.date_format)
        deadline_date = datetime.strptime(deadline_date_str, self.const.date_format)
        
        
        
        
        start_lon = (bounding_box[self.const.lon_min_tag] + 0.1)
        start_lat = (bounding_box[self.const.lat_min_tag] + 0.1)

        lon_vals = np.arange(start_lon, bounding_box[self.const.lon_max_tag], coordinates_step)
        lat_vals = np.arange(start_lat, bounding_box[self.const.lat_max_tag], coordinates_step)       
        
        conf_list = []
        now = datetime.now()
        later = now + timedelta(minutes=10)
        data = {}
        for i in lon_vals:
            if i <= bounding_box[self.const.lon_min_tag]:
                continue
            for j in lat_vals:
                if j <= bounding_box[self.const.lat_min_tag]:
                    continue                
                for dt in rrule.rrule(rrule.YEARLY, dtstart=start_date, until=end_date):
                    if start_date == dt:
                        continue
                    for dl in rrule.rrule(rrule.MINUTELY, dtstart=later, until=deadline_date):                       
                        cum_param = []
                        for param in self.const.all_parameters:
                            cum_param.append(param)
                            if len(cum_param) % 200 == 0:
                                input_bounding_box = {self.const.lon_min_tag: bounding_box[self.const.lon_min_tag], self.const.lon_max_tag:i,
                                self.const.lat_min_tag:bounding_box[self.const.lat_min_tag], self.const.lat_max_tag:j}
                                input_time_range = {self.const.time_start_tag:(start_date), 
                                self.const.time_end_tag:(dt)}
                                input_deadline = (dl)
                                input_params = cum_param
                                data = self.create_conf(input_folder_path, 
                                                        output_file_path, 
                                                        metadata_file_path, 
                                                        subscription_date, 
                                                        end_subscription_date, 
                                                        input_bounding_box, 
                                                        input_time_range,
                                                        input_deadline,
                                                        input_params, 
                                                        subscription_id, 
                                                        subscription_user_id)
                                conf_list.append(data)
                                data = {}
                        
                        input_bounding_box = {self.const.lon_min_tag: bounding_box[self.const.lon_min_tag], self.const.lon_max_tag:i,
                        self.const.lat_min_tag:bounding_box[self.const.lat_min_tag], self.const.lat_max_tag:j}
                        input_time_range = {self.const.time_start_tag:(start_date), 
                        self.const.time_end_tag:(dt)}
                        input_deadline = (dl)
                        input_params = self.const.all_parameters
                        data = self.create_conf(input_folder_path, 
                                                output_file_path, 
                                                metadata_file_path, 
                                                subscription_date, 
                                                end_subscription_date, 
                                                input_bounding_box, 
                                                input_time_range,
                                                input_deadline,
                                                input_params, 
                                                subscription_id, 
                                                subscription_user_id)
                        conf_list.append(data)
                            
                    input_bounding_box = {self.const.lon_min_tag: bounding_box[self.const.lon_min_tag], self.const.lon_max_tag:i,
                    self.const.lat_min_tag:bounding_box[self.const.lat_min_tag], self.const.lat_max_tag:j}
                    input_time_range = {self.const.time_start_tag:(start_date), 
                    self.const.time_end_tag:(dt)}
                    input_deadline = deadline_date
                    input_params = self.const.all_parameters

                    data = self.create_conf(input_folder_path, 
                                            output_file_path, 
                                            metadata_file_path, 
                                            subscription_date, 
                                            end_subscription_date, 
                                            input_bounding_box, 
                                            input_time_range,
                                            input_deadline,
                                            input_params, 
                                            subscription_id, 
                                            subscription_user_id)
                    conf_list.append(data)
                    
                input_bounding_box = {self.const.lon_min_tag: bounding_box[self.const.lon_min_tag], self.const.lon_max_tag:i,
                self.const.lat_min_tag:bounding_box[self.const.lat_min_tag], self.const.lat_max_tag:j}
                input_time_range = {self.const.time_start_tag:(start_date), 
                self.const.time_end_tag:(end_date)}
                input_deadline = deadline_date
                input_params = self.const.all_parameters

                data = self.create_conf(input_folder_path, 
                                        output_file_path, 
                                        metadata_file_path, 
                                        subscription_date, 
                                        end_subscription_date, 
                                        input_bounding_box, 
                                        input_time_range,
                                        input_deadline,
                                        input_params, 
                                        subscription_id, 
                                        subscription_user_id)
                conf_list.append(data)
                    
            input_bounding_box = {self.const.lon_min_tag: bounding_box[self.const.lon_min_tag], self.const.lon_max_tag:i,
            self.const.lat_min_tag:bounding_box[self.const.lat_min_tag], self.const.lat_max_tag:bounding_box[self.const.lat_max_tag]}
            input_time_range = {self.const.time_start_tag:(start_date), 
            self.const.time_end_tag:(end_date)}
            
            
            input_deadline = deadline_date
            input_params = self.const.all_parameters

            data = self.create_conf(input_folder_path, 
                                    output_file_path, 
                                    metadata_file_path, 
                                    subscription_date, 
                                    end_subscription_date, 
                                    input_bounding_box, 
                                    input_time_range,
                                    input_deadline,
                                    input_params, 
                                    subscription_id, 
                                    subscription_user_id)
            conf_list.append(data)         
                
        input_bounding_box = {self.const.lon_min_tag: bounding_box[self.const.lon_min_tag], self.const.lon_max_tag:bounding_box[self.const.lon_max_tag],
        self.const.lat_min_tag:bounding_box[self.const.lat_min_tag], self.const.lat_max_tag:bounding_box[self.const.lat_max_tag]}
        input_time_range = {self.const.time_start_tag:(start_date), 
        self.const.time_end_tag:(end_date)}
        input_deadline = deadline_date
        input_params = self.const.all_parameters
        
        data = self.create_conf(input_folder_path, 
                                output_file_path, 
                                metadata_file_path, 
                                subscription_date, 
                                end_subscription_date, 
                                input_bounding_box, 
                                input_time_range,
                                input_deadline,
                                input_params, 
                                subscription_id, 
                                subscription_user_id)
        conf_list.append(data)     
        return conf_list
            
        
        