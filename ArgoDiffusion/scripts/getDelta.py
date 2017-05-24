#!/usr/bin/python

import sys
from datetime import datetime



def calculateDatesDelta(start, end):
    start_date = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
    end_date = datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")
    delta = end_date-start_date
    return delta.total_seconds()
    
    
if __name__ == '__main__':
    start = sys.argv[1]
    end = sys.argv[2]
    print calculateDatesDelta(start,end);
