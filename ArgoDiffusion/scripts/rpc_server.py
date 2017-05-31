#!/usr/bin/env python
import pika
import generation_argo_big_data
from generation_argo_big_data import *
import tempfile
import random, string
from threading import Thread

rabbit_host = sys.argv[1]
rabbit_port = sys.argv[2]

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, port=int(rabbit_port)))

channel = connection.channel()

channel.queue_declare(queue='argo_rpc_queue')

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

def on_request(ch, method, props, body):
    n = str(body)
    response = execute(n)    
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='argo_rpc_queue')

thread = Thread(target = threaded_function, args = (1, ))
thread.start()

try:
    channel.start_consuming()
except KeyboardInterrupt:
    #thread.stop()
    done = True
    thread.join()
    print "threads successfully closed"
    