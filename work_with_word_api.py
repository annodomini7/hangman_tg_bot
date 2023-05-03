import requests
from my_token import API_KEY
import json


def find_word() -> str:
    api_url = 'https://api.api-ninjas.com/v1/randomword'
    while True:
        response = requests.get(api_url, headers={'X-Api-Key': API_KEY, 'type': 'noun'})
        if response.status_code == requests.codes.ok:
            text = json.loads(response.text)
            try:
                meaning_of_word(text)
                return text['word'].lower()
            except:
                pass


def meaning_of_word(word: str) -> str:
    api_url = 'https://api.api-ninjas.com/v1/dictionary?word={}'.format(word)
    response = requests.get(api_url, headers={'X-Api-Key': API_KEY})
    if response.status_code == requests.codes.ok:
        text = json.loads(response.text)
        return text['definition']
    else:
        raise RuntimeError
