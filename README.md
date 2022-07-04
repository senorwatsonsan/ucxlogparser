# ucxlogparser
Python script for extracting and colorizing call-specific info from the /var/log/asterisk/full logfile. 

Using a Source or Destination channel from CDR records, determine the unique call identifier, extract all log lines related to that phone call, and add some coloring.

usage: ~/ucxlogparser.py <channel id to search for> </path/to/asterisk/fulllog>
example usage: $python3 ~/ucxlogparser.py UCX/204@204-00000000 ~/Documents/clients/AcmeFireworks/full
