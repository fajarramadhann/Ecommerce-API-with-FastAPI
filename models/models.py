from tortoise import Model, fields
from pydantic import BaseModel
from datetime import datetime, timezone
from tortoise.contrib.pydantic import pydantic_model_creator


""" 
Create Model database tables ( User, Business, Product )
"""
class User(Model):
  id = fields.IntField(pk = True, index = True)
  username = fields.CharField(max_length=20, null = False, unique = True)
  email = fields.CharField(max_length=200, null = False, unique = True)
  password = fields.CharField(max_length=100, null = False)
  is_verified = fields.BooleanField(default = False)
  joinDate = fields.DatetimeField(default = datetime.now(timezone.utc))
  

class Business(Model):
  id = fields.IntField(pk = True, index = True)
  business_name = fields.CharField(max_length=20, null = False, unique = True)
  city = fields.CharField(max_length=100, null = False, default = "Unspecified")
  region = fields.CharField(max_length=100, null = False, default = "Unspecified")
  businessDescription = fields.TextField(null = True)
  logo = fields.CharField(max_length=200, null = False, default = "default.jpg")
  owner = fields.ForeignKeyField("models.User", related_name="business")
  
class Product(Model):
  id = fields.IntField(pk = True, index = True)
  name = fields.CharField(max_length=100, null = False, index = True)
  category = fields.CharField(max_length=30, index = True)
  originalPrice = fields.DecimalField(max_digits=12, decimal_places=2)
  newPrice = fields.DecimalField(max_digits=12, decimal_places=2)
  percentageDiscount = fields.IntField()
  offerExpirationDate = fields.DateField(default = datetime.utcnow)
  productImage = fields.CharField(max_length=200, null = False, default = "productDefault.jpg")
  business = fields.ForeignKeyField("models.Business", related_name="products")


  """
  Create Pydantic models for User, Business, Product
  """
userPydantic = pydantic_model_creator(User, name = "User", exclude=("is_verified" , ))
userPydanticIn = pydantic_model_creator(User, name = "UserIn", exclude_readonly = True, exclude=("is_verified" , "joinDate"))
userPydanticOut = pydantic_model_creator(User, name = "UserOut", exclude=("password" , ))

class user_pydanticIn(userPydanticIn):
  pass

businessPydantic = pydantic_model_creator(Business, name = "Business")
businessPydanticIn = pydantic_model_creator(Business, name = "BusinessIn", exclude_readonly = True)

productPydantic = pydantic_model_creator(Product, name = "Product")
productPydanticIn = pydantic_model_creator(Product, name = "ProductIn", exclude=("percentageDiscount", "id"))

