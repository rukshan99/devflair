import requests

# Extracting profile summary from Linkedin profile
def extract_profile_summary(username):
    api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
    api_key = ''#'6c620473-e480-4678-965e-062d9556e5bc'
    header_dict = {'Authorization': 'Bearer ' + api_key}
    params = {
        'url': 'https://www.linkedin.com/in/' + username + '/',
        'use_cache': 'if-present',
    }
    response = requests.get(api_endpoint,
                            params=params,
                            headers=header_dict)
    profile_data = response.json()
    profile_summary = profile_data['summary'];
    
    return profile_summary