from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.goal

def delete_all_users():
    users = db.users.remove()
    print "Deleted all users"

if __name__ == '__main__':
    print "This will delete all users. Proceed? (y/N)",
    answer = raw_input()
    if answer == 'y':
        delete_all_users()
