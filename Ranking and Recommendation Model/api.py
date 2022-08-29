import pandas as pd
import numpy as np
import os
import pickle
import warnings
import math 
from flask import Flask, request
from flask_restful import Api, Resource

from matplotlib import pyplot as plt
from pandas import DataFrame, Series
from math import *
from scipy.spatial import distance
from decimal import Decimal

# Instantiate Flask Rest Api
app = Flask(__name__)
api = Api(app)

# Create class for Api Resource
class RRM(Resource):
    def get(self):
        # get request that returns the JSON format for API request
        return {'status_data': 'RRMDataSet.json'}, 200
    
    #df.to_json (r'C:\Users\Ron\Desktop\Test\New_Products.json')
    
    def post(self):
        # post request
        
        data = request.get_json()
        p = float(data['personalityPrecentage'])
        s = float(data['skillPrecentage'])
        l = data['language']
        n = data['nunOfCandidates']
        try:
        
            #import Data Set
            status_data=pd.read_json("Research/2022-014/Ranking and Recommendation Model/RRMDataSet.json")
            
            #Filtering the Language
            grouped = status_data.groupby(status_data.Language_type)
            df= grouped.get_group(l)
            
            
            #Give the priorities to SkillScore
            def multiply_s1(x):
                return x * 0.7

            df['cSkillScore'] = df['cSkillScore'].apply(multiply_s1)
            
            def multiply_s2(x):
                return x * 0.3

            df['cLanUsageScore'] = df['cLanUsageScore'].apply(multiply_s2)
            
            #Create Skill Compound
            S_cols = ['cSkillScore', 'cLanUsageScore']

            df['S_Compound'] = df[S_cols].sum(axis=1)
            
            #Create the Personality traits to marks
            def multply(x):
                return x * (-1)

            df['cNEU'] = df['cNEU'].apply(multply)
            
            #Create Personality compound field
            P_cols = ['cOPN', 'cCON','cEXT', 'cAGR', 'cNEU']

            df['P_Compound'] = df[P_cols].sum(axis=1)
            def P_multiply(x):
                return x * 20

            df['P_Compound'] = df['P_Compound'].apply(P_multiply)
            
            # Drop NAs
            status_data = status_data.dropna()

            # We drop columns which give us a score for personality type
            df = df.drop(['cOPN', 'cCON','cEXT','cAGR','cNEU','cSkillScore','cLanUsageScore'], axis=1)
            
            #Recruitor Selection for Personality Precentage
            def C1_multiply(x):
                return x * (p/float(100)) 
            
            df['P_Compound'] = df['P_Compound'].apply(C1_multiply)
            
            #Recruitor Selection for Skill Precentage
            def C2_multiply(x):
                return x * (s/float(100)) 

            df['S_Compound'] = df['S_Compound'].apply(C2_multiply)
            
            #Add Euclidean Distance
            x1 =s 
            y1 =p 

            x2= df.S_Compound.values
            y2= df.P_Compound.values
           

            distance = np.sqrt(np.square(x1 - x2) + np.square(y1 - y2))

            # print Euclidean distance      
            df['E_distance'] = distance
            
            #Ranking
            df.sort_values(by=['E_distance'])
            E_df = df.sort_values(by=['E_distance'])
            
            # We drop columns which give us a score for personality type
            F_df = E_df.drop(['Language_type', 'S_Compound','P_Compound','E_distance'], axis=1)
            
            #Filter the needing of candidate quantity
            R_Sdf = F_df.head(int(n))
            
            
            json_load = R_Sdf.to_json()
            return { 'Rank_Candidates': json_load }, 200
        
        except:
           
            return {'Error!': 'Wrong Way'}, 500

api.add_resource(RRM, '/rrm')
app.run(port=5000, debug=True)
# Run with -> python "Research/2022-014/Ranking and Recommendation Model/api.py"
