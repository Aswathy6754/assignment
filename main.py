
from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()


app.mount('/static',StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


@app.get("/",response_class=HTMLResponse)
async def read_root(request:Request):
    return templates.TemplateResponse('main.html',{'request' : request, 'name':'jhone doe','number':'1234241'})

@app.get("/login",response_class=HTMLResponse)
async def login_read_root(request:Request):
    return templates.TemplateResponse('login.html',{'request' : request, 'name':'jhone doe','number':'1234241'})

@app.get("/signup",response_class=HTMLResponse)
async def signup_read_root(request:Request):
    return templates.TemplateResponse('signup.html',{'request' : request, 'name':'jhone doe','number':'1234241'})

@app.get("/booking",response_class=HTMLResponse)
async def booking_read_root(request:Request):
    return templates.TemplateResponse('booking.html',{'request' : request, 'name':'jhone doe','number':'1234241'})   

@app.get("/rooms",response_class=HTMLResponse)
async def rooms_read_root(request:Request):
    return templates.TemplateResponse('rooms.html',{'request' : request, 'name':'jhone doe','number':'1234241'})       