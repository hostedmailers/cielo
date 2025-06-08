from curl_cffi import requests
from jwt_utils import get_token_expiry

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

# Example usage:
# old_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhZGRyZXNzIjoiMHgwNzU1ODgxNWFmMjc5MGIzYmIxNGY3ODIwNDZiODdkOTk1YjQzYmUwIiwiaXNzIjoiaHR0cHM6Ly9hcGkudW5pd2hhbGVzLmlvLyIsInN1YiI6InVzZXIiLCJwbGFuIjoiYmFzaWMiLCJiYWxhbmNlIjowLCJpYXQiOjE3MzAwODg2NTYsImV4cCI6MTczMDA5OTQ1Nn0.Kdyytnp2IUXdxm3BFKEs_YSAm17UMtggtbRA5eMCubU'


# (renew_bearer_token(old_token))
