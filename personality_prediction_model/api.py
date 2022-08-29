import os
import pandas
import numpy
import json 
from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_mail import Message
from flask_mail import Mail

import util.db as db
from util.linkedin_profile_extract import extract_profile_summary
from util.preprocessor import preprocessor_v1, preprocessor_v2, preprocessor_v3
from util.predictor import predictor_v5

# Instantiate Flask Rest Api
app = Flask(__name__)
CORS(app)
api = Api(app)

# Mailtrap configurations
app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'ddca7a9c425ee2'
app.config['MAIL_PASSWORD'] = 'c8d2cdcd9cd294'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# Database Connection
client = db.DBConnect()
candidates_database = db.CandidatesDBConnect(client)
personality_collection = db.PersonalityCollectionConnect(candidates_database)

# Create class for Api Resource
class PPF(Resource):
    def get(self):
        # Testing email sender
        msg = Message('Hello from the other side!', sender = 'peter@mailtrap.io', recipients = ['paul@mailtrap.io'])
        msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works"
        mail.send(msg)
        
        return "Message sent!"
        # get request that returns the JSON format for API request
        #return { 'JSON data format': { 'username': 'linkedin_username' } }, 200
    
    def post(self):
        # post request
        
        # make db connections global variables 
        global client
        global candidates_database
        global personality_collection
        
        data = request.get_json()
        
        try:
            if data['isLinkedIn']:
                linkedin_username = data['username']
            
                #profile_summary = extract_profile_summary(username)
            
                # For Testing
                #profile_summary = 'Final year undergraduate at Sri Lanka Institute of Information Technology, future Software Engineer. My passion for technology made me fall in love with software development and is the reason to follow my BSc (Hons) Information Technology degree program specializing in Software Engineering.'
            
            else:
                profile_summary = data['about_me'];
            
            # PPF v2.1 (NLTK SentimentIntensityAnalyzer based preprocessor)
            df = preprocessor_v1(profile_summary)
            
            # PPF v3 (Doc2Vec based preprocessor)
            vectors = preprocessor_v2(profile_summary)
            
            # PPF v4 (fastText based preprocessor)
            text = preprocessor_v3(profile_summary)
            
            # Predictor_v4 deals with the best accuracy models for each trait from all the approaches
            result = predictor_v5(df, vectors, text)
            
            # Counting the personality collection document length
            count = personality_collection.count_documents({})
            
            # Creating JSON
            pOPN = result[0] if(type(result[0]) == float) else result[0].item()
            pCON = result[1] if(type(result[1]) == float) else result[1].item()
            pEXT = result[2] if(type(result[2]) == float) else result[2].item()
            pAGR = result[3] if(type(result[3]) == float) else result[3].item()
            pNEU = result[4] if(type(result[4]) == float) else result[4].item()
            
            # Calculating the compund personality score as a PERCENTAGE
            pCOMPOUND = (pOPN * pCON * pEXT * pAGR * (100.0-pNEU)) / 100000000
            
            json_dump = json.dumps({ "_id": count, "pOPN": pOPN, "pCON": pCON, "pEXT": pEXT, "pAGR": pAGR, "pNEU": pNEU, "pCOMPOUND": pCOMPOUND })
            print(json_dump)
            json_load = json.loads(json_dump)
            
            # Saving to personality collection
            res = personality_collection.insert_one(json_load)
            
            return { 'personality_prediction': json_load }, 200
        
        except:
            # If client sends the wrong request or data type then return correct format
            return {'Error! Please use this JSON format': { 'username': 'linkedin_username' } }, 500

api.add_resource(PPF, '/ppf')
app.run(port=5000, debug=True)
# Run with -> python "2022-014/personality_prediction_model/api.py"