import os
import sys
import pandas
import numpy
import json
from bson.json_util import dumps
from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_mail import Message
from flask_mail import Mail
from pathlib import Path

import shared.db as db
from shared.get_personality_scores import get_personality_scores
from shared.token_generator import generate_token
from shared.analyze_github import analyze_github
from shared.calculate_technical_quiz_score import get_quiz_score
from shared.extract_cv_details import extract_cv_details
from shared.get_ranked_list import get_ranked_list

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
candidates_collection = db.CandidatesCollectionConnect(candidates_database)
questions_collection = db.QuestionsCollectionConnect(candidates_database)



@app.route('/api/v1/candidates', methods=['POST'])
def create_candidate_api():
    try:
        candidate = {}
        candidate['_id'] = candidates_collection.count_documents({})
        
        data = request.json
        candidate['firstName'] = data['firstName']
        candidate['lastName'] = data['lastName']
        language = data['language']
        cv_base64 = data['cv']
        
        base_path = Path(__file__).parent
        cv_path = str(base_path) + '/cv/' + language + '/'
        cv_path2 = '/cv/' + language + '/'
        cv_data = extract_cv_details(cv_path, candidate['firstName'], candidate['lastName'], language, cv_base64)
        fileName = cv_data['fileName']
        candidate['path']  =  cv_path2 +  fileName
        
        email = cv_data['email']
        linkedin_username = cv_data['linkedin_username']
        github_username = cv_data['github_username']
                                                                   
        candidate['email'] = email
        candidate['linkedinId'] = linkedin_username
        candidate['githubId'] = github_username
        token = generate_token(candidate)
        candidate['token'] = token
        
        #profile_summary = extract_profile_summary(linkedin_username)
        with open("2022-014/personality_prediction_model/util/sample_data.json", "r") as read_content:
            profile_load = json.load(read_content)
            profile_summary = profile_load['summary']   
        summary_word_count = len(profile_summary.split())
        
        if(summary_word_count > 200):
            personality_scores = get_personality_scores(profile_summary)
            candidate['ppmScore'] = personality_scores
            candidate['isPersonalityQuiz'] = False
        else:
            candidate['ppmScore'] = {}
            msg = Message('Welcome!', sender = 'peter@mailtrap.io', recipients = [email])
            msg.body = 'Hi! We are the DevFlair team and we have a small question for you. Please visit this link to continue. http://localhost:3000/pquiz/' + token
            mail.send(msg)
            candidate['isPersonalityQuiz'] = True
        
        if github_username is not None:
            x_tsuam = analyze_github(github_username)
            if x_tsuam is not None:
                candidate['tsuamScore'] = x_tsuam
            else:
                candidate['tsuamScore'] = {}
                candidate['tsuamScore']['java'] = 0
                candidate['tsuamScore']['javascript'] = 0
                candidate['tsuamScore']['python'] = 0
        
        msg = Message('Welcome!', sender = 'peter@mailtrap.io', recipients = [email])
        msg.body = 'Hi! We are the DevFlair team and we have a technical quiz for you. Please visit this link to continue. http://localhost:3000/pquiz/' + language + '/' + token
        mail.send(msg)
        candidate['isSkillQuiz'] = True
        candidate['tsrmScore'] = {}
        candidate['tsrmScore'][language] = 0
        
        res = candidates_collection.insert_one(candidate)
        return { 'candidate': candidate }, 200
        
    except(ValueError, IOError) as err:
        return {'Error': { 'details': err } }, 500


    
@app.route('/api/v1/personality', methods=['PUT'])
def update_personality_score_api():
    try:
        data = request.json
        token = data['token']
        profile_summary = data['summary']
        personality_scores = get_personality_scores(profile_summary)
        
        candidates_collection.update_one(
            { 'token': token },
            { '$set': {
                    'ppmScore': personality_scores
                }
           }
        )
        
        return {'personality_scores': personality_scores}, 200
        
    except(ValueError, IOError) as err:
        return {'Error': { 'details': err } }, 500    

@app.route('/api/v1/candidates', methods=['GET'])
def get_ranked_list_api():
    try:
        
        skill_priority = request.args.get('skill_priority', default="50", type=float)
        personality_priority = request.args.get('personality_priority', default="50", type=float)
        language = request.args.get('language', default="java", type=str)
        no_of_candidates = request.args.get('no_of_candidates', default="2", type=int)
        
        cursor = candidates_collection.find({ 'language': language })
        
        candidate_list = get_ranked_list(cursor, skill_priority, personality_priority, language, no_of_candidates);
        return { 'candidates': candidate_list }, 200

    except(ValueError, IOError) as err:
        return {'Error': { 'details': err } }, 500

@app.route('/api/v1/allCandidates', methods=['GET'])
def get_list_api():
    try:
        cursor = candidates_collection.find()
        serialized_results = dumps(cursor)
        r = serialized_results.replace("'",'')
        data = json.loads(r)
        
        return { 'candidates': data }, 200

    except(ValueError, IOError) as err:
        return {'Error': { 'details': err } }, 500

@app.route('/api/v1/countCandidates', methods=['GET'])
def count_candidates_by_language_api():
    try:
        language = request.args.get('language', default="", type=str)
        count = candidates_collection.count_documents({ 'language': language })
        
        return { 'count': count }, 200

    except(ValueError, IOError) as err:
        return {'Error': { 'details': err } }, 500
    
@app.route('/api/v1/tokens', methods=['GET'])
def get_candidate_by_token_api():
    try:
        token = request.args.get('token', default="", type=str)
        doc = candidates_collection.find_one({ 'token': token })
        if doc is None:
            return {'candidate': 'No candidate found. Invalid token.', 'isMatch': False}, 200
        
        serialized_results = dumps(doc)
        r = serialized_results.replace("'",'')
        candidate = json.loads(r)
        
        return {'candidate': candidate, 'isMatch': True}, 200
        
    except(ValueError, IOError) as err:
        return {'Error': { 'details': err } }, 500

    
    
@app.route('/api/v1/questions', methods=['GET'])
def get_questions_by_language_api():
    try:
        language = request.args.get('language', default="", type=str)
        cursor = questions_collection.find({'language': language})
        serialized_results = dumps(cursor)
        r = serialized_results.replace("'",'')
        data = json.loads(r)
        
        return {'questions': data}, 200
        
    except(ValueError, IOError) as err:
        return {'Error': { 'details': err } }, 500  

    
    
@app.route('/api/v1/skill', methods=['PUT'])
def update_skill_score_api():
    try:
        data = request.json
        token = data['token']
        language = data['language']
        candidate_answers = data['answers']
        cursor = questions_collection.find({'language': language})
        serialized_results = dumps(cursor)
        r = serialized_results.replace("'",'')
        model_answers = json.loads(r)
        
        skil_score = get_quiz_score(model_answers, candidate_answers)
        candidates_collection.update_one(
            { 'token': token },
            { '$set': {
                    'tsrmScore.%s'%(language): skil_score
                }
           }
        )
        
        return {'language': language, 'skil_score': skil_score}, 200
        
    except(ValueError, IOError) as err:
        return {'Error': { 'details': err } }, 500
    
    
    
app.run(port=5000, debug=True)
# Run with -> python "2022-014/devflair_api.py"