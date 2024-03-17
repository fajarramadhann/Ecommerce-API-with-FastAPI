from fastapi import FastAPI, HTTPException, Request, status, Request, Depends
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import HTMLResponse
from tortoise.contrib.fastapi import register_tortoise

from models.models import * # import all from models/models.py
from authentication.authentication import * # import all from authentication.py
from emails import send_email

# signals
from tortoise.signals import post_save
from tortoise import BaseDBAsyncClient

#authentication
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# response classes
from fastapi.responses import HTMLResponse

# image & upload file
from fastapi import UploadFile, File
from PIL import Image
import secrets

# templates
from fastapi.templating import Jinja2Templates


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
  token = await token_generator(request_form.username, request_form.password)
  return {"access_token": token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
  try:
    payload = jwt.decode(token, config_credentials["SECRET"], algorithms = ["HS256"])
    user = await User.get(id = payload.get("id"))
  except:
    raise HTTPException(
      status_code = status.HTTP_401_UNAUTHORIZED,
      detail = "Invalid Username or Password",
      headers = {"WWW-Authenticate": "Bearer"}
    )
  
  return await user

@app.post("/user/me")
async def user_login(user: user_pydanticIn = Depends(get_current_user)):
  business = await Business.get(owner = user)

  return {
    "status": "OK",
    "data": {
      "username": user.username,
      "email": user.email,
      "verified": user.is_verified,
      "join_date": user.joinDate.strftime("%d %b %Y")
    }
  }  

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


# email verification dengan email verification template html
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

app.mount("/static", StaticFiles(directory = "static"), name="static")

@app.post('/upload-img/profile')
async def upload_img_profile(file: UploadFile = File(...), user: user_pydantic = Depends(get_current_user)):
  
  PATHFILE = "./static/images/userProfiles/"
  # ambil filename
  filename = file.filename
  
  # ambil extension dari filename
  extension = filename.split(".")[1]
  if extension not in ["png", "jpg", "jpeg"]:
    return {"status": "error", "detail": "Extension not allowed"}
  
  # generate token name
  token_name = secrets.token_hex(10)+ "." + extension
  generated_name = PATHFILE + token_name
  
  file_content = await file.read()
  
  with open(generated_name, "wb") as f:
    f.write(file_content)
    
  
  img = Image.open(generated_name)
  img = img.resize((300, 300))
  img.save(generated_name)
  
  f.close()
  
  # auth upload img
  
  business = await Business.get(owner = user)
  owner = await business.owner
  
  if owner == user:
    business.logo = token_name
    await business.save()
    
  else:
    raise HTTPException(
      status_code = status.HTTP_401_UNAUTHORIZED,
      detail = "Not authorized to upload image",
      headers = {"WWW-Authenticate": "Bearer"}
    )
  
  fileUrl = "localhost:5000" + generated_name[1:]
  return {"status": "OK", "detail": "Image uploaded successfully", "filename": fileUrl}

@app.post("/upload-img/product/{id}")
async def upload_img_product(id: int, file: UploadFile = File(...), user: user_pydantic = Depends(get_current_user)):
  
  PATHFILE = "./static/images/products/"
  # ambil filename
  filename = file.filename
  
  # ambil extension dari filename
  extension = filename.split(".")[1]
  
  if extension not in ["png", "jpg", "jpeg"]:
    return {"status": "error", "detail": "Extension not allowed"}
  
  # generate token name
  token_name = secrets.token_hex(10)+ "." + extension
  generated_name = PATHFILE + token_name
  
  file_content = await file.read()
  
  with open(generated_name, "wb") as f:
    f.write(file_content)
    
  
  img = Image.open(generated_name)
  img = img.resize((200, 200))
  img.save(generated_name)
  
  f.close()

  product = await Product.get(id = id)
  business = await product.business
  owner = await business.owner
  
  if owner == user:
    product.productImage = token_name
    await product.save()
    
  else:
    raise HTTPException(
      status_code = status.HTTP_401_UNAUTHORIZED,
      detail = "Not authorized to upload image",
      headers = {"WWW-Authenticate": "Bearer"}
    )
  
  fileUrl = "localhost:5000" + generated_name[1:]
  return {"status": "OK", "detail": "Image uploaded successfully", "filename": fileUrl}
  
  
  
  
  
  
  
  
  
# connect to database
register_tortoise(
  app,
  db_url="mysql://jardev:jarssdev@localhost:3306/ecommerce-fastapi",
  modules={"models": ["models.models"]},
  generate_schemas=True,
  add_exception_handlers=True
)
  
