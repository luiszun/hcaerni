# hcaerni
Scripts and utilities that allow you to get some other information on your Garmin InReach through messages.

daemon.py (not really a daemon) should be called every now and then (I suggest every minute) with a cron job or equivalent.

# Install

Clone, setup a virtualenv, and install requirements

```
mkvirtualenv --python=`which python3` -a $(pwd) hcaerni
pip install -r requirements.txt
```

# Configure:
Change the hostname,username,password values in mailmod.py

# Run:

Activate your virtualenv, and then run `hcaerni/daemon.py`