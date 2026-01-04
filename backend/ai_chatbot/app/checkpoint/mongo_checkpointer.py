from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver

from ai_chatbot.app.config.settings import (
    MONGO_URI,
    DB_NAME
)


def get_mongo_checkpointer():
    print("✅ MongoDBSaver initialized")
    client = MongoClient(MONGO_URI)
    return MongoDBSaver(
        client=client,
        db_name=DB_NAME,
        collection_name="conversation_memory",
    )
