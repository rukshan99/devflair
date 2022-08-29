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
class TSUM(Resource):
    def get(self):
        # get request that returns the JSON format for API request
        return {'status_data': 'tech_usageV2.json'}, 200
    
    #df.to_json (r'C:\Users\Ron\Desktop\Test\New_Products.json')
    
    def post(self):
        # post request
        
        data = request.get_json()
        u = data['username']
        l1 = data['lang1']
        l2 = data['lang2']
        l3 = data['lang3']
        l4 = data['lang4']
        try:
        
            #import Data Set
            
            status_data=pd.read_json("Reasearch/2022-014/Technical Skill Usage Analysis Model/tech_usageV2.json")
            
                
            #Filtering the User
            
            grouped = status_data.groupby(status_data.User)
            usage= grouped.get_group(u)
            
            
            #Group by Languages and Calculate percentages
            
            def multiply_s1(x):
                return x * 100.00
            
            df = pd.DataFrame(usage.groupby('Language')['value'].sum().nlargest(10))
            total = df['value'].sum()
            print(total)
            df['percentage'] = df['value']/total
            df.reset_index(level=0, inplace=True)
            df['percentage'] = df['percentage'].apply(multiply_s1).round(3)
            df['percentagePoints'] = (df['percentage']/100).round(4)
            print(df)
            
            #getting total reporsitories
            
            allRepo = pd.DataFrame(usage.groupby('Name'))
            index = allRepo.index
            number_of_repos = len(index)
            print(number_of_repos)
            rep_point = number_of_repos//10
            print("Repos point: {}".format(rep_point))
            
            #add new repo points and calculate the points
            
            df['NewpercentagePoints'] = df['percentagePoints']+rep_point
            print(df)
            
            #filtering Languages
            
            mask1 = (df['Language'].isin([l1]))
            mask2 = (df['Language'].isin([l2]))
            mask3 = (df['Language'].isin([l3]))
            mask4 = (df['Language'].isin([l4]))

            filteredL = df[mask1 | mask2 | mask3 | mask4]
            print(filteredL)
            
            #drop unnecessary columns
            
            F_df = filteredL.drop(['value', 'percentage','percentagePoints'], axis=1)
            F_df = F_df.rename(columns={'NewpercentagePoints': 'Points'})
            print(F_df)
            
            json_load = F_df.to_json(orient = 'records')
            print(json_load)
            return { 'Language_points': json_load }, 200

            
  
        
        except:
           
            return {'Error!': 'Wrong Way'}, 500

api.add_resource(TSUM, '/tsum')
app.run(port=5000, debug=True)
# Run with -> python "Reasearch/2022-014/Technical Skill Usage Analysis Model/api.py"

# {
# "username":"Navoxya",
# "lang1":"Dart",
# "lang2":"JavaScript",
# "lang3":"HTML",
# "lang4":"CSS"
# }
