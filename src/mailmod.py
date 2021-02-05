import imaplib
import smtplib
import email
from email.header import decode_header
import webbrowser
import os
from email.mime.text import MIMEText

# account credentials
hostname = "mail.luiszun.com"
username = "nwac@anxiousmountaineer.com"
password = "IAmNotThatDumbIThink"

def GetOneEmailBody():
    
    def clean(text):
        # clean text for creating a folder
        return "".join(c if c.isalnum() else "_" for c in text)
    
    # create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL(hostname)
    # authenticate
    imap.login(username, password)    
    
    imap.select("INBOX")
    status, messages = imap.search(None, '(UNSEEN)')
    
    # The cached bodies
    bodies = []
    From = ""
    
    ids = messages[0].split()
    if len(ids) == 0:
        return "", ""
    id = ids[0]
    # fetch the email message by ID
    res, msg = imap.fetch(id, "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            # decode the email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode(encoding)
            # decode email sender
            From, encoding = decode_header(msg.get("From"))[0]
            From = email.utils.parseaddr(From)

            # Force to select at least something? If a name is included the 2nd is the good one
            if len(From) > 1:
                From = From[1]
            else:
                From = From[0]

            if isinstance(From, bytes):
                From = From.decode(encoding)
            print("Subject:", subject)
            print("From:", From)
            # if the email message is multipart
            if msg.is_multipart():
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        # get the email body
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        # print text/plain emails and skip attachments
                        print(body)
                        bodies.append(body)
            else:
                # extract content type of email
                content_type = msg.get_content_type()
                # get the email body
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    # print only text email parts
                    print(body)
                    bodies.append(body)
            print("="*100)
    # close the connection and logout
    imap.close()
    imap.logout()

    # Let's make sure we never discard or misread messages due to casing
    lowerCaseBodies = []
    for s in bodies:
        lowerCaseBodies.append(s.lower())

    return lowerCaseBodies, From
    
def SendMail(body, to):
    smtp_ssl_port = 587 
    targets = [to]

    msg = MIMEText(body)
    msg["Subject"] = "Avalanche Forecast"
    msg['From'] = username 
    msg['To'] = to

    server = smtplib.SMTP(hostname, smtp_ssl_port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username, password)
    server.sendmail(username, [to], msg.as_string())
    server.quit()