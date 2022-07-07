#!/usr/bin/evn python3

'''
ucxlogparser

Using a Source or Destination channel from CDR records, determine the unique call identifier, extract all log lines related to that phone call, and add some coloring.

usage: ~/ucxlogparser.py <channel id to search for> </path/to/asterisk/fulllog>
example usage: $python3 ~/ucxlogparser.py UCX/204@204-00000000 ~/downloads/logs/full

author: senorwatsonsan@protonmail[.]com 
'''

import re
import sys

#"line signature - generic - 1" <timestamp> <verbose-id> <call-sn> <logdata> 
#Example: "[2022-07-03 12:20:03.980] VERBOSE[9849][C-00000003] pbx.c: Executing [s@macro-dialout-trunk:1] Set("UCX/204@204-00000002", "DIAL_TRUNK=11") in new stack"
lsgeneric1 = r"(?P<lsgencall>" \
        + "(?P<timestamp>\[\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\])." \
        + "(?P<vb>VERBOSE\[\d+\])" \
        + "(?P<callsn>\[C\-[0-9a-f]{8}])" \
        + "(?P<logdata>.*))"  
lsgen1 = re.compile(lsgeneric1)

#"line signature - generic - 2" <timestamp> <verbose-id> <logdata>
#Example: "[2022-07-03 12:20:03.960] VERBOSE[2406] chan_ucx.c: UCX/204@204-00000002 created for sub 0"
lsgeneric2 = r"(?P<lsgencall>" \
        + "(?P<timestamp>\[\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\])." \
        + "(?P<vb>VERBOSE\[\d+\])" \
        + "(?P<logdata>.*))"  
lsgen2 = re.compile(lsgeneric2)

#"line signature - play recording"
#Example: "[2022-07-03 12:20:27.229] VERBOSE[9884][C-00000004] file.c: <SIP/202-00000004> Playing 'vm-password.slin' (language 'en')"
lsplayrec = r"(?P<lsplayrec>" \
        + "(?P<timestamp>\[\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\])." \
        + "(?P<vb>VERBOSE\[\d{4,}\])" \
        + "(?P<callsn>\[C\-[0-9a-f]{8}\]).+" \
        + "(?P<playrec>Playing\s'[\w\/-]+?\.slin'\s\(language\s'\w{2}'\)))"
lsprc = re.compile(lsplayrec)

#"line signature - hanging up"
#Example: "[2022-07-03 12:20:35.443] VERBOSE[2406] chan_ucx.c: Hanging up UCX/204@204-00000002"
lshangup1 = r"(?P<lshangup>" \
        + "(?P<timestamp>\[\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\])\s" \
        + "(?P<vb>VERBOSE\[\d+\])\s" \
        + "(?P<asteriskc>\w+\.c:)\s" \
        + "(?P<hangup>Hanging\sup.+))"
lshu1 = re.compile(lshangup1)

#"line signature - ringing"
#Example: "[2022-07-03 12:21:38.604] VERBOSE[9993][C-00000005] app_dial.c: UCX/204@204-00000003 is ringing"
lsringing = r"(?P<lsringing>" \
        + "(?P<timestamp>\[\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\])\s" \
        + "(?P<vb>VERBOSE\[\d+\])" \
        + "(?P<callsn>\[C\-[0-9a-f]{8}])\s" \
        + "(?P<asteriskc>\w+\.c:)\s" \
        + "(?P<ringing>.+ringing))"
lsrin = re.compile(lsringing)

#"line signature - no answer"
#Example: "[2022-07-03 12:19:18.273] VERBOSE[9733][C-00000001] app_dial.c: Nobody picked up in 20000 ms"
lsnoans = r"(?P<lsnoans>" \
        + "(?P<timestamp>\[\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\])\s" \
        + "(?P<vb>VERBOSE\[\d+\])" \
        + "(?P<callsn>\[C\-[0-9a-f]{8}])\s" \
        + "(?P<asteriskc>\w+\.c:)\s" \
        + "(?P<noanswer>Nobody\spicked\sup\sin\s\d+\sms))"
lsnoa = re.compile(lsnoans)

#"line signature - call answered"
#Example: "[2022-07-03 12:20:05.646] VERBOSE[9849][C-00000003] app_dial.c: SIP/siptrunk-00000003 answered UCX/204@204-00000002"
lsansd = r"(?P<lsanswered>" \
        + "(?P<timestamp>\[\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\])\s" \
        + "(?P<vb>VERBOSE\[\d+\])" \
        + "(?P<callsn>\[C\-[0-9a-f]{8}])\s" \
        + "(?P<asteriskc>\w+?\.c:)\s" \
        + "(?P<answered>\w{3}\/\w+\-[0-9a-f]{8}\sanswered\s\w{3}\/\d{2,6}@\d{2,6}\-[0-9a-f]{8}))"
lsans = re.compile(lsansd)

#define regex pattern for call serial number to be "tracked"
#eight hex digits prefixed with "C-" and surrounded by brackets
#example: "[C-000017ed]"
re_callid = r'(?P<callsntr>\[C\-[0-9a-f]{8}])'
s = re.compile(re_callid)

#prep color codes
clrW = '\033[0m'  #white
clrR = '\033[31m' #red
clrG = '\033[32m' #green
clrO = '\033[33m' #orange
clrB = '\033[34m' #blue
clrP = '\033[35m' #purple

#enable incoming arguments
calldetail = sys.argv[1]
logfile = sys.argv[2]

#find a line with both the call detail being searched on, AND the call serial number (i.e. "[C-00012acf]".
#extract call serial number and save it
with open(logfile, 'rt') as file:
    for line in file:
        if calldetail in line:
            x = re.search(s, line) 
            if x != None: 
                linematch = line
                break
            else:
                continue
                #line has no Call ID tag. move to next line. 
    else:
        print("No matches found.")
        sys.exit()

#extract call serial number and save to "C"
m = re.search(s, linematch)
C = m.group('callsntr')

#find log lines with call serial number match to line type, and add appropriate coloring. 
with open(logfile, 'rt') as file:
    for line in file:
        lspr = re.match(lsprc, line)
        lsh1 = re.match(lshu1, line)
        lsrn = re.match(lsrin, line)
        lsna = re.match(lsnoa, line)
        lsan = re.match(lsans, line)
        lsg1 = re.match(lsgen1, line)
        lsg2 = re.match(lsgen2, line)
        if lspr != None and (C in line or calldetail in line): 
            print('{} {}{} {}'.format(
                    clrG+lspr.group('timestamp'), clrO+lspr.group('vb'), clrG+lspr.group('callsn'), clrR+lspr.group('playrec'))
                    ) 
        elif lsh1 != None and (C in line or calldetail in line): 
            print('{} {}{} {}'.format(
                    clrG+lsh1.group('timestamp'), clrO+lsh1.group('vb'), clrO+lsh1.group('asteriskc'), clrR+lsh1.group('hangup'))
                    ) 
        elif lsrn != None and (C in line or calldetail in line): 
            print('{} {}{} {} {}'.format(
                    clrG+lsrn.group('timestamp'), clrO+lsrn.group('vb'), clrG+lsrn.group('callsn') ,clrO+lsrn.group('asteriskc'), clrR+lsrn.group('ringing'))
                    ) 
        elif lsna != None and (C in line or calldetail in line): 
            print('{} {}{} {} {}'.format(
                    clrG+lsna.group('timestamp'), clrO+lsna.group('vb'), clrG+lsna.group('callsn') ,clrO+lsna.group('asteriskc'), clrR+lsna.group('noanswer'))
                    ) 
        elif lsan != None and (C in line or calldetail in line): 
            print('{} {}{} {} {}'.format(
                    clrG+lsan.group('timestamp'), clrO+lsan.group('vb'), clrG+lsan.group('callsn') ,clrO+lsan.group('asteriskc'), clrR+lsan.group('answered'))
                    ) 
        elif lsg1 != None and (C in line or calldetail in line):
            print('{} {}{}{}'.format(
                    clrG+lsg1.group('timestamp'), clrO+lsg1.group('vb'), clrG+lsg1.group('callsn'), clrO+lsg1.group('logdata'))
                    )
        elif lsg2 != None and (C in line or calldetail in line):
            print('{} {}{}'.format(
                    clrG+lsg2.group('timestamp'), clrO+lsg2.group('vb'), clrO+lsg2.group('logdata'))
                    )
        else:
            continue
