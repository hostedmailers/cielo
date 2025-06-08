from curl_cffi import requests
import jwt
import datetime

def get_bearer_token(file_path='bearer_token.txt'):
    with open(file_path, 'r') as file:
        return file.read().strip()

def save_bearer_token(token, file_path='bearer_token.txt'):
    with open(file_path, 'w') as file:
        file.write(token)

def get_token_expiry(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = payload.get('exp')
        if exp:
            print(f'Bearer token will expire at : {datetime.datetime.fromtimestamp(exp)}')
            local_time = datetime.datetime.fromtimestamp(exp).astimezone()
            print(f'Bearer token will expire at (local time): {local_time}')
            return local_time
        else:
            return None
    except jwt.DecodeError:
        return None

def renew_bearer_token(old_token):
    url = "https://api.uniwhales.io/auth/renew/"
    payload = {}
    headers = {
        'Authorization': f'Bearer {old_token}',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        new_token = response.json()['token']
        print(f'New token will expire at : {get_token_expiry(new_token)}')
        print(f'Bearer token renewed : {new_token}')
    else:
        print(f'Failed to renew token: {response.status_code}, {response.text}')
    return new_token

def fetch_page(page, db_connection, writer, headers, params):
    response = requests.get('https://feed-api.cielo.finance/v1/leaderboard/tag', params=params, headers=headers)
    return response


# get_token_expiry("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhZGRyZXNzIjoiMHgyZThlZDUxZmE2YWYzYWQ2OWY4NjJlYzVjMDY3ZDQzMDA3YjUxYTk0IiwiaXNzIjoiaHR0cHM6Ly9hcGkudW5pd2hhbGVzLmlvLyIsInN1YiI6InVzZXIiLCJwbGFuIjoiYmFzaWMiLCJiYWxhbmNlIjowLCJpYXQiOjE3MzA3NDkzOTAsImV4cCI6MTczMDc2MDE5MH0.H0Z2mixyJw-JegdkH9dBG3Nt42MA4f9QrOz5BB2k6bQ")
renew_bearer_token("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhZGRyZXNzIjoiMHgwNzU1ODgxNWFmMjc5MGIzYmIxNGY3ODIwNDZiODdkOTk1YjQzYmUwIiwiaXNzIjoiaHR0cHM6Ly9hcGkudW5pd2hhbGVzLmlvLyIsInN1YiI6InVzZXIiLCJwbGFuIjoiYmFzaWMiLCJiYWxhbmNlIjowLCJpYXQiOjE3MzA3ODk1MjEsImV4cCI6MTczMDgwMDMyMX0.YIa_kRAiX0QDkcz5hXTKv0_C2eERJJt6KpookCFwMTo")