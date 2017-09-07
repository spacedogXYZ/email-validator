import requests
import os

BRITEVERIFY_API_URL = 'https://bpi.briteverify.com/emails.json'
BRITEVERIFY_API_KEY = os.environ.get('BRITEVERIFY_API_KEY')

def check(email):
    r = requests.get(BRITEVERIFY_API_URL, params={address: email, apikey:BRITEVERIFY_API_KEY})
    response = r.json()

    status = response.get('status')
    if response.get('disposable'):
        status = 'disposable'
    # check role_address as well?
    return status
