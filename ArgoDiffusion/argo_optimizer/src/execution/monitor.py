from datetime import datetime
from datetime import timedelta
from db.db_helper import *
import json
import linecache
import pika
from pika import exceptions
import requests
from requests.auth import HTTPBasicAuth
import socket
from util.constants import *
from util.util import *
import uuid
import subprocess

class Monitor:
    
    def __init__(self, rabbit_host, rabbit_port, q_name, list_of_nodes):
        self.q_name = q_name
        self.rabbit_port = rabbit_port
        self.num_of_meesages = 0
        self.rabbit_host = rabbit_host
        self.user = 'guest'
        self.password = 'guest'
        self.rest_api_port = "15672"
        
        self.conumer_tag = str(socket.gethostname()) + "_" + str(uuid.uuid4())
        self.init_connection()
            
        self.const = Constants()
        self.util = Util()
        self.last_exec_date = datetime(10, 1, 1)
        self.finised_tasks = {}
        self.db = DBHelper("localhost", 27017)
        self.list_of_nodes = list_of_nodes
        self.node_index = 2
        self.threshold = 100
        self.max_nodes = self.util.get_num_of_lines_in_file(self.list_of_nodes)
        
    def init_connection(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbit_host, port=int(self.rabbit_port)))
        self.channel = self.connection.channel()
        self.channel.confirm_delivery()
        self.channel.queue_declare(queue=self.q_name, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue=self.q_name, consumer_tag=self.conumer_tag)

        
    def get_q_size(self):
        q = self.get_q()
        return int(q['messages'])

    def get_idle_since(self):
        q = self.get_q()
        if 'idle_since' in q:
            return datetime.strptime(q['idle_since'], self.const.date_format)  

    def get_q(self):
        url = "http://" + self.rabbit_host + ":" + self.rest_api_port + "/api/queues/"
        response = requests.get(url, auth=HTTPBasicAuth(self.user, self.password))
        if response.status_code == 200:
            for doc in response.json():
                if doc['name'] == self.q_name:
                    return doc
                    
    
    def delete_q(self):
        self.channel.queue_delete(queue=self.q_name)
        
        
    def callback(self, channel, method, properties, body):
        channel.basic_ack(delivery_tag=method.delivery_tag)
        resp = {}
        resp = json.loads(str(body))
        if 'date' in resp:
            key = 'date'
        elif 'execution_date' in resp:
            key = 'execution_date' 
        exec_date = datetime.strptime(resp[key], self.const.date_format)
        if exec_date > self.last_exec_date:
            self.last_exec_date = exec_date
        
        _id = resp['configuration']['_id']
        sub_tasks = []
        sub_tasks.append(resp)
        task = self.db.get_task_by_id(_id)
        out = self.util.build_deadline_output(task, sub_tasks)        
        print json.dumps(out)
        time_to_deadline = int(out['time_to_deadline'])
        if time_to_deadline <= self.threshold:
            self.provision_worker()
        
        if self.num_of_meesages > 0:
            self.num_of_meesages -= 1
            if self.num_of_meesages <= 0:
                channel.close()
                return
           
        
    def monitor(self, num_of_meesages):
        self.num_of_meesages = num_of_meesages
        self.channel.start_consuming()
        
    def get_number_of_consumers(self):
        q = self.get_q()
        return int(q['consumers'])
    
    def provision_worker(self):
        line = linecache.getline(self.list_of_nodes, self.node_index)
        line = line.rstrip()        
        cmd = "screen -L -dmS rabbit_worker python ~/workspace/dockerfiles/ArgoDiffusion/argo_optimizer/src/argo_optimizer.py worker 147.228.242.1 5672"
        subprocess.call(cmd, shell=True)
        self.node_index += 1
        if self.node_index > self.max_nodes:
            print "reset index"
            self.node_index = 1
        