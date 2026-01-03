from motor.motor_asyncio import AsyncIOMotorClient
from ai_chatbot.app.config.settings import DB_NAME, MONGO_URI

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            MONGO_URI,
            maxPoolSize=10,
            minPoolSize=1
        )
    return _client


def get_db():
    return get_client()[DB_NAME]


def get_collection(name: str):
    return get_db()[name]


# Explicit collections (recommended)
borrower_col = get_collection("borrower")
loans_col = get_collection("loans")
admin_col = get_collection("admin")
