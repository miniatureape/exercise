import os
import sys
import smtplib  
from pymongo import MongoClient
from datetime import date
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
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
    print "Sending to %s, %s" % (msg, user.get('email'))
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
    send_msg(user)
    "TODO: update date"

if __name__ == '__main__':

    if not APP_PASS:
        print "Need app pass!"
        sys.exit()

    for user in users:
        last_mail = user.get('last_mail')
        if not last_mail:
            mail(user)
        else:
            delta = now - last_mail
            if delta.days > 0:
                mail(user)
