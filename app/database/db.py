from app.config.settings import DB_NAME, MONGO_URI
from motor.motor_asyncio import AsyncIOMotorClient

# mongoDB connection with DB
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

admin_col = db["admin"]
borrower_col = db["borrower"]

def get_collection(name):
    return db[name]