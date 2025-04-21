# database.py
import os
from flask_pymongo import PyMongo
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

mongo = PyMongo()

def init_db(app):
    uri    = os.getenv("COSMOS_MONGO_URI")
    dbname = os.getenv("COSMOS_DBNAME")
    if not uri or not dbname:
        raise RuntimeError("Please set COSMOS_MONGO_URI & COSMOS_DBNAME in .env")
    app.config["MONGO_URI"]    = uri
    app.config["MONGO_DBNAME"] = dbname
    mongo.init_app(app)
    return mongo
