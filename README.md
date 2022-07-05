# ucxlogparser
Python script for extracting and colorizing call-specific info from the /var/log/asterisk/full logfile. 

Using a Source or Destination channel from CDR records, determine the unique call identifier, extract all log lines related to that phone call, and add some coloring.



example usage: $python3 ~/ucxlogparser.py UCX/204@204-00000000 ~/downloads/logs/full
