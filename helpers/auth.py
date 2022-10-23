import requests
import json
import os

SECRETS_PATH = f'{os.getcwd()}/secrets/twitch_creds.json'
def get_credentials():
    current_creds = {}
    try:
        with open(SECRETS_PATH, 'r', encoding='utf-8') as fp:
            current_creds = json.load(fp)
    except FileNotFoundError:
        raise FileNotFoundError(f'Please define client_id and client_secret in {SECRETS_PATH} to authenticate with the Twitch api')
        
    if not current_creds.get('client_id'):
        raise KeyError(f'No client_id property found in {SECRETS_PATH}')
    if not current_creds.get('client_secret'):
        raise KeyError(f'No client_secret property found in {SECRETS_PATH}')

    # check if bearer token still valid
    if current_creds.get('bearer_access_token'):
        HEADERS = {
                'Authorization': f'Bearer {current_creds["bearer_access_token"]}'
                }
        validate_endpoint = 'https://id.twitch.tv/oauth2/validate'
        r = requests.get(url=validate_endpoint, headers=HEADERS)
        if r.status_code == 200:
            return current_creds
    
    # if oauth token not valid, get a new one
    new_oauth_token = get_oauth_token(current_creds)
    current_creds['bearer_access_token'] = new_oauth_token
    update_bearer(new_oauth_token)
    return current_creds

def update_bearer(bearer):
    """update bearer token in credentials file"""
    print('Generating new bearer access token')
    curr = None
    with open(SECRETS_PATH, 'r') as fp:
        curr = json.load(fp)
    # update dict with new bearer
    curr['bearer_access_token'] = bearer

    # write obj with new bearer to file
    with open(SECRETS_PATH, 'w') as fp:
        json.dump(fp=fp, obj=curr)

def get_oauth_token(creds):
    oauth_endpoint = 'https://id.twitch.tv/oauth2/token'
    PARAMS = {
        'client_id': creds['client_id'],
        'client_secret': creds['client_secret'],
        'grant_type': 'client_credentials'
    }
    r = requests.post(url=oauth_endpoint, params=PARAMS)
    return r.json().get('access_token')


if __name__ == '__main__':
    res = get_credentials()
    print(res)