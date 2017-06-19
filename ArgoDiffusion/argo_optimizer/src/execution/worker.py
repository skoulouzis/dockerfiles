from datetime import datetime
from datetime import timedelta
import generation_argo_big_data
from generation_argo_big_data import *
import json
import pika
from pika import exceptions
import socket
import tempfile
from threading import Thread
import time
from time import sleep
import timeit
from util.util import *
import uuid


class Worker:
    
    def __init__(self, rabbit_host, rabbit_port, q_name):
        self.q_name = q_name
        self.rabbit_host = rabbit_host
        self.rabbit_port = rabbit_port
        self.conumer_tag = str(socket.gethostname()) + "_" + str(uuid.uuid4())
        try:
            self.init_connection()
        except exceptions.ConnectionClosed():
            self.init_connection()
        
        self.thread = Thread(target=self.threaded_function, args=(1, ))
        self.util = Util()
        self.argo = Argo()
        self.done = False
        self.done_count = 0
        
    
    def init_connection(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbit_host, port=int(self.rabbit_port)))
        self.channel = self.connection.channel()
        self.channel.confirm_delivery()
        self.channel.queue_declare(queue=self.q_name, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue=self.q_name, consumer_tag=self.conumer_tag)
#        self.queue_done = self.channel.queue_declare(queue='task_queue_done', durable=True)
        
    def execute(self, data):
        rand_name = self.util.randomword();
        rand_name = tempfile.gettempdir() + "/" + rand_name + ".json.out"
        with open(rand_name, 'w') as outfile:
            outfile.write(str(data))
            
        generation_argo_big_data.config_file = rand_name
        out = data
        out = self.argo.run()
        try:
            os.remove(rand_name)
        except OSError:
            pass
        return out


    def consume(self):
        self.thread.start()        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.done = True
            self.thread.join()
    
    def threaded_function(self, args):
        while not self.done:
            try:
                self.connection.process_data_events()
            except exceptions.ConnectionClosed():
                self.init_connection()
                self.connection.process_data_events()
            sleep(10)
            
    def callback(self, ch, method, properties, body):
        start_time = timeit.default_timer()
        n = str(body)
        response = self.execute(n)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        elapsed = timeit.default_timer() - start_time
        conf = json.loads(body)
        start = datetime.now()
        out = self.util.build_output(conf, elapsed, start, 1, str(socket.gethostname()), 1, None)
        self.send_done(out)
#        print out


    def send_done(self, response):
        message = response
        self.done_count += 1
        sent = self.channel.basic_publish(exchange='',
                                          routing_key='task_queue_done',
                                          body=message,
                                          properties=pika.BasicProperties(
                                          delivery_mode=2,
                                          ))
        while not(sent):
            self.done_count += 1
            sent = self.channel.basic_publish(exchange='',
                                              routing_key='task_queue_done',
                                              body=message,
                                              properties=pika.BasicProperties(
                                              delivery_mode=2,
                                              ))
                        
      
    