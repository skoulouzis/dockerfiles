from datetime import date
from datetime import datetime
from datetime import timedelta
from util.constants import *
from util.util import *

class Scheduler:
    
    def __init__(self):
        self.const = Constants()
        self.util = Util()
        self.params_len_weight = 0
        self.ttf_weight = 0.1
        self.time_range_weight = 1
        self.area_weight = 0.2
        self.now = datetime.now()
    
    def rank_tasks(self, tasks):
        ranked_tasks = []
        for task in tasks:
            ranked_task = self.get_task_rank(task)
            ranked_tasks.append(ranked_task)
        return ranked_tasks

    def get_task_rank(self, task):
        params_len = len(task[self.const.parameters_tag])
        ttf = self.util.get_time_delta(self.now, task[self.const.deadline_date_tag])
        ttf_sec = ttf.total_seconds()
        time_range = self.util.get_time_delta(task[self.const.time_tag][self.const.time_start_tag], 
                                                task[self.const.time_tag][self.const.time_end_tag])
        time_range_sec = time_range.total_seconds()
        area = self.util.get_area(task[self.const.bounding_box_tag])
        
        params_comp = (float(params_len) * self.params_len_weight)
        deadline_comp = (float(ttf_sec) * self.ttf_weight)
        time_range_comp = (float(time_range_sec) * self.time_range_weight)
        area_comp = (float(area) * self.area_weight)


        urgency = params_comp + deadline_comp + time_range_comp + area_comp
        execution_rank = 1 / float(urgency)
        task[self.const.execution_rank_tag] = execution_rank
        return task