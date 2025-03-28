# from core.config import settings as s
#
#
# FIREBASE_CONF = {
#     'apiKey': s.env.FIREBASE_APIKEY,
#     'authDomain': s.env.FIREBASE_AUTHDOMAIN,
#     'projectId': s.env.FIREBASE_PROJECTID,
#     'storageBucket': s.env.FIREBASE_BUCKET,
#     'messagingSenderId': s.env.FIREBASE_SENDERID,
#     'appId': s.env.FIREBASE_APPID,
# }

# import firebase_admin
# from firebase_admin import credentials
#
#
# cred = credentials.Certificate("path/to/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)


# from fastapi import FastAPI, Depends, HTTPException
# from firebase_admin import auth, initialize_app
# from fastapi.security import OAuth2PasswordBearer
#
# app = FastAPI()
# initialize_app()
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
# def get_verified_user(token: str = Depends(oauth2_scheme)):
#     try:
#         decoded_token = auth.verify_id_token(token)
#         return decoded_token
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid token")
#
# @app.get("/protected")
# async def protected_route(user: dict = Depends(get_verified_user)):
#     return {"message": "Access granted", "user": user}
