import jwt
import datetime

def get_token_expiry(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = payload.get('exp')
        if exp:
            return datetime.datetime.fromtimestamp(exp)
        else:
            return None
    except jwt.DecodeError:
        return None

# token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhZGRyZXNzIjoiMHgwNzU1ODgxNWFmMjc5MGIzYmIxNGY3ODIwNDZiODdkOTk1YjQzYmUwIiwiaXNzIjoiaHR0cHM6Ly9hcGkudW5pd2hhbGVzLmlvLyIsInN1YiI6InVzZXIiLCJwbGFuIjoiYmFzaWMiLCJiYWxhbmNlIjowLCJpYXQiOjE3MzAwODg2NTYsImV4cCI6MTczMDA5OTQ1Nn0.Kdyytnp2IUXdxm3BFKEs_YSAm17UMtggtbRA5eMCubU"
# expiry = get_token_expiry(token)

# if expiry:
#     print("Token expires at:", expiry)
# else:
#     print("Unable to determine token expiry.")