# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

from config.configuration_generator import *
from db.db_helper import *
from execution.submitter import *
from execution.monitor import *
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
partitioner = Partitioner()
util = Util()

time_range = {const.time_start_tag:"1999-01-01T00:00:19Z", const.time_end_tag:"2003-01-01T00:00:19Z"}
subscription_user_id = "1"
subscription_id = "1"
output_file_path = "/mnt/data/data_argo.txt"
metadata_file_path = "/mnt/data/source/ar_bigmetadata.json"
input_folder_path = "/mnt/data/data_argo/"
subscription_date = "2017-04-10T13:28:06Z"
end_subscription_date = "2018-04-10T13:28:06Z"
now = datetime.now()
list_of_nodes = "/mnt/data/source/ssh.8"


deadline_date = now + timedelta(minutes=5)
deadline_date = str(deadline_date.strftime(const.date_format))

coordinates_step = 4
bounding_box = {const.lon_min_tag:-2, const.lon_max_tag:10,
const.lat_min_tag:6, const.lat_max_tag:12}
partition_type = "log"
tasks_per_node = 1
task_limit = 100
    



def wait_for_output(num_of_tasks):
    done_listener = Submitter("localhost", 5672, "task_queue_done")
    done_listener.listen(num_of_tasks)
    end = done_listener.last_exec_date
    elapsed = timeit.default_timer() - start_time
    executing_node = str(socket.gethostname())
    out = util.build_output(task, elapsed,  datetime.now(), num_of_nodes, executing_node, num_of_tasks, partition_type)
    print out
    
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

def get_missed_deadlines(total_num_of_tasks):    
    done_listener = Submitter("localhost", 5672, "task_queue_done")
    done_listener.listen(total_num_of_tasks)
    finised_tasks = done_listener.finised_tasks
    for task_id in finised_tasks:
        sub_tasks = finised_tasks[task_id]
        task = db.get_task_by_id(task_id)
        out = util.build_deadline_output(task,sub_tasks)        
        print json.dumps(out)

        

if __name__ == "__main__":
    if len(sys.argv) > 1:
        op = sys.argv[1]
        if op != None and op == "worker":
            worker = Worker(sys.argv[2], sys.argv[3], "task_queue")
            worker.consume()
        elif op != None and op == "master":
            db = DBHelper("localhost", 27017)
            total_num_of_tasks = 0
            
            for i in range(0, db.get_num_of_docs(), 1):
                start = datetime.now()
                start_time = timeit.default_timer()
                task = db.get_first_task()
                if task is None:
                    continue               
#                task = db.get_task_by_id('594582074186716deb086c24')
#                task = db.get_last_task()
#                test_time_range = {const.time_start_tag:"1999-01-01T00:00:19Z", const.time_end_tag:"2007-01-01T00:00:19Z"}
#                tasks = db.get_tasks_in_time_range(test_time_range)
#                task = tasks[0]   
                
                submitter = Submitter("localhost", 5672, "task_queue")
                num_of_nodes = submitter.get_number_of_consumers()                
                total_num_of_tasks_req = tasks_per_node * num_of_nodes
                if partition_type == "log":
                    sub_tasks = partitioner.partition_log(task, total_num_of_tasks_req)
                elif  partition_type == "linear":
                    sub_tasks = partitioner.partition_linear(task, total_num_of_tasks_req)

                num_of_tasks = 0
                for sub in sub_tasks:
                    try:
                        submitter.submitt_task(sub)
                    except pika.exceptions.ChannelClosed:
                        submitter = Submitter("localhost", 5672, "task_queue")
                        submitter.submitt_task(sub)
                    num_of_tasks += 1
                    total_num_of_tasks += 1
                
#                wait_for_output(num_of_tasks)
                
                
                db.mark_task_done(task)
                
                if total_num_of_tasks >= task_limit:
                    break
#            get_missed_deadlines(total_num_of_tasks)
        
        elif op != None and op == "monitor":
            mon = Monitor("localhost", 5672, "task_queue_done",list_of_nodes)
            mon.monitor(-1)
        elif op != None and op == "init_task":
            db = DBHelper("localhost", 27017)
            tasks = generate_tasks()
            print "Created %s tasks" % len(tasks)
            ranked_tasks = sch.rank_tasks(tasks)
            db.import_tasks(ranked_tasks)
            print "Imported %s tasks " % db.get_num_of_docs()
            print "execution_rank,Num. Of Params.,ttf,time_range_sec,Area"
            for task in ranked_tasks:
                util.print_task_stats(task)       
    
    
    
    
    
    
        
