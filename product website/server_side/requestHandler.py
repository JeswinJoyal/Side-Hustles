from fastapi import FastAPI,HTTPException,status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext #!should i put hashing function here or in the data.py
import secrets

from sqlFunctions import data

app = FastAPI()

app.mount("/css", StaticFiles(directory="../client_side/css"), name="css")
app.mount("/js", StaticFiles(directory="../client_side/js"), name="js")

std_session_duration = 30 #in minutes


#==========================================================================================

@app.get("/")
def HomePage():
    try:
        with open("../client_side/index.html", "r") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: index.html not found!</h1>", status_code=404)
    
@app.get("/admin/login")
def AdminLoginPage():
    try:
        with open("../client_side/adminLogin.html", "r") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: adminLogin.html not found!</h1>", status_code=404)
   
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/admin/verify_login")
async def VerifyLogin(request : LoginRequest):

    hashed_password = data.get_admin_hash(request.username)

    if hashed_password is not None and data.verify_password(request.password,hashed_password) :
        #generate session token and decide expiry
        token = secrets.token_urlsafe(32)   #not really sure on what the 32 is
        admin_id = data.get_id(request.username)
        #save session
        data.create_session(admin_id,token,std_session_duration)
        print("New session started")
        #send token
        return {
            "access_token" : token,
            "expires_in" : 1800
        }
    else :
        #send error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@app.get("/admin")
def AdminLoginPage():
    try:
        with open("../client_side/adminDashboard.html", "r") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: adminDashboard.html not found!</h1>", status_code=404)
   
@app.get("/admin/add-product")
def AdminLoginPage():
    try:
        with open("../client_side/addProduct.html", "r") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: addProduct.html not found!</h1>", status_code=404)
   