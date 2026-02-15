import os

import requests

base_url = os.environ.get('API_BASE_URL', 'http://localhost:5000')

# GET requests
def get_api_data(endpoint, params=None):
    if params is None:
        params = {}
    response = requests.get(f'{base_url}{endpoint}', params=params)
    return response

# POST requests
def post_api_data(endpoint, data):
    response = requests.post(f'{base_url}{endpoint}', json=data)
    return response

# PATCH requests
def patch_api_data(endpoint, data):
    response = requests.patch(f'{base_url}{endpoint}', json=data)
    return response