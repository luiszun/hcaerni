#!/usr/bin/env python3

from src.body_parser import ParseAndTriage
from src.mailmod import GetOneEmailBody

while True:
    message, From = GetOneEmailBody()
    if message == "":
        break
    for body in message:
        try:
            ParseAndTriage(body, From)
        except ValueError:
            print("Caught exception " + ValueError)
