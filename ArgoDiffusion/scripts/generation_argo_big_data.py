#!/usr/bin/python

import json
import csv
import time
import sys
import os.path
import psutil
import argo_model
from klepto.archives import *


sys.settrace 

# time format
print_time_format = '%a, %d %b %Y %H:%M:%S'
date_format = '%Y-%m-%dT%H:%M:%SZ'
mont_time_format = '%Y%m'


try:
    os.remove("/tmp/stations.tmp")
except OSError:
    pass


class Argo:
    
    def __init__(self):
        'init'

        #init model
        self.model = argo_model.ArgoModel()
        
        
    def run(self):
        'process'
        
        # process beginning
        start_time = time.gmtime()
        start_time_sec = time.time()

        # init configuration and selection parameters    
        self.read_configuration()
        
        #test
        if start_time < self.end_subs_date:
            # build filtered list files
            list_files = []
            for ncfile in os.listdir(self.input_folder):
                if ncfile.endswith(".csv"):
                    #extract date from filename (YYYYMM format)
                    date_file = ncfile.split('_')[2].split('.')[0]
                    
                    #build time range from configuration (YYYYMM format) 
                    begin = time.strftime(mont_time_format, self.begin_date)
                    end = time.strftime(mont_time_format, self.end_date)
            
                    #test if file data in time range
                    if int(begin) <= int(date_file) <= int(end):
                        list_files.append(os.path.join(self.input_folder, ncfile))
                        
            
            # loop on select files
            for argofile in list_files:
                self.read_file(argofile)
                    
            #self.model.dump()
            #build parameters labels
            label_parameters = self.build_parameter_labels()
              
            #create odv file
            self.write_csv_odv(label_parameters)
    
        else:
            print 'the end subscription date has passed'
            
        # process ending
        duration = time.time() - start_time_sec
        
        #create json structure
        out_data = {}
        out_data['subscription_id'] = self.subs_id
        out_data['subscription_user_id'] = self.subs_user_id
        out_data['date'] = time.strftime(date_format, start_time)
        out_data['duration (seconds)'] = '%.3f' % duration
        out_data = json.dumps(out_data)
        
        return out_data
    
    
    def read_file(self, argofile):
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
                if self.min_lat < lat < self.max_lat and self.min_lon < lon < self.max_lon:
                        # test parameter
                        parameter = int(row [6])
                        if not self.parameters or parameter in self.parameters:
                            #date
                            station_date = row [2]
                            station_date = time.strptime(station_date, date_format)
                            if self.begin_date < station_date < self.end_date :
                                self.model.add_data_line(row)
                                
        finally:
            fargofile.close()
    
    def build_parameter_labels(self):
        
        input_file = file(self.metadata_file, "r")
        data = json.loads(input_file.read().decode("utf-8", "ignore"))
        config_parameters = data['physical_parameter']
        
        parameters_dict = {}
        for parameter in self.model.parameters:
            unit = config_parameters[parameter]['unit']
            label = config_parameters[parameter]['label']
            parameter_label = label + " [" + unit + "]"
            parameters_dict[parameter] = parameter_label
        
        return parameters_dict

        
    def read_configuration(self):
        
        input_folder_tag = 'input_folder'
        metadata_file_tag = 'metadata_file'
        output_file_tag = 'output_file'
        
        bounding_box_tag = 'bounding_box'
        lat_min_tag = 'geospatial_lat_min'
        lat_max_tag = 'geospatial_lat_max'
        lon_min_tag = 'geospatial_lon_min'
        lon_max_tag = 'geospatial_lon_max'
        
        time_tag = 'time_range'
        time_start_tag = 'time_coverage_start'
        time_end_tag = 'time_coverage_end'
        
        parameters_tag = 'parameters'
        
        subs_id_tag = 'subscription_id'
        subs_user_id_tag = 'subscription_user_id'
        
        subs_date_tag = 'subscription_date'
        end_subs_date_tag = 'end_subscription_date'
    
        with open(config_file) as data_file:
            data = json.load(data_file)
        
        self.input_folder = data[input_folder_tag]
        self.metadata_file = data[metadata_file_tag]
        self.output_path = data[output_file_tag]
    #     print(self.input_folder, self.metadata_file, self.output_path)
        
        self.min_lat = data[bounding_box_tag][lat_min_tag]
        self.max_lat = data[bounding_box_tag][lat_max_tag]
        self.min_lon = data[bounding_box_tag][lon_min_tag]
        self.max_lon = data[bounding_box_tag][lon_max_tag]
    #     print(self.min_lat, self.max_lat, self.min_lon, self.max_lon)
        
        self.begin_date = data[time_tag][time_start_tag]
        self.begin_date = time.strptime(self.begin_date, date_format)
        self.end_date = data[time_tag][time_end_tag]
        self.end_date = time.strptime(self.end_date, date_format)
    #     print self.begin_date, self.end_date
        
        #parameter tag is  optional
        self.parameters = []
        if parameters_tag in data:
            self.parameters = data[parameters_tag]
    #     print self.parameters
        
        self.subs_id = data[subs_id_tag]
        self.subs_user_id = data[subs_user_id_tag]
    #     print subs_id, subs_user_id
        
        self.subs_date = data[subs_date_tag]
        self.subs_date = time.strptime(self.subs_date, date_format)
        self.end_subs_date = data[end_subs_date_tag]
        self.end_subs_date = time.strptime(self.end_subs_date, date_format) 
    
    
    def write_csv_odv(self, label_parameters):
        cruise_label = 'Cruise'
        station_label = 'Station'
        date_label = 'yyyy-mm-ddThh:mm:ss'
        long_label= 'Longitude [degrees_east]'
        lat_label = 'Latitude [degrees_north]'
        qc_label = 'QV:ARGO'
        
        #create odv-csv file
        csv.register_dialect('out', delimiter='\t')
        try:
            fout = open(self.output_path, 'wb')
            writer = csv.writer(fout, dialect='out')
            #build the header line and write
            header = []
            header.append(cruise_label)
            header.append(station_label)
            header.append(date_label)
            header.append(long_label)
            header.append(lat_label)
            
            #build paramter labels list
            for par in self.model.parameters:
                header.append(label_parameters[par])
                header.append(qc_label)
            writer.writerow(header)
            
            #build the data lines and write
            #dump_stations = file_archive('/tmp/stations.tmp')
            #dump_stations.load()
            
            #if len(dump_stations)==0:
            dump_stations = self.model.stations
                
            
            for station_id in dump_stations:
                #print station_id.station_id
                station = dump_stations[station_id]
                
                for idx, level in enumerate(station.levels):
                    #first line, header
                    if idx == 0:
                        cruise = station.platform_code
                        station_val = station.station_id
                        date_val = station.station_date
                        latitude = station.latitude
                        longitude = station.longitude
                    else:
                        cruise = None
                        station_val = None
                        date_val = None
                        latitude = None
                        longitude = None
                    
                    tmp_row = [cruise, station_val, date_val, longitude, latitude]
                    
                    line = station.levels[level]
                    for par in self.model.parameters:
                        if par in line.parameters:
                            tmp_row.append(line.variables[par].value)
                            tmp_row.append(line.variables[par].qc)
                        else:
                            tmp_row.append(None)
                            tmp_row.append(None)
                    writer.writerow(tmp_row)
        except Exception, e:
            print repr(e)
        finally:
            fout.close()            
            
            



if __name__ == '__main__':
    from optparse import OptionParser
    
    ##############################
    #gestion args
    parser = OptionParser("%prog json_config_file")
    
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    else:
        config_file = args[0]
    try:
        argo = Argo()
    except Exception as ex:
        logging.exception("Something happened!")
    
    print argo.run()
    
    #process = psutil.Process(os.getpid())
    #mem = process.memory_percent()
    #cpu = process.cpu_percent()
    #disk_io = process.disk_io_counters()
    #print mem
    #print cpu
