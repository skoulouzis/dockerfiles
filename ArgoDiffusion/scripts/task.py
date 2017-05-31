#!/usr/bin/env python
import pika
import sys
import uuid
import sys
import json


rabbit_host = sys.argv[1]
rabbit_port = sys.argv[2]
conf_file = sys.argv[3]

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, port=int(rabbit_port)))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)

with open(conf_file) as json_data:
    conf = json.load(json_data)
message  = json.dumps(conf)

channel.basic_publish(exchange='',
                      routing_key='task_queue',
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
#print(" [x] Sent %r" % message)
connection.close()


