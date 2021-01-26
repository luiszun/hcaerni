import re
from mailmod import SendMail

def FindMapShare(body):
    share = re.findall('http[s]?://.*anxiousmountaineer\.com', body)
    if len(share) > 0:
        return share[0] 
    return ""


def ParseAndTriage(body):
    firstLine = body.partition('\n')[0]
    lineSplit = firstLine.split(' ')

    # Check to see if this is a test - example
    # "test luis@luiszun.com"
    # This would try to read the mapshare link from the body and send an email with it to luis@luiszun.com
    # Serves to verify that the body structure of the email hasn't changed or that it can still be parsed.
    if lineSplit[0] == 'test' and len(lineSplit) > 1:
        share = FindMapShare(body)
        if share != "":
            message = "Success: parsed the MapShare link to be: " + share
            SendMail(message, lineSplit[1].rstrip())


