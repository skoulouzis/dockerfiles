#!/usr/bin/python
import json
import sys
from datetime import timedelta, date, datetime
from dateutil import rrule
from time import gmtime, strftime


date_format = "%Y-%m-%dT%H:%M:%SZ"
output_file_path ="/mnt/data/data_argo.txt"
metadata_file_path = "/mnt/data/source/ar_bigmetadata.json"
input_folder_path=  "/mnt/data/data_argo/"
subscription_date = "2017-04-10T13:28:06Z"
end_subscription_date= "2018-04-10T13:28:06Z"


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

deadline_date_tag = 'deadline_date'
        
med_box = {lon_min_tag: -6,lon_max_tag:37,
       lat_min_tag:30,lat_max_tag:46}


all_parameters = [9,11,12,13,20,28,30,35,43,44,45,50,54,55,58,59,60,61,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,82,83,84,87,88,89,90,94,95,96,97,98,100,101,102,103,104,105,106,107,108,109,114,124,132,133,135,139,145,146,147,148,150,151,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,180,183,184,188,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,385,386,387,388,389,390,391,392,393,394,395,396,397,398,399,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426,427,428,429,430,431,432,433,434,435,436,437,438,439,440,441,442,443,444,445,500,501,502,504,505,506,508,509,510,511,512,513,514,515,516,517,520,521,522,523,524,525,526,534,535,536,542,543,544,545,546,547,548,549,551,552,553,554,555,556,557,558,559,560,561,562,563,564,565,566,567,568,569,570,571,572,573,575,576,577,578,579,580,581,582,583,584,585,586,587,588,589,590,591,592,593,594,595,596,597,598,599,600,601,602,603,604,605,606,607,608,609,610,611,612,613,614,615,616,617,618,619,620,621,622,623,624,625,626,627,628,629,630,631,632,633,634,635,636,637,638,639,640,641,642,643,644,645]


def frange(x, y, jump):
  while x < y:
    yield x
    x += jump

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)
        
        
      

def create_conf_file(bounding_box,time_range,parameters,subscription_user_id,subscription_id):
    conf_data = {}
    conf_data[input_folder_tag] = input_folder_path
    conf_data[output_file_tag] = output_file_path
    conf_data[metadata_file_tag] = metadata_file_path
    conf_data[subs_date_tag] = subscription_date
    conf_data[end_subs_date_tag] = end_subscription_date   
    
    conf_data[bounding_box_tag] = bounding_box
    conf_data[time_tag] = time_range
    conf_data[parameters_tag] = parameters
    conf_data[subs_user_id_tag] = subscription_user_id
    conf_data[subs_id_tag] = subscription_id
    #conf_data[deadline_date_tag] = deadline_date
    
    #json_str = json.dumps(conf_data,ensure_ascii=False)
    return conf_data

def write_file(file_name,data):
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)
    outfile.close
    
def generate_range(bounding_box, coordinates_step,time_range,deadline_date,subscription_user_id,subscription_id):
    start_date = datetime.strptime(time_range[time_start_tag], date_format)
    end_date = datetime.strptime(time_range[time_end_tag], date_format)   
    
    
    now = datetime.strptime(strftime(date_format, gmtime()),date_format)
        
    start_lon = ( bounding_box[lon_min_tag] + 0.1)
    start_lat = ( bounding_box[lat_min_tag] + 0.1)
    count = 0;
    for i in frange(start_lon,bounding_box[lon_max_tag],coordinates_step):
        for j in frange(start_lat,bounding_box[lat_max_tag],coordinates_step):
            for dt in rrule.rrule(rrule.YEARLY, dtstart=start_date, until=end_date):
                for dl in rrule.rrule(rrule.DAILY, dtstart=now, until=deadline_date):
                    cum_param = []
                    for param in all_parameters:
                        cum_param.append(param)
                        if len(cum_param)%200==0:
                            input_bounding_box = {lon_min_tag: start_lon,lon_max_tag:i,
                                                lat_min_tag:start_lat,lat_max_tag:j}
                            input_time_range = {time_start_tag:str(start_date.strftime(date_format)),
                                                time_end_tag:str(dt.strftime(date_format))}
                            input_params = cum_param
                            data = create_conf_file(input_bounding_box,input_time_range,input_params,subscription_user_id,subscription_id,dl)
                            write_file(str(count)+"_conf.json",data)
                            count += 1
                            
                        input_params = all_parameters
                        input_bounding_box = {lon_min_tag: start_lon,lon_max_tag:i,
                                                lat_min_tag:start_lat,lat_max_tag:j}
                        input_time_range = {time_start_tag:str(start_date.strftime(date_format)),
                                                time_end_tag:str(dt.strftime(date_format))}
                        data = create_conf_file(input_bounding_box,input_time_range,input_params,subscription_user_id,subscription_id,dl)
                        write_file(str(count)+"_conf.json",data)
                        count += 1
                        
                    input_params = all_parameters
                    input_bounding_box = {lon_min_tag: start_lon,lon_max_tag:i,
                                                lat_min_tag:start_lat,lat_max_tag:j}
                    input_time_range = {time_start_tag:str(start_date.strftime(date_format)),
                                            time_end_tag:str(end_date.strftime(date_format))}
                    data = create_conf_file(input_bounding_box,input_time_range,input_params,subscription_user_id,subscription_id,dl)
                    write_file(str(count)+"_conf.json",data)
                    count += 1          

                input_params = all_parameters
                input_bounding_box = {lon_min_tag: start_lon,lon_max_tag:i,
                                            lat_min_tag:start_lat,lat_max_tag: bounding_box[lat_max_tag]}
                input_time_range = {time_start_tag:str(start_date.strftime(date_format)),
                                        time_end_tag:str(end_date.strftime(date_format))}
                data = create_conf_file(input_bounding_box,input_time_range,input_params,subscription_user_id,subscription_id,dl)
                write_file(str(count)+"_conf.json",data)
                count += 1              
                
            input_params = all_parameters
            input_bounding_box = {lon_min_tag: start_lon,lon_max_tag:bounding_box[lon_max_tag],
                                        lat_min_tag:start_lat,lat_max_tag: bounding_box[lat_max_tag]}
            input_time_range = {time_start_tag:str(start_date.strftime(date_format)),
                                    time_end_tag:str(end_date.strftime(date_format))}
            data = create_conf_file(input_bounding_box,input_time_range,input_params,subscription_user_id,subscription_id,dl)
            write_file(str(count)+"_conf.json",data)
            count += 1          



subscription_user_id = "1"
subscription_id = "1"
time_range = {time_start_tag:"1999-01-01T00:00:19Z",time_end_tag:"2020-01-01T00:00:19Z"}


now = datetime.now()
#later = now + timedelta(days=10)
#later = datetime.strptime(str(now + timedelta(days=10)), date_format)

step = 20
#generate_range(med_box,step,time_range,later,subscription_user_id,subscription_id)





parameters = [9, 11, 12, 13, 20, 28, 30, 35, 43, 44, 45, 50, 54, 55, 58, 59, 60, 61, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 82, 83, 84, 87, 88, 89, 90, 94, 95, 96, 97, 98, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 114, 124, 132, 133, 135, 139, 145, 146, 147, 148, 150, 151, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 180, 183, 184, 188, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 500, 501, 502, 504, 505, 506, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 520, 521, 522, 523, 524, 525, 526, 534, 535, 536, 542, 543, 544, 545, 546, 547, 548, 549, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635]





data = create_conf_file(med_box,time_range,parameters,subscription_user_id,subscription_id)
write_file("0_conf.json",data)


data = create_conf_file(med_box,time_range,parameters,subscription_user_id,subscription_id)
write_file("1_conf.json",data)
time_range = {time_start_tag:"1999-01-01T00:00:19Z",time_end_tag:"2001-01-01T00:00:19Z"}