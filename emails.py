from fastapi import (BackgroundTasks, UploadFile, File, Form, Depends, HTTPException, status)
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import dotenv_values
from pydantic import BaseModel, EmailStr
from models.models import User
import jwt


# load .env
config_credentials = dict(dotenv_values(".env"))

# mail connection configuration 
conf = ConnectionConfig(
    MAIL_USERNAME = config_credentials["EMAIL"],
    MAIL_PASSWORD = config_credentials["PASSWORD"],
    MAIL_FROM = config_credentials["EMAIL"],
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

# class for email schema
class EmailSchema(BaseModel):
  email: list[EmailStr]
  
  
async def send_email(email: list, instance: User):
  
  # generate token
  token_data = {
    "id": instance.id,
    "username": instance.username
  }
  
  # encode token
  token = jwt.encode(token_data, config_credentials["SECRET"], algorithm="HS256")
  
  # email template
  template = f"""
  
      <!DOCTYPE html>
      <html>
        <head>
          <title>
            Hello {instance.username}
          </title>
        </head>
      <body>
        <div style="display: flex; align-items: center; justify-content: center; flex-direction: column">
        
          <h2> Account Verification </h2>
          <br>
          <h2> Hello {instance.username} </h2>
          <p> please verify your account </p>
          
          <p> Click the link below to confirm your account </p>
          
          <a style="margin-top: 1rem"; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; background-color: blue; color: white;" 
          href="http://localhost:5000/verification?token={token}">
          Confirm Account
          </a>
          
          <p> Please ignore if this was not you </p>
          
        </div>
      </body
      </html

  """
  
  # skema pesan yang akan dikirim
  message = MessageSchema(
    subject = "Account Verification",
    recipients = email, # List of recipients email
    body = template,
    subtype = "html"
  )
  
  
  fastmail_conf = FastMail(conf) # FastMail config
  await fastmail_conf.send_message(message) # kirim email dengan FastMail sesuai dengan skema pesan yang dibuat
  