import json
import requests
import numpy as np
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

def analyze_github(username):
    try:
        data = requests.get('https://api.github.com/users/' + username,headers={'Authorization': 'Bearer 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'})
        data = data.json()
        data_l = data
        url = data['repos_url']
        page_no = 1
        repos_data = []
        while (True):
            response = requests.get(url, headers={'Authorization': 'Bearer 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'})
            response = response.json()
            repos_data = repos_data + response
            repos_fetched = len(response)
            if (repos_fetched == 30):
                page_no = page_no + 1
                url = data['repos_url'] + '?page=' + str(page_no)
            else:
                break
                    
            repos_information = []
            for i, repo in enumerate(repos_data):
                if (repo['fork'] == False):
                    data = []
                    data.append(repo['id'])
                    data.append(repo['name'])
                    data.append(repo['description'])
                    data.append(repo['created_at'])
                    data.append(repo['updated_at'])
                    data.append(repo['owner']['login'])
                    data.append(repo['license']['name'] if repo['license'] != None else None)
                    data.append(repo['has_wiki'])
                    data.append(repo['forks_count'])
                    data.append(repo['open_issues_count'])
                    data.append(repo['stargazers_count'])
                    data.append(repo['watchers_count'])
                    data.append(repo['url'])
                    data.append(repo['commits_url'].split("{")[0])
                    data.append(repo['url'] + '/languages')
                    repos_information.append(data)
    
            repos_df = pd.DataFrame(repos_information, columns = ['Id', 'Name', 'Description', 'Created on', 'Updated on', 
                                                                  'Owner', 'License', 'Includes wiki', 'Forks count', 
                                                                  'Issues count', 'Stars count', 'Watchers count',
                                                                  'Repo URL', 'Commits URL', 'Languages URL'])
        
            langArr = []

            for i in range(repos_df.shape[0]):
                response = requests.get(repos_df.loc[i, 'Languages URL'], headers={'Authorization': 'Bearer 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'})
                response = response.json()
                if response != {}:
                    arr = []
                    for key, value in response.items():
                        b = {key : value}
                        arr.append(b)

                    langArr.append(arr)

                else:
                    langArr.append([])
                    
            usage_information = []

            for i, repo in enumerate(langArr):

                for j, usage in enumerate(repo):

                    for key, value in usage.items():
                        dataU = []
                        dataU.append(repos_data[i]['id'])
                        dataU.append(data_l['login'])
                        dataU.append(repos_data[i]['name'])
                        dataU.append(key)
                        dataU.append(value)
                        usage_information.append(dataU)

            usage_df = pd.DataFrame(usage_information, columns = ['Id', 'User','Name','Language','value'])
            
             #Filtering the User
            grouped = usage_df.groupby(usage_df.User)
            usage= grouped.get_group(username)
            
            
            #Group by Languages and Calculate percentages
            def multiply_s1(x):
                return x * 100.00
            
            df = pd.DataFrame(pd.to_numeric(usage.groupby('Language')['value'].sum()).nlargest(10))
            total = df['value'].sum()
            df['percentage'] = df['value']/total
            df.reset_index(level=0, inplace=True)
            df['percentage'] = df['percentage'].apply(multiply_s1).round(3)
            df['percentagePoints'] = (df['percentage']/100).round(4)
            
            #getting total reporsitories
            allRepo = pd.DataFrame(usage.groupby('Name'))
            index = allRepo.index
            number_of_repos = len(index)
            rep_point = number_of_repos//10
            
            #add new repo points and calculate the points
            df['NewpercentagePoints'] = df['percentagePoints']+rep_point
            
            #filtering Languages
            mask1 = (df['Language'].str.lower().isin(['java']))
            mask2 = (df['Language'].str.lower().isin(['javascript']))
            mask3 = (df['Language'].str.lower().isin(['python']))

            filteredL = df[mask1 | mask2 | mask3]
            
            #drop unnecessary columns
            F_df = filteredL.drop(['value', 'percentage','percentagePoints'], axis=1)
            F_df = F_df.rename(columns={'NewpercentagePoints': 'Points'})
            scores = {}
            scores['javascript'] = F_df['Points'][0]
            scores['java'] = F_df['Points'][4]
            scores['python'] = F_df['Points'][8]
            return scores
       
    except(ValueError, IOError) as err:
        return {'Error': { 'details': err } }, 500  