import os
import sys
import smtplib  
from pymongo import MongoClient
from datetime import date
from datetime import datetime
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

file_dir = os.path.dirname(__file__)
print file_dir
env = Environment(loader=FileSystemLoader(os.path.join(file_dir, 'templates')))
template = env.get_template('basic_mail.txt')

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

    print "Message for %s: %s" % (user.get('email'), msg.replace('\n', ''))

    session.sendmail(GMAIL_USERNAME, user.get('email'), msg)

    session.quit()

def make_msg(user):
    msg = MIMEText(create_email_text(user))
    msg['Subject'] = SUBJECT
    msg['From'] = GMAIL_USERNAME
    msg['To'] = user.get('email')

    return msg

def create_email_text(user):
    return template.render(user=user)

def mail(user):
    print "Sending mail to: %s" % user.get('email')
    send_msg(user)
    user['last_mail'] = datetime.combine(now, datetime.min.time())
    db.users.save(user)

if __name__ == '__main__':

    print "Started mail script at: %s" % datetime.now().strftime("%c")

    assert APP_PASS != None, "Need to set $GOOGLE_APP_PASS first. Exiting"

    for user in users:
        print "Checking: %s" % user.get('email')
        last_mail = user.get('last_mail')
        if not last_mail:
            mail(user)
        else:
            delta = now - last_mail.date()
            if delta.days > 0:
                mail(user)
            else:
                print "Skipping: %s. Already sent today." % user.get('email')
