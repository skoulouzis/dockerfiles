from datetime import datetime, timedelta
from util.constants import *
from util.util import *


class Partitioner:
    
    def __init__(self):
        self.const = Constants()
        self.util = Util()
        
    def partition_linear(self, task, num_of_tasks):
        partitioned_tasks = []
        start_date = task[self.const.time_tag][self.const.time_start_tag]
        end_date = task[self.const.time_tag][self.const.time_end_tag]
        problem_size = self.util.get_time_delta(start_date, end_date)
        problem_size = problem_size.total_seconds()
        chunk_size = (problem_size) // (num_of_tasks)
        start_chunk = start_date
        for i in range(0, int(problem_size), int(chunk_size + 1)):
            
            end = i + chunk_size
            if end > problem_size:
                end = problem_size
            
            end_chunk = start_chunk + timedelta(seconds=end)
            if end_chunk > end_date:
                end_chunk = end_date
            sub_task = {}
            sub_task = self.create_time_range_configuration(start_chunk, end_chunk, task)
            partitioned_tasks.append(sub_task)            
            start_chunk = end_chunk
        return partitioned_tasks        
    
    
    def partition_log(self, task, num_of_tasks):
        partitioned_tasks = []
        start_date = task[self.const.time_tag][self.const.time_start_tag]
        end_date = task[self.const.time_tag][self.const.time_end_tag]
        problem_size = self.util.get_time_delta(start_date, end_date)
        problem_size = problem_size.total_seconds()
        chunk_size = problem_size
        start_chunk = start_date
        end_chunk = None
        for i in range(0, int(num_of_tasks), 1):
            chunk_size = (chunk_size) // (1.2)
            if chunk_size <= 0:
                break
            
            end_chunk = start_chunk + timedelta(seconds=chunk_size)
            sub_task = self.create_time_range_configuration(start_chunk, end_chunk, task)
            partitioned_tasks.append(sub_task)
            if (i >= num_of_tasks-1) and end_chunk < end_date:
                end_chunk = end_date
                sub_task = self.create_time_range_configuration(start_chunk, end_chunk, task)
                del partitioned_tasks[-1]
                partitioned_tasks.append(sub_task)
            start_chunk = end_chunk
        
        return partitioned_tasks

    def create_time_range_configuration(self, time_coverage_start, time_coverage_end, task):
        new_task = {}
        new_task = task.copy()
        time_range = {}
        time_range[self.const.time_start_tag] = time_coverage_start
        time_range[self.const.time_end_tag] = time_coverage_end
        new_task[self.const.time_tag] = time_range
        return new_task    