from pymongo import MongoClient


mongo_uri = "mongodb://localhost:27017"
database_name = "fractalalpha"

# Initialize the MongoDB client
client = MongoClient(mongo_uri)
db = client[database_name]
