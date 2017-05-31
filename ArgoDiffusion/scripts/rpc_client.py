#!/usr/bin/env python
import pika
import uuid
import sys
import json

class ArgoRpcClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(parameters)

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, conf_file):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        with open(conf_file) as json_data:
            conf = json.load(json_data)
        conf_data  = json.dumps(conf)
        self.channel.basic_publish(exchange='',
                                   routing_key='argo_rpc_queue',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=str(conf_data))
        while self.response is None:
            self.connection.process_data_events()
        return str(self.response)


rabbit_host = sys.argv[1]
rabbit_port = sys.argv[2]
conf_file = sys.argv[3]

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, port=int(rabbit_port)))


argo_rpc = ArgoRpcClient()

response = argo_rpc.call(conf_file)
print response