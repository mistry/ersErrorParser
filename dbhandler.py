#!/usr/bin/python

import argparse
import json
import getsb
import sqlite3
from collections import namedtuple
from dateutil import parser as dateparser

Entry = namedtuple("Entry",["date","severity", "msgID","application","host","text","sb","sb_total_time","sb_time_run","sb_length","run","gh"])

def add_to_db(runs, beg_sb, end_sb, log_file):
    
    data = [] 
    entries = []
    ind = 0
    run = 0

    with open(log_file, 'r') as json_file:
        try:
            data = json.load(json_file)
        except ValueError as error:
            print('invalid JSON: %s' % error)

            print '''
            Check that your JSON is in the a correct format, https://jsonlint.com/
            
            JSON file downloaded from Web ERS is in wrong format. You need to add:

             1. '[' character at beginning of file
             2. ']' character at end of file
             3. ',' character after every line except the last line

             To do this (semi-efficiently) in vim, in command mode


             1. vim file.json      -- Open file
             2. :%s/$/,/g          -- This adds a ',' to the last line which we don't want. but don't worry. :)
             3. SHIFT + g + $      -- At this point your cursor should be over the end of the file (last line's ',')
             4. r then ']'         -- Replaces the comma with ']'
             5. :0                 -- Now should be at first character of line
             6. SHIFT + i then '[' -- Inserts before the '[' character
             7. :x                 -- Write and quit vim

            '''
            return False
    
    #iterate through json, line looks like
    #{u'preview': False, u'result': {u'sev': u'INFO', u'chained': u'0', u'msgID': u'TRT::ROD05Module', u'time': u'23:33:41 Sep 23 2018', u'application': u'TRTEndcapC_E-05', u'host': u'sbc-trt-rcc-e-05', u'text': u"ROD 340d02: An event didn't pass majority: 24 chips reported", u'gh': u'993251029'}}

   
    db = sqlite3.connect('db_errors.sqlite', sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

    try:
        most_recent = db.execute("SELECT date from entries order by date desc limit 1")
        most_recent = dateparser.parse(most_recent.fetchone()[0])
    except Exception:
        most_recent = False
    for line in reversed(data):
        date  = dateparser.parse(line['result']['time'])
        sev   = line['result']['sev']
        msgID = line['result']['msgID']
        app   = line['result']['application']
        host  = line['result']['host']
        text  = line['result']['text']
        bit   = 0
        gh    = line['result']['gh']

        if most_recent and date <= most_recent:
            continue

        while beg_sb[ind] <= date and bit == 0:
            if beg_sb[ind] <= date and date <= end_sb[ind]:
                bit = 1 
            elif end_sb[ind] < date and ind != len(beg_sb)-1 and date < beg_sb[ind+1]:
                break
            elif ind != len(beg_sb)-1:
                ind += 1 
            elif end_sb[ind] < date:
                break
        
        hours = 0.0 
        sb_length = 0.0 
        hours_run = 0.0
        if bit == 1:
            sbl = end_sb[ind] - beg_sb[ind]
            sb_length = sbl.days*24 + (sbl.seconds/3600.0)
            for i in range(ind):
                diff = end_sb[i] - beg_sb[i]
                hours = hours + diff.days*24 + (diff.seconds/3600.0)
            diff_run = date - beg_sb[ind]
            run = runs[ind]
            hours_run  = diff_run.days*24 + (diff_run.seconds/3600.0)
            hours = hours + hours_run


        hours = round(hours, 2)
        hours_run = round(hours_run, 2)
        sb_length = round(sb_length, 2)
        entries.append(Entry(date, sev, msgID, app, host, text, bit, hours, hours_run, sb_length, run ,gh))

    c = db.cursor()
    c.executemany("INSERT OR IGNORE INTO entries"\
                  "(date,severity,msgID,application,host,text,sb,sb_total_time,sb_time_run,sb_length,run,gh)"\
                  " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", entries)
    db.commit()
    db.close()
    print "Done: Added entries " + repr(len(entries)) + " to database!"
    return True 

def get_query(non_sb, text_filter, date_beg, date_end):
    
    db = sqlite3.connect('db_errors.sqlite', sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    #Looks like : Entry = namedtuple("Entry",("date","severity", "msgID","application","host","text","sb","sb_total_time","sb_time_run","sb_length","run","gh"))
    command = ("SELECT * FROM entries WHERE sb = " +str(int(not non_sb)) + " " + 
               "AND text LIKE '%"+text_filter+"%' " +
               "AND date >= '" + date_beg + "' "  +
               "AND date <= '" + date_end + "' "  +
               "ORDER BY date;")

    print "\nQUERY: " + command
    c = db.execute(command)
    return [Entry(*val) for val in c.fetchall()]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Error Analysis for TRT logs, input grafana mu dumps and ers log.')
    parser.add_argument('-d', '--dir', dest='dir', default='2018', type=str,  help="Directory of grafana mu dumps")
    parser.add_argument('-f', '--file', dest='log_file', default='', type=str, help="Log file from ERS.")

    args = parser.parse_args()

    if args.log_file != '':
        runs, beg_sb, end_sb = getsb.get_sb_list(False)
        add_to_db(runs, beg_sb, end_sb, args.log_file)
