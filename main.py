from fastapi import FastAPI, HTTPException, Request, status, Request
from starlette.requests import Request
from starlette.responses import HTMLResponse
from tortoise.contrib.fastapi import register_tortoise
from models.models import * # import all from models/models.py
from authentication.authentication import (get_hashed_password, verify_token) # import all from authentication.py

# signals
from tortoise.signals import post_save
from tortoise import BaseDBAsyncClient

# response classes
from fastapi.responses import HTMLResponse

# templates
from fastapi.templating import Jinja2Templates

from emails import send_email

app = FastAPI()


@post_save(User) # DECORATOR | menjalankan fungsi create_business setiap objek User yang dibuat disimpan ke database
async def create_business( # 
  sender: "type[User]", 
  instance: User,
  created: bool,
  usingDb: BaseDBAsyncClient,
  updateFields: list[str]
) -> None: 
  
  if created:
    businessObj = await Business.create(
      business_name=instance.username,
      owner=instance
    )
    
    await businessPydantic.from_tortoise_orm(businessObj)
    # send the email
    await send_email([instance.email], instance)

@app.post("/register")
async def user_registration(user: user_pydanticIn):
  userInfo = user.model_dump(exclude_unset = True)
  userInfo["password"] = get_hashed_password(userInfo["password"])
  userObj = await User.create(**userInfo)
  newUser = await userPydantic.from_tortoise_orm(userObj)
  return{
    "Status": "OK",
    "data": f"Hello {newUser.username}. Please check your email to confirm your registration"
  }

templates = Jinja2Templates(directory = "templates")
@app.get("/verification", response_class = HTMLResponse)
async def emailVerification(request: Request, token: str):
  user = await verify_token(token)
  
  if user and not user.is_verified:
    user.is_verified = True
    await user.save()
    return templates.TemplateResponse("verification.html", {"request": request, "username": user.username})
  
  raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid token or Expired Token", headers = {"WWW-Authenticate": "Bearer"})

@app.get("/")
def index():
  return {"Message": "Hello World"}

# connect to database
register_tortoise(
  app,
  db_url="mysql://jardev:jarssdev@localhost:3306/ecommerce-fastapi",
  modules={"models": ["models.models"]},
  generate_schemas=True,
  add_exception_handlers=True
)
  
