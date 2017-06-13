#!/usr/bin/python

#Code from https://stackoverflow.com/questions/16188912/get-total-number-of-consumers-for-a-rabbitmq-queue-using-pika. Added q name 

import subprocess
import os
import json
import sys

#Execute in command line
def execute_command(command,queue_name):
     proc = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE) 
     script_response = proc.stdout.read()
     resp=json.loads(script_response)
     for q in resp:
         if q['name'] == queue_name:
             print q['consumers']

######### MAIN #########
if __name__ == '__main__':
    host =  sys.argv[1]
    port =  sys.argv[2]
    queue_name = sys.argv[3]
    cmd = "curl -s -u guest:guest http://"+host+":"+port+"/api/queues/"
    execute_command(cmd,queue_name)