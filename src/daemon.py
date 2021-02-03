from mailmod import GetOneEmailBody
from body_parser import FindMapShare, ParseAndTriage

while True:
    message = GetOneEmailBody()
    if message == "":
        break
    for body in message:
        ParseAndTriage(body)
