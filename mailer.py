import os
import sys
import smtplib  
from pymongo import MongoClient
from datetime import date
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

file_dir = os.path.dirname(__file__)
print file_dir
env = Environment(loader=FileSystemLoader(os.path.join(file_dir, 'templates')))
template = env.get_template('basic_mail.txt')
html_template = env.get_template('html_mail_inlined.html')

client = MongoClient('localhost', 27017)

db = client.goal
now = date.today()

APP_PASS = os.environ.get('GOOGLE_APP_PASS', None);
GMAIL_USERNAME = 'justin.donato@gmail.com'
SUBJECT = 'Daily Balance'

users = db.users.find()

def send_msg(user):

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    session.login(GMAIL_USERNAME, APP_PASS)

    msg = make_msg(user)
    msg = msg.as_string()

    email_address = user.get('email')

    print "Message for %s: %s" % (email_address, msg.replace('\n', ''))

    try:
        session.sendmail(GMAIL_USERNAME, email_address, msg)
    except smtplib.SMTPRecipientsRefused:
        print "Could not send message to %s" % email_address

    session.quit()

def make_msg(user):
    msg = MIMEMultipart('alternative')

    msg['Subject'] = SUBJECT
    msg['From'] = GMAIL_USERNAME
    msg['To'] = user.get('email')

    text = create_email_text(user)
    html = create_email_html(user)

    msg.attach(text)
    msg.attach(html)

    return msg

def create_email_text(user):
    return MIMEText(template.render(user=user), 'plain')

def create_email_html(user):
    return MIMEText(html_template.render(user=user), 'html')

def mail(user):
    print "Sending mail to: %s" % user.get('email')
    send_msg(user)
    user['last_mail'] = datetime.combine(now, datetime.min.time())
    db.users.save(user)

if __name__ == '__main__':

    force = False;

    if len(sys.argv) > 1:
        force = sys.argv[1] == '-f'

    print "Started mail script at: %s" % datetime.now().strftime("%c")

    assert APP_PASS != None, "Need to set $GOOGLE_APP_PASS first. Exiting"

    for user in users:
        print "Checking: %s" % user.get('email')
        last_mail = user.get('last_mail')
        if not last_mail or force:
            mail(user)
        else:
            delta = now - last_mail.date()
            if delta.days > 0:
                mail(user)
            else:
                print "Skipping: %s. Already sent today." % user.get('email')
