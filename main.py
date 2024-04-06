
from fastapi import FastAPI, Request, Response, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests

app = FastAPI()

firebase_request_adapter = requests.Request()


app.mount('/static',StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


@app.get("/signup",response_class=HTMLResponse)
async def signup_read_root(request:Request):
    return templates.TemplateResponse('signup.html',{'request' : request,})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse('login.html',{'request' : request,})




@app.get("/",response_class=HTMLResponse)
async def read_root(request:Request): 

    id_token = request.cookies.get('token')
    error_message = 'No Error Here'
    user_token = None
    if id_token:
        try:
            user_token =google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as err:
            print(str(err))

    return templates.TemplateResponse('main.html',{'request' : request, 'user_token':user_token,'error_message':error_message})

# @app.get("/login",response_class=HTMLResponse)
# async def login_read_root(request:Request):
#     return templates.TemplateResponse('login.html',{'request' : request, 'name':'jhone doe','number':'1234241'})





@app.get("/signup",response_class=HTMLResponse)
async def signup_read_root(request:Request):
    return templates.TemplateResponse('signup.html',{'request' : request, 'name':'jhone doe','number':'1234241'})

@app.get("/booking",response_class=HTMLResponse)
async def booking_read_root(request:Request):
    return templates.TemplateResponse('booking.html',{'request' : request, 'name':'jhone doe','number':'1234241'})   

@app.get("/rooms",response_class=HTMLResponse)
async def rooms_read_root(request:Request):
    return templates.TemplateResponse('rooms.html',{'request' : request, 'name':'jhone doe','number':'1234241'})       