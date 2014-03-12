# coding: utf-8
import os
import smtplib

from email import Encoders
from email.MIMEMultipart import MIMEMultipart
from email.Utils import formatdate
from email.MIMEImage import MIMEImage
from email.MIMEBase import MIMEBase

# declare resources system paths for attachments
# attach this script
file_path = r'resume_mail_sender.py'
# attach photo
image_path = r'my_photo.gif'
# attach resume
html_path = r'resume.html'


# create function for sending mail(set needed value of arguments by default)
def send_email(_to="some-email@gmail.com",
               _from="my-email@mail.ru"):
    # declare self as host
    HOST = 'localhost'

    # create intermediate base class for MIME message
    msg = MIMEMultipart('mixed', 'multi_outer')

    # form headers of letter(from, to, subject, date)
    msg["From"] = _from
    msg["To"] = _to
    msg["Subject"] = u"Резюме на должность веб-разработчика."
    msg['Date'] = formatdate(localtime=True)

    # attach a text to the letter
    mail_text = MIMEBase('text', 'plain', charset='utf-8')
    mail_text.set_payload('Резюме: Дыкин Сергей Александрович')
    Encoders.encode_base64(mail_text)
    msg.attach(mail_text)

    # create intermediate base class for MIME message inside another one
    msg_inside = MIMEMultipart('alternative', 'multi_inner')
    msg.attach(msg_inside)

    # attach embedded a image(photo) to the letter
    attached_image = open(image_path, "rb")
    attached_image = MIMEImage(attached_image.read())
    attached_image.add_header('Content-Disposition', 'inline;" +\
                           " filename="%s"' % os.path.basename(image_path))
    attached_image.add_header('Content-ID', '<photo>')
    msg_inside.attach(attached_image)

    # attach a html-file to the letter
    mail_html = MIMEBase('text', 'html', charset='utf-8')
    mail_html.set_payload(open(html_path, "rb").read())
    Encoders.encode_base64(mail_html)
    msg_inside.attach(mail_html)

    # attach a text-file(with program code) to the letter
    part = MIMEBase('application', 'octet-stream')
    attached_file = open(file_path, "rb")
    part.set_payload(attached_file.read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition',
                    'attachment; filename="%s"' % os.path.basename(file_path))
    msg.attach(part)

    # create SMTP connection
    server = smtplib.SMTP(HOST)

    # send letter, if successful then print confirm message
    try:
        failed = server.sendmail(_from, _to, msg.as_string())
        server.close()
        print "Letter was sent."
    # if something wrong, print error message
    except Exception, e:
        error_msg = "Unable to send letter.\nError: {0}".format(str(e))
        print error_msg

# test mode
if __name__ == "__main__":
    # call function for sending email with default adresses
    send_email()
