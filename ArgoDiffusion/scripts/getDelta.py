#!/usr/bin/python

import sys
from datetime import datetime


start = sys.argv[1]
end = sys.argv[2]

start_date = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
end_date = datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")
delta = end_date-start_date
print delta.total_seconds()
