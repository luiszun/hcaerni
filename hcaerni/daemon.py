#!/usr/bin/env python3

from src.body_parser import ParseAndTriage
from src.mailmod import EmailHandler

# account credentials
hostname = "mail.luiszun.com"
username = "nwac@anxiousmountaineer.com"
password = "IAmNotThatDumbIThink"

ep = EmailHandler(hostname=hostname, username=username, password=password)

while True:
    message, From = ep.GetOneEmailBody()
    if message == "":
        break
    for body in message:
        try:
            ParseAndTriage(body, From, ep)
        except ValueError:
            print("Caught exception " + ValueError)
