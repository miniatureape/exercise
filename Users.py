import time
import random
import datetime
from flask.ext import pymongo

"""

exercises: [{
    "eid": 123,
    "name": "abc",
    "value": "abc",
    "quantity": 5,
}]


"""

db = None
app = None

def setApp(f):
    global app 
    app = f;

def setDb(mongo):
    global db
    with app.app_context():
        db = mongo.db;

def generate_id():
    return '%030x' % random.randrange(16**8)

def create_doc(email, id=None):

    user_doc = {
        "bill": 0,
        "balance": 0,
        "email": email,
        "exercises": [],
        "created": int(time.time()),
        "streak": 0,
        "longest_streak": 0,
        "last": None,
        "last_mail": None,
        "last_deducted": None
    }

    return user_doc

def create(email):
    return db.users.insert(create_doc(email))

def find(query):
    return db.users.find(query)

def find_one(query):
    return db.users.find_one(query)

def find_by_id(user_id):
    return db.users.find_one({'_id': pymongo.ObjectId(user_id)})

def update_exercise(user, data, eid):
    for e in user.get(exercises, []):
        if e.get('eid') == eid:
            e.update(data)
    return user

def add_exercise(user, data):
    data.update({"eid": generate_id()})
    user.get('exercises').append(data)
    return user

def set_exercise(user, data, eid=None):

    if eid:
        user = update_exercise(user, data, eid)
    else:
        user = add_exercise(user, data);

    return store(user)

def del_exercise(user, eid):
    exercises = [e for e in user.get('exercises', []) if e.get('eid') != eid]
    user['exercises'] = exercises
    return store(user)

def date_str_to_list(datestr):
    return [int(d) for d in datestr.split('/')]

def deposit(user, value, date):
    user['balance'] = user.get('balance') + value
    user['last'] = date

    return store(user)

def store(user):
    db.users.save(user)
    return user

def delete(user):
    return db.users.remove({'_id': user.get('_id')})

