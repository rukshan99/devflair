import pymongo
from pymongo import MongoClient

# Connecting to MongoDB Atlas cluster
def DBConnect():
    client = MongoClient("mongodb+srv://admin:3FwQ4ofOoDBXeue1@dev.0wx0l.mongodb.net/candidates?retryWrites=true&w=majority")
    return client

# Connecting to candidates database
def CandidatesDBConnect(client):
    db = client.candidates
    return db

# Connecting to candidates collection
def CandidatesCollectionConnect(db):
    collection = db.candidates
    return collection

# Connecting to candidates collection
def QuestionsCollectionConnect(db):
    collection = db.questions
    return collection
