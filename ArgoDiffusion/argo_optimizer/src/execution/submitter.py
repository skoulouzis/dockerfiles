from datetime import datetime
from datetime import timedelta
import json
import pika
import requests
from requests.auth import HTTPBasicAuth
from util.constants import *
from util.util import *


class Submitter:
    
    def __init__(self, rabbit_host, rabbit_port, q_name):
        self.q_name = q_name
        self.num_of_meesages = 0
        self.rabbit_host = rabbit_host
        self.user = 'guest'
        self.password = 'guest'
        self.rest_api_port = "15672"
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, port=int(rabbit_port)))
        self.channel = self.connection.channel()
        self.queue = self.channel.queue_declare(queue=q_name, durable=True)
        self.const = Constants()
        self.util = Util()
        self.last_exec_date = datetime(10, 1, 1)
        
        
    
    def submitt_task(self, task):
        task = self.util.convert_dates_to_string(task)
        task = self.util.uid_to_string(task)
        message = json.dumps(task)
        self.channel.basic_publish(exchange='',
                                   routing_key=self.q_name,
                                   body=message,
                                   properties=pika.BasicProperties(
                                   delivery_mode=2, # make message persistent
                                   ))


        
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
                    
                    
                    
#    def get_q_size(self):
#        res = self.channel.queue_declare(
##                                         callback=self.print_callback,
#                                         queue=self.q_name,
#                                         durable=True,
#                                         exclusive=False,
#                                         auto_delete=False,
#                                         passive=True
#                                         )
#        return res.method.message_count



    def delete_q(self):
        self.channel.queue_delete(queue=self.q_name)
        
        
    def callback(self, channel, method, properties, body):
        channel.basic_ack(delivery_tag=method.delivery_tag)
        resp = json.loads(str(body))
        exec_date = datetime.strptime(resp['date'], self.const.date_format)
        if exec_date > self.last_exec_date:
            self.last_exec_date = exec_date
             
        self.num_of_meesages -= 1
        if self.num_of_meesages <= 0:
            channel.close()
            return
        
        
    def listen(self, num_of_meesages):
        self.num_of_meesages = num_of_meesages 
        self.channel.basic_consume(self.callback, queue=self.q_name)
        self.channel.start_consuming()
#        try:
#            queue_state = self.channel.queue_declare(self.q_name, durable=True, passive=True)
#            queue_empty = queue_state.method.message_count == 0
#            if not queue_empty:
#                method, properties, body = self.channel.basic_get(queue, no_ack=True)
#                self.callback_func(channel, method, properties, body)
#        finally:
#            self.channel.close()
        
    def get_number_of_consumers(self):
        q = self.get_q()
        return int(q['consumers'])