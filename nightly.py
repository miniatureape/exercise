import os
import sys
import smtplib  
from datetime import date
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pymongo import MongoClient
from jinja2 import Environment, FileSystemLoader

MAX_DEBT = 500

class MailMan(object):

    PLAIN_TPL_NAME = 'plain-mail.txt'
    HTML_TPL_NAME  = 'html-mail.html'

    subject = 'Here\s Your Daily Balance'
    return_addr = 'info@excercredit.com'

    def __init__(self, options):

         self.options = options

         file_dir = os.path.dirname(__file__)
         env = Environment(loader=FileSystemLoader(os.path.join(file_dir, 'templates')))

         self.plain_tpl = env.get_template(self.PLAIN_TPL_NAME)
         self.html_tpl = env.get_template(self.HTML_TPL_NAME)

    def should_mail(self, user):
        last_mail = user.get('last_mail')
        if not last_mail or self.options.force: return True

        delta = date.today() - last_mail.date()
        return delta.days > 0

    def create_envelope(self, email):
         msg = MIMEMultipart('alternative')

         msg['Subject'] = self.subject
         msg['From'] = self.return_addr
         msg['To'] = email

         return msg

    def create_html_body(self, user, msgs):
        return MIMEText(self.html_tpl.render(user=user, msgs=msgs), 'html')

    def create_plain_body(self, user, msgs):
        return MIMEText(self.plain_tpl.render(user=user, msgs=msgs), 'plain')

    def mail(self, user, msgs):
        email = user.get('email')
        envelope = self.create_envelope(email)

        envelope.attach(self.create_plain_body(user, msgs))
        envelope.attach(self.create_html_body(user, msgs))

        session = smtplib.SMTP(self.options.smtp_server, 587)
        session.ehlo()
        session.starttls()
        session.login(self.options.smtp_username, self.options.smtp_password)

        msg_str = envelope.as_string();

        print("Message for %s: %s" % (email, msg_str.replace('\n', '')))

        try: 
            session.sendmail(self.options.smtp_username, email, msg_str)
        except smtplib.SMTPRecipientsRefused:
            print("Could not send message to %s" % email_address)

    def email_user(self, user, msgs):

        if self.should_mail(user):
            self.mail(user, msgs)
        else:
            print("Skipping: %s. Already emailed today." % user.get('email'))


class Nightly(object):

    def __init__(self, mailman):

        client = MongoClient('localhost', 27017)
        self.db = client.goal
        self.mailman = mailman

        self.msgs = []

    def should_deduct(self, user):
        last_deducted = user.get('last_deducted', None)
        if not last_deducted: return True

        delta = date.today() - last_deducted.date()
        return delta.days > 0;

    def set_streak(self, user):
        prev_balance = user.get('balance')

        if prev_balance >= 0:
            print("User: %s is on a streak. Prev streak was %s days." % (user.get('email'), user.get('streak')))
            user['streak'] = user['streak'] + 1
            self.msgs.append("ON_STREAK")

            if user['streak'] > user['longest_streak']:
                print("User: %s set a streak record with %s days." % (user.get('email'), user.get('streak')))
                user['longest_streak'] = user['streak']
                self.msgs.append("NEW_RECORD")

    def limit(self, user):
        if user['balance'] >= MAX_DEBT:
            print("Limiting %s to max of %s" % (user.get('email'), MAX_DEBT))
            user['balance'] = MAX_DEBT
            self.msgs.append('REACHED_MAX_DEBT')

    def deduct(self, user):
        deduction = user.get('deduction', 100)
        print("Deducting %s points from: %s" % (deduction, user.get('email')))

        user['balance'] = user['balance'] - deduction
        user['last_deducted'] = datetime.combine(date.today(), datetime.min.time())

    def update_account(self, user):

        if self.should_deduct(user):
            self.set_streak(user)
            self.deduct(user)
            self.limit(user)
        else:
            print("Skipping: %s. Already deducted today." % user.get('email'))

    def send_email(self, user):
        self.mailman.email_user(user, self.msgs)
        print("sending email");

    def do_nightly(self, user):
        print("Processing user: %s" % user.get('email'));

        self.msgs = [] # reset messages for user
        self.update_account(user)
        self.send_email(user)

    def get_users(self):
        return self.db.users.find()

    def run(self):

        print("Starting nightly job at: %s", datetime.now().strftime("%c"))

        for user in self.get_users():
            self.do_nightly(user)

if __name__ == '__main__':

    """ This job is responsible for updating a user's data
        and sending her an email digest.  """

    from optparse import OptionParser

    parser = OptionParser()

    parser.set_defaults(
        force=False,
        smtp_password=os.environ.get("SMTP_PASS"),
        smtp_server="smtp.sendgrid.net",
        smtp_username="justindonato750",
    )

    parser.add_option('-f', '--force', 
                     action="store_true", dest="force",
                     help="Send email even if its already been sent for the day")

    parser.add_option('-p', '--smtp-password', 
                     action="store", type="string", dest="smtp_password",
                     help="Password for SMTP server")

    parser.add_option('-s', '--smtp-server', 
                     action="store", type="string", dest="smtp_server",
                     help="Password for SMTP server")

    parser.add_option('-u', '--smtp-user', 
                     action="store", type="string", dest="smtp_user",
                     help="Username for SMTP server")

    (options, args) = parser.parse_args()

    if not options.smtp_password:
        print("Must set SMTP_PASS or run with --smtp-password option.")
        sys.exit()

    mailman = MailMan(options)
    nightly = Nightly(mailman)
    nightly.run()
