import requests
from my_token import API_KEY
import json


def find_word():
    api_url = 'https://api.api-ninjas.com/v1/randomword'
    response = requests.get(api_url, headers={'X-Api-Key': API_KEY, 'type': 'noun'})
    if response.status_code == requests.codes.ok:
        text = json.loads(response.text)
        return text['word'].lower()
    else:
        raise RuntimeError
