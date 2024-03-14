from fastapi.exceptions import HTTPException
from fastapi import status
from passlib.context import CryptContext
import jwt
from dotenv import dotenv_values
from models.models import User

config_credentials = dotenv_values(".env")

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password):
  return password_context.hash(password)


async def verify_token(token: str):
  
  try:
    payload = jwt.decode(token, config_credentials["SECRET"], algorithms=["HS256"]) # decode token
    user = await User.get(id = payload["id"]) # return this user
  
  except:
    raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid token", headers = {"WWW-Authenticate": "Bearer"}) # if token is invalid
  
  return user # if token is valid