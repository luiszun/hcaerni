# hcaerni
Scripts and utilities that allow you to get some other information on your Garmin InReach through messages.

daemon.py (not really a daemon) should be called every now and then (I suggest every minute) with a cron job or equivalent.

Needs Python's requests
python -m pip install requests

Configure:
Change the hostname,username,password values in body_parser.py