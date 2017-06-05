#!/usr/bin/python

class ArgoModel:
    description = 'argo model file class'
    
    def __init__(self):
        'init'
        self.stations = {}
        self.parameters = []


    def add_data_line(self, row):
        'add data line in model'
        
        #test if station exists
        station_id = row[0]
        if station_id in self.stations:
            #select station
            station = self.stations[station_id]
        else:
            #create new station
            platform_code = row [1]
            station_date = row [2]
            latitude = row [3]
            longitude = row [4]    
            station = Station(station_id, platform_code, station_date, latitude, longitude)
            #save new station in dict
            self.stations[station_id] = station
        
        #add z and parameter data 
        parameter_code = row [6]    
        parameter_value = row [7]    
        parameter_qc = row [8]    
        z_code = row [9]    
        z_value = row [10]    
        z_qc = row [11]  
        #station.add_data_line(parameter_code, parameter_value,parameter_qc,z_code,z_value,z_qc)
        
        if z_code not in  self.parameters:
            self.parameters.append(z_code)
        if parameter_code not in  self.parameters:
            self.parameters.append(parameter_code)



class Station:
    description = 'station model class'
    
    def __init__(self, station_id, platform_code, station_date, latitude, longitude):
        'init'
        self.station_id = station_id
        self.platform_code = platform_code
        self.station_date = station_date
        self.latitude = latitude
        self.longitude = longitude
        
        self.parameters = []
        # variables list
        self.levels = {}


    def add_data_line(self, parameter_code, parameter_value,parameter_qc,z_code,z_value,z_qc):
        'store data line'        
        if z_value in self.levels:
            line = self.levels[z_value]
            line.add_parameter(parameter_code, parameter_value,parameter_qc)
        else:
            line = Line(parameter_code, parameter_value,parameter_qc,z_code,z_value,z_qc)
            self.levels[z_value] = line
        
        #create parameter list for the station 
        if z_code not in  self.parameters:
            self.parameters.append(z_code)
        if parameter_code not in  self.parameters:
            self.parameters.append(parameter_code)

    def getSize(self):
        return len(self.levels)
 
 
            
class Line:
    description = 'variable model class'
    
    def __init__(self, parameter_code, parameter_value, parameter_qc,z_code,z_value,z_qc):
        'init'
        self.parameters = []
        
        self.variables = {}
        var = Variable(z_code,z_value,z_qc)
        self.variables[z_code] = var
        var = Variable(parameter_code,parameter_value,parameter_qc)
        self.variables[parameter_code] = var

        #create parameter list for the line 
        if z_code not in  self.parameters:
            self.parameters.append(z_code)
        if parameter_code not in  self.parameters:
            self.parameters.append(parameter_code)
        
        
    def add_parameter(self, parameter_code, parameter_value, parameter_qc):
        'add parameter'
        var = Variable(parameter_code,parameter_value,parameter_qc)
        self.variables[parameter_code] = var
        
        #parameter list 
        if parameter_code not in  self.parameters:
            self.parameters.append(parameter_code)



class Variable:
    description = 'variable model class'
    
    def __init__(self, parameter_code, value, qc):
        'init'
        self.parameter_code = parameter_code
        self.value = value
        self.qc = qc
