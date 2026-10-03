from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
db = MongoClient(os.getenv('MONGODB_URI'))['jobportal']

r = db.jobs.update_many(
    {'postedBy': ObjectId('6aa798749c1a4a92115f97'), 'createdAt': {'$exists': False}},
    {'$set': {'createdAt': datetime.utcnow(), 'updatedAt': datetime.utcnow()}}
)

# Agar createdAt hai bhi lekin galat format me hai to ye sab ko fix karega
r2 = db.jobs.update_many(
    {'postedBy': ObjectId('6aa798749c1a4a92115f97')},
    {'$set': {'createdAt': datetime.utcnow(), 'updatedAt': datetime.utcnow()}}
)

print(f"Fixed {r2.modified_count} jobs dates - Ab N/A khatam!")