from mailmod import GetEmailBodies
from body_parser import FindMapShare, ParseAndTriage

messages = GetEmailBodies()
for m in messages:
    share = ParseAndTriage(m)