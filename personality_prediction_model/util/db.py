import pymongo
from pymongo import MongoClient

# Connecting to MongoDB Atlas cluster
def DBConnect():
    client = MongoClient("mongodb+srv://admin:3FwQ4ofOoDBXeue1@dev.0wx0l.mongodb.net/candidates?retryWrites=true&w=majority")
    return client

# Connecting to Candidates Database
def CandidatesDBConnect(client):
    db = client.candidates
    return db

# Connectingto Personality Collection
def PersonalityCollectionConnect(db):
    collection = db.personality
    return collection

# For testing
#collection.insert_one({"_id":0, "cOPN":1, "cCON":0, "cEXT":0, "cAGR":1, "cNEU":1})