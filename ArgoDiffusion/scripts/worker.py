#!/usr/bin/env python
import pika
import time
import generation_argo_big_data
from generation_argo_big_data import *
import tempfile
import random, string
from threading import Thread
from time import sleep

done = False
def threaded_function(args):
    while not done:
        connection.process_data_events()
        sleep(5)
        
        
def randomword():
   return ''.join(random.choice(string.lowercase) for i in range(5))

def execute(data):
    tempfile.gettempdir() 
    f = tempfile.NamedTemporaryFile(delete=False)
    rand_name = randomword();
    rand_name+=".json.out"
    with open(rand_name, 'w') as outfile:
        outfile.write(str(data))
    
    generation_argo_big_data.config_file = rand_name
    argo = Argo()
    out = argo.run()
    return out


def callback(ch, method, properties, body):
    n = str(body)
    response = execute(n)
    #print response
    ch.basic_ack(delivery_tag = method.delivery_tag)




rabbit_host = sys.argv[1]
rabbit_port = sys.argv[2]
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, port=int(rabbit_port)))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)

thread = Thread(target = threaded_function, args = (1, ))
#thread.start()


channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,queue='task_queue')

try:
    channel.start_consuming()
except KeyboardInterrupt:
    #thread.stop()
    done = True
    thread.join()
    print "threads successfully closed"