#-*- encoding: utf-8 -*-
import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.Utils import formatdate
from email.MIMEText import MIMEText


# create function for sending mail(set needed value of arguments by default)
def send_email(_to="motmomtest@motmom.com", _from="test@test.com",
               letter_number=1):
    HOST = 'localhost'
    msg = MIMEMultipart('mixed', 'multipart')

    msg["From"] = _from
    msg["To"] = _to
    msg["Subject"] = u"Test chain from localhost 1"
    msg['Date'] = formatdate(localtime=True)

    mail_html = MIMEText("Test letter {0}.".format(letter_number))
    msg.attach(mail_html)

    server = smtplib.SMTP(HOST)

    # send letter, if successful then print confirm message
    try:
        server.sendmail(_from, _to, msg.as_string())
        server.close()
        print "Letter {0} was sent.".format(letter_number)
    # if something wrong, print error message
    except Exception, e:
        error_msg = "Unable to send letter.\nError: %s" % str(e)
        print error_msg

if __name__ == "__main__":
    for number in xrange(1, 5):
        send_email(letter_number=number)
