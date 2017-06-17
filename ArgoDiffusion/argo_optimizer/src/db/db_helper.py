import os
import pymongo
from pymongo import Connection
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir) 
from util.constants import *

class DBHelper:
    
    def __init__(self, host, port):
        self.connection = Connection(host, port)
        self.drip_db = self.connection.drip
        self.task_collection = self.drip_db["tasks"]
        self.const = Constants()
        self.task_collection.create_index([(self.const.execution_rank_tag, pymongo.DESCENDING)],
                                          unique=False)
    
    def import_tasks(self, tasks):
        self.task_collection.insert(tasks)
        
        
    def get_all_tasks(self):
        return self.task_collection.find({});
    
    def get_first_task(self):
        return self.task_collection.find_one(
    
                                             {"$or":[
                                             {self.const.executed_tag: {"$exists": False}},
                                             {self.const.executed_tag: {"$eq": False}}]}, 
                                             sort=[(self.const.execution_rank_tag, 1)])
            
    def delete_task(self, task):
        self.task_collection.delete(task)
        
    def mark_task_done(self, task):
        task[self.const.executed_tag] = True
        doc_id = task['_id']
        self.task_collection.update({'_id':doc_id}, task)
        
        
    def get_num_of_docs(self):
        return self.task_collection.count()