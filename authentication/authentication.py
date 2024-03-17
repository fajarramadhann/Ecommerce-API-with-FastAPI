from fastapi.exceptions import HTTPException
from fastapi import status
from passlib.context import CryptContext
import jwt
from dotenv import dotenv_values
from models.models import User

# load .env file
config_credentials = dotenv_values(".env")

# password hashing
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password):
  return password_context.hash(password)

# verify token for email verification
async def verify_token(token: str):
  
  try:
    payload = jwt.decode(token, config_credentials["SECRET"], algorithms=["HS256"]) # decode token
    user = await User.get(id = payload["id"]) # return this user
  
  except:
    raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid token", headers = {"WWW-Authenticate": "Bearer"}) # if token is invalid
  
  return user # if token is valid

# function untuk verify password asli dari database dan password yang diinputkan user dan sudah dihash
async def verify_password(plain_password, hashed_password):
  return password_context.verify(plain_password, hashed_password)

# function untuk authenticate user apakah user sudah terdaftar atau belum
async def authenticate_user(username, password):
  user = await User.get(username = username) # ambil username dari database
  
  # jika user terdaftar dan password sesuai
  if user and verify_password(password, user.password):
    return user
  return False

# generate token untuk user yang sudah terdaftar
async def token_generator(username: str, password: str):
  user = await authenticate_user(username, password)
  
  if not user:
    raise HTTPException(
      status_code = status.HTTP_401_UNAUTHORIZED,
      detail = "Invalid Username or Password",
      headers = {"WWW-Authenticate": "Bearer"}
    )

  token_data = {
    "id": user.id,
    "username": user.username
  }

  token = jwt.encode(token_data, config_credentials["SECRET"])

  return token