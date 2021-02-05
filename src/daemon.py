from mailmod import GetOneEmailBody
from body_parser import FindMapShare, ParseAndTriage

while True:
    message, From = GetOneEmailBody()
    if message == "":
        break
    for body in message:
        try:
            ParseAndTriage(body, From)
        except ValueError:
            print ("Caught exception "+ValueError)
