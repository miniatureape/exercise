from pymongo import MongoClient
from datetime import date
from datetime import datetime

client = MongoClient('localhost', 27017)
db = client.goal
now = date.today()
users = db.users.find()

def deduct(user):
    print "Deducting 100 points from: %s" % user.get('email')

    prev_balance = user.get('balance')

    if prev_balance >= 0:
        user['streak'] = user['streak'] + 1

        if user['streak'] > user['longest_streak']:
            user['longest_streak'] = user['streak']


    user['balance'] = user['balance'] - 100
    user['last_deducted'] = datetime.combine(now, datetime.min.time())

    db.users.save(user)

if __name__ == '__main__':

    print "Started deducting script at: %s" % datetime.now().strftime("%c")

    for user in users:
        print "Checking: %s" % user.get('email')
        last_deducted = user.get('last_deducted', None)
        if not last_deducted:
            deduct(user)
        else:
            delta = now - last_deducted.date()
            if delta.days > 0:
                deduct(user)
            else:
                print "Skipping: %s. Already deducted today." % user.get('email')
