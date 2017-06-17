# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

from config.configuration_generator import *
from db.db_helper import *
from execution.submitter import *
from execution.worker import *
from schedule.partitioner import *
from schedule.scheduler import *
import socket
import timeit
from util.constants import *
from util.util import *


conf = ConfigurationGenerator()
const = Constants()
sch = Scheduler()
db = DBHelper("localhost", 27017)
partitioner = Partitioner()
submitter = Submitter("localhost", 5672, "task_queue")
done_listener = Submitter("localhost", 5672, "task_queue_done")
util = Util()

time_range = {const.time_start_tag:"1999-01-01T00:00:19Z", const.time_end_tag:"2020-01-01T00:00:19Z"}
subscription_user_id = "1"
subscription_id = "1"
output_file_path = "/mnt/data/data_argo.txt"
metadata_file_path = "/mnt/data/source/ar_bigmetadata.json"
input_folder_path = "/mnt/data/data_argo/"
subscription_date = "2017-04-10T13:28:06Z"
end_subscription_date = "2018-04-10T13:28:06Z"
now = datetime.now()    

deadline_date = now + timedelta(hours=7)
deadline_date = str(deadline_date.strftime(const.date_format))

coordinates_step = 5
bounding_box = {const.lon_min_tag:-1, const.lon_max_tag:9,
const.lat_min_tag:7, const.lat_max_tag:11}

    



    
    
def generate_tasks():
    tasks = conf.generate_conf_range(input_folder_path, 
                                     output_file_path, 
                                     metadata_file_path, 
                                     subscription_date, 
                                     end_subscription_date, 
                                     bounding_box, 
                                     coordinates_step,
                                     time_range, 
                                     deadline_date, 
                                     subscription_id, 
                                     subscription_user_id)
    return tasks



if __name__ == "__main__":
    if len(sys.argv) > 1:
        op = sys.argv[1]
        if op != None and op == "worker":
            worker = Worker("localhost", 5672, "task_queue")
            worker.consume()
        elif op != None and op == "master":
            num_of_nodes = submitter.get_number_of_consumers()
            tasks_per_node = 1
            start = datetime.now()
            start_time = timeit.default_timer()
            task = db.get_first_task()
        #    sub_tasks = partitioner.partition_linear(task, tasks_per_node * num_of_nodes)
            sub_tasks = partitioner.partition_log(task, tasks_per_node * num_of_nodes)

            num_of_tasks = 0
            for sub in sub_tasks:
                submitter.submitt_task(sub)
                num_of_tasks += 1


            done_listener.listen(num_of_tasks)
            end = done_listener.last_exec_date
            elapsed = timeit.default_timer() - start_time

            executing_node = str(socket.gethostname())

            out = util.build_output(task, elapsed, start, num_of_nodes, executing_node, num_of_tasks)
            print out
#            db.mark_task_done(t)
        elif op != None and op == "init_task":
            tasks = generate_tasks()
            ranked_tasks = sch.rank_tasks(tasks)
            db.import_tasks(ranked_tasks)
    

    
    
    
    
    
    
    
        
