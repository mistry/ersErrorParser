#!/usr/bin/python

import os
import argparse
from dateutil import parser as dateparser
from dateutil.relativedelta import relativedelta

def get_sb_list(print_sb):
    
    # get file names from directory and order them by date

    runs = [] 
    run_beg = [] 
    sb_beg = [] 
    sb_end = [] 
    with open('sbtimes/sbtimes.txt') as f:
        lines = f.readlines()
        for line in lines:
            line = line.split(';')
            runs.append(line[0])
            run_beg.append(dateparser.parse(line[1]) + relativedelta(hours=2))
            sb_beg.append(dateparser.parse(line[2]) + relativedelta(hours=2))
            sb_end.append(dateparser.parse(line[3].rstrip('\n')) + relativedelta(hours=2))

    if len(sb_beg) > len(sb_end):
        print 'adding last line to sb end'
        end.append(end_time)

    h = 0
    if print_sb:
        for x,y in zip(sb_beg, sb_end):
            diff = y - x 
            h = h +  diff.days*24 + (diff.seconds/3600.0)
            print x,y, h 

    return runs, sb_beg, sb_end

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to get sb times from grafana files, input grafana mu dumps')
    parser.add_argument('-s', '--print_sb', dest='print_sb', default=False, action='store_true', help="print sb times")
    args = parser.parse_args()
    get_sb_list(args.print_sb)
