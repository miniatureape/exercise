from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.goal

def report_users():
    users = db.users.find()
    for user in users:
        for key, val in user.items():
            print "%s: %s" % (key, val)
        print "\n\n"

if __name__ == '__main__':
    report_users()
