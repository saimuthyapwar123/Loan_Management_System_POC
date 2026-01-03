import os


# jwt token generate
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = os.getenv("JWT_EXPIRATION_MINUTES", 120)


# mongoDB URL and DB name
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://saiprasad:IeRjrY04NFZwXR4I@newarticles.waa3uh5.mongodb.net/")
DB_NAME = os.getenv("MONGO_DB", "loan_management_system_poc")


# default rate of loan type
DEFAULT_RATES = {
    "PROPERTY": 8.5,
    "EDUCATION": 6.5,
    "GOLD": 10.0,
    "VEHICLE": 9.0
}