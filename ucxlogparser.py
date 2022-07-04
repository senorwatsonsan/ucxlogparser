#!/usr/bin/evn python3

'''
ucxlogminer

Using a Source or Destination channel from CDR records, determine the unique call identifier, extract all log lines related to that phone call, and add some coloring.

usage: $python3 ~/ucxlogparser.py <channel id to search for> </path/to/asterisk/fulllog>
example usage: $python3 ~/ucxlogparser.py UCX/204@204-00000000 ~/Documents/clients/AcmeFireworks/full

author: senorwatsonsan@protonmail[.]com 
'''

import re
import sys

#"line signature - generic - 1" <timestamp> <verbose-id> <call-sn> <logdata> 
lsgeneric1 = r"(?P<lsgencall>" \
        + "(?P<timestamp>\[\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\])." \
        + "(?P<vb>VERBOSE\[\d+\])" \
        + "(?P<callsn>\[C\-[0-9a-f]{8}])" \
        + "(?P<logdata>.*))"  
lsgen1 = re.compile(lsgeneric1)

#"line signature - generic - 2" <timestamp> <verbose-id> <logdata>
lsgeneric2 = r"(?P<lsgencall>" \
        + "(?P<timestamp>\[\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\])." \
        + "(?P<vb>VERBOSE\[\d+\])" \
        + "(?P<logdata>.*))"  
lsgen2 = re.compile(lsgeneric2)

#"line signature - play recording"
lsplayrec = r"(?P<lsplayrec>" \
        + "(?P<timestamp>\[\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\])." \
        + "(?P<vb>VERBOSE\[\d{4,}\])" \
        + "(?P<callsn>\[C\-[0-9a-f]{8}\]).+" \
        + "(?P<playrec>Playing\s'[\w\/-]+?\.slin'\s\(language\s'\w{2}'\)))"
lsprc = re.compile(lsplayrec)

#"line signature - hanging up"
lshangup1 = r"(?P<lshangup>" \
        + "(?P<timestamp>\[\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\])\s" \
        + "(?P<vb>VERBOSE\[\d+\])\s" \
        + "(?P<asteriskc>\w+\.c:)\s" \
        + "(?P<hangup>Hanging\sup.+))"
lshu1 = re.compile(lshangup1)

#"line signature - ringing"
lsringing = r"(?P<lsringing>" \
        + "(?P<timestamp>\[\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\])\s" \
        + "(?P<vb>VERBOSE\[\d+\])" \
        + "(?P<callsn>\[C\-[0-9a-f]{8}])\s" \
        + "(?P<asteriskc>\w+\.c:)\s" \
        + "(?P<ringing>.+ringing))"
lsrin = re.compile(lsringing)

#"line signature - no answer"
lsnoans = r"(?P<lsnoans>" \
        + "(?P<timestamp>\[\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\])\s" \
        + "(?P<vb>VERBOSE\[\d+\])" \
        + "(?P<callsn>\[C\-[0-9a-f]{8}])\s" \
        + "(?P<asteriskc>\w+\.c:)\s" \
        + "(?P<noanswer>Nobody\spicked\sup\sin\s\d+\sms))"
lsnoa = re.compile(lsnoans)

#"line signature - call answered"
lsansd = r"(?P<lsanswered>" \
        + "(?P<timestamp>\[\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\])\s" \
        + "(?P<vb>VERBOSE\[\d+\])" \
        + "(?P<callsn>\[C\-[0-9a-f]{8}])\s" \
        + "(?P<asteriskc>\w+\.c:)\s" \
        + "(?P<answered>\w{3}\/\w+-[0-9a-f]{8}\sanswered\s\w{3}\/\w+-[0-9a-f]{8}))"
lsans = re.compile(lsansd)

#define regex pattern for call serial number to be "tracked"
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

#
m = re.search(s, linematch)
C = m.group('callsntr')

#determine which type of log line signature matches, and add appropriate coloring. 
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
