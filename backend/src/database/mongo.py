from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "property_graph"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# If database cannot be loaded due to conflicts, run command below
db.datasets.drop()

db["datasets"].create_index("name", unique=True)

