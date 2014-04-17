import pymongo
import Users
from pymongo import MongoClient

client = MongoClient()
client = MongoClient('localhost', 27017)

db = client.goal

users = db.users
users.ensure_index([("email",1)], cache_for=300, unique=True)

users.update(
    {"email": "justin.donato@gmail.com"}, 
    Users.create_doc("justin.donato@gmail.com"), 
    upsert=True
)
