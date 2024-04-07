
from fastapi import FastAPI, Request,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import BaseModel
from datetime import datetime
from typing import Any, List,Dict

app = FastAPI()
 
firebase_request_adapter = requests.Request()
cred = credentials.Certificate("./firebaseConfig.json")  
firebase_admin.initialize_app(cred)
db = firestore.client()



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
    uid = request.cookies.get('uid')
    error_message = 'No Error Here'
    user_token = None
    rooms_ref = db.collection("rooms")
    query = rooms_ref.where("createdBy", "==", uid)
    query_result = query.get()
    rooms_with_id = []
    for doc in query_result:
        room_id = doc.id
        room_data = doc.to_dict()
        room_with_id = {"id": room_id, **room_data}
        rooms_with_id.append(room_with_id)

    if id_token:
        try:
            user_token =google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as err:
            print(str(err))

    return templates.TemplateResponse('main.html',{'request' : request, 'user_token':user_token,"all_rooms":rooms_with_id,'error_message':error_message})


class Room(BaseModel):
    title: str
    description: str

def check_room_existence(title, createdBy):
    rooms_ref = db.collection("rooms")
    query = rooms_ref.where("title", "==", title.strip()).where("createdBy", "==", createdBy)
    query_result = query.limit(1).get()
    return len(query_result) > 0

@app.post("/rooms")
async def add_room(room: Room,request:Request):
    uid = request.cookies.get('uid')
    
    if not uid:
        raise HTTPException(status_code=401, detail="User not authenticated")

    if not room.title.strip() or not room.description.strip():
        raise HTTPException(status_code=400, detail="Title and description cannot be empty")

    if check_room_existence(room.title.strip(), uid):
        raise HTTPException(status_code=400, detail="A room with the same title already exists")

    rooms_ref = db.collection("rooms")
    createdByEmail = request.cookies.get('email')
    room_data = room.dict()
    room_data["createdBy"] = uid
    room_data["createdByEmail"] = createdByEmail
    room_data['days']=[]
    rooms_ref.add(room_data)
    return {"message": "Room added successfully"}

@app.get("/rooms",response_class=HTMLResponse)
async def rooms_read_root(request:Request):
    return templates.TemplateResponse('rooms.html',{'request' : request, "type":"add", 'room_data':{"title":"","description":"","id":""}})       
   

@app.get("/rooms/edit/{room_id}", response_class=HTMLResponse)
async def render_room_edit_page(request: Request, room_id: str):
    uid = request.cookies.get('uid')

    if not uid:
        raise HTTPException(status_code=401, detail="User not authenticated")

    room_ref = db.collection("rooms").document(room_id)
    room_doc = room_ref.get()
    if not room_doc.exists:
        raise HTTPException(status_code=404, detail="Room not found")

    room_data = room_doc.to_dict()
    room_data['id'] = room_id
    return templates.TemplateResponse('rooms.html',{'request' : request, "type":"edit", "room_data":room_data})   

@app.put("/rooms/edit/{room_id}")
async def edit_room(request: Request,room_id: str, updated_room: Room):
    uid = request.cookies.get('uid')

    if not uid:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Retrieve the room document from Firestore
    room_ref = db.collection("rooms").document(room_id)
    room_doc = room_ref.get()

    # Check if the room exists
    if not room_doc.exists:
        raise HTTPException(status_code=404, detail="Room not found")

    # Check if the room belongs to the authenticated user
    room_data = room_doc.to_dict()
    if room_data["createdBy"] != uid:
        raise HTTPException(status_code=403, detail="You are not authorized to edit this room")

    # Update the room details in Firestore
    room_ref.update({
        "title": updated_room.title,
        "description": updated_room.description
    })

    return {"message": "Room updated successfully"}

@app.delete("/rooms/delete/{room_id}")
async def delete_room(request: Request,room_id: str):
    uid = request.cookies.get('uid')
    if not uid:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Retrieve the room document from Firestore
    room_ref = db.collection("rooms").document(room_id)
    room_doc = room_ref.get()

    # Check if the room exists
    if not room_doc.exists:
        raise HTTPException(status_code=404, detail="Room not found")

    # Extract room data
    room_data = room_doc.to_dict()

    # Check if the authenticated user is the creator of the room
    if room_data["createdBy"] != uid:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this room")

    # Delete the room document from Firestore
    room_ref.delete()

    return {"message": "Room deleted successfully"}


@app.get("/booking",response_class=HTMLResponse)
async def booking_read_root(request:Request):
    uid =request.cookies.get('uid')
    rooms_ref = db.collection("rooms")
    query = rooms_ref.where("createdBy", "==", uid)
    query_result = query.get()
    rooms_with_id = []
    for doc in query_result:
        room_id = doc.id
        room_data = doc.to_dict()
        room_with_id = {"id": room_id, **room_data}
        rooms_with_id.append(room_with_id)
    return templates.TemplateResponse('booking.html',{'request' : request,"rooms":rooms_with_id})   

# Data model for booking
class Booking(BaseModel):
    room: str
    date: str
    time_from: str
    time_to: str


def validate_room(room_id: str) -> bool:
    room_ref = db.collection("rooms").document(room_id)
    return room_ref.get().exists

def create_booking_document(room: str, date: str, time_from: str, time_to: str) -> str:
    booking_data = {
        "room": room,
        "date": date,
        "time_from": time_from,
        "time_to": time_to
    }
    booking_ref = db.collection("bookings").add(booking_data)
    return booking_ref[1].id

def update_room_days(room_id: str, date_id: str,) -> None:
    room_ref = db.collection("rooms").document(room_id)
    room_ref.update({"days": firestore.ArrayUnion([date_id])})

def find_element_by_date(array: List[dict], date: Any) -> dict:
    try:
        for item in array:
            if item.get("day") == date:
                return item
        return None
    except Exception as e:
        raise e


def is_booking_overlapping(bookings: List[Dict[str, str]], new_time_from: str, new_time_to: str) -> bool:
  
    try:
        # Convert time strings to datetime objects for comparison
        new_start_time = datetime.strptime(new_time_from, "%H:%M")
        new_end_time = datetime.strptime(new_time_to, "%H:%M")

        for booking in bookings:
            # Convert existing booking times to datetime objects
            existing_start_time = datetime.strptime(booking["time_from"], "%H:%M")
            existing_end_time = datetime.strptime(booking["time_to"], "%H:%M")

            # Check for overlap
            if (new_start_time < existing_end_time and new_end_time > existing_start_time):
                return True  # Overlap detected

        return False  # No overlap detected
    except Exception as e:
        raise e

@app.post("/bookings/add")
async def add_booking(booking:Booking):
    try:
        # Check if room exists
        if not validate_room(booking.room):
            raise HTTPException(status_code=404, detail="Room not found")

        room_ref = db.collection("rooms").document(booking.room)
        room_data = room_ref.get().to_dict()
        if not room_data["days"]:
                booking_id = create_booking_document(booking.room, booking.date, booking.time_from, booking.time_to)
                day_data = {
                    "day": booking.date,
                    "bookings": [booking_id]
                }
                day_ref = db.collection("days").add(day_data)
                date_id = day_ref[1].id
                update_room_days(booking.room, date_id)
                return {"message": "Booking added successfully"}
        
        else:
            days_query = db.collection("days").where(f"__name__", "in", room_data["days"])
            days_docs = days_query.stream()
            documents = []
            for doc in days_docs:
                elem =doc.to_dict()
                elem['id']=doc.id
                documents.append((elem))

            matching_date_elements = find_element_by_date(documents,booking.date)
            match_date_id = matching_date_elements['id']
            if matching_date_elements:
                if not matching_date_elements["bookings"]:
                    booking_id = create_booking_document(booking.room, booking.date, booking.time_from, booking.time_to)
                    day_data = {
                            "day": booking.date,
                            "bookings": [booking_id]
                    }
                    day_ref = db.collection("days").add(day_data)
                    date_id = day_ref[1].id

                    update_room_days(booking.room, date_id)
                    return {"message": "Booking added successfully"}

                else:
                    days_query = db.collection("bookings").where(f"__name__", "in", matching_date_elements["bookings"])
                    days_docs = days_query.stream()
                    booking_documents = []
                    for doc in days_docs:
                        booking_documents.append(doc.to_dict())

                    check_over_lapping = is_booking_overlapping(booking_documents,booking.time_from , booking.time_to)

                    if check_over_lapping:
                        raise HTTPException(status_code=400, detail="Already booked the room in the same time")
                    
                    else:
                        booking_id = create_booking_document(booking.room, booking.date, booking.time_from, booking.time_to)
                        day_ref = db.collection("days").document(match_date_id)
                        # Atomically update the booking array by appending the new booking ID
                        day_ref.update({
                            "bookings": firestore.ArrayUnion([booking_id])
                        })
                        print('date updated')
  
            else:
                booking_id = create_booking_document(booking.room, booking.date, booking.time_from, booking.time_to)
                day_data = {
                    "day": booking.date,
                    "bookings": [booking_id]
                }
                day_ref = db.collection("days").add(day_data)
                date_id = day_ref[1].id
                update_room_days(booking.room, date_id)
                return {"message": "Booking added successfully"}



    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
