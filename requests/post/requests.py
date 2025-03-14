import json
from fastapi import FastAPI, Form, WebSocket, WebSocketDisconnect, HTTPException, Depends, File, UploadFile,APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from h11 import Response
from pydantic import BaseModel
from typing import List, Dict, Optional
from jwt import PyJWT
from dependencies.database import get_db
from models import UserCreate, MessageCreate, GroupCreate
from pymongo.database import Database
import uuid
from dotenv import load_dotenv
from datetime import datetime
import os

from dependencies import upload_to_cloudinary

load_dotenv()
postRouter = APIRouter()

active_connections: Dict[str, WebSocket] = {}


def get_user_by_username(username: str,usersCollection: Database):
    print(usersCollection.find_one({"username": username}))
    return usersCollection.find_one({"username": username})

def create_user(username: str, password: str,user_id: str,dp_info: dict,usersCollection: Database):
    
    user = {"id": user_id, "username": username, "password": password, "dp": dp_info.get("url"), "public_id" : dp_info.get("public_id"),"friends": [],"blocks" : []}
    usersCollection.insert_one(user)
    return user_id

@postRouter.post("/register")
async def register(username: str = Form(...),password: str = Form(), dp: UploadFile = File(...),db: Database = Depends(get_db),):
    usersCollection = db.get_collection("users")
    if get_user_by_username(username,usersCollection=usersCollection):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_id = str(uuid.uuid4())
    dp_info = upload_to_cloudinary.upload_to_cloudinary(file=dp,folder=f"chatsphere/profiles/{user_id}")

    user_id = create_user(username=username,password=password,dp_info=dp_info,user_id=user_id,usersCollection=usersCollection)

    return {"user_id": user_id,"msg": "Registration Successfull."}

@postRouter.post("/signin")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),db: Database = Depends(get_db)):
    usersCollection = db.get_collection("users")
    user = get_user_by_username(form_data.username,usersCollection=usersCollection)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    jwt = PyJWT().encode(payload={"uid" : user.get("id")},key=os.getenv("JWT_KEY"),algorithm='HS256')
    return {"token": jwt,"msg": "SignIn Succeed"}

@postRouter.post("/add-friend/")
async def addFriend():
    pass

# # WebSocket endpoint
# @postRouter.websocket("/ws/{user_id}")
# async def websocket_endpoint(websocket: WebSocket, user_id: str):
#     await websocket.accept()
#     active_connections[user_id] = websocket
#     try:
#         while True:
#             data = await websocket.receive_text()
#             message_data = json.loads(data)
#             await broadcast_message(
#                 sender_id=user_id,
#                 receiver_id=message_data.get("receiver_id"),
#                 group_id=message_data.get("group_id"),
#                 content=message_data["content"],
#                 is_voice=message_data.get("is_voice", False),
#             )
#     except WebSocketDisconnect:
#         del active_connections[user_id]

# async def broadcast_message(sender_id: str, receiver_id: Optional[str], group_id: Optional[str], content: str, is_voice: bool = False):
#     message_id = str(uuid.uuid4())
#     message = {
#         "id": message_id,
#         "sender_id": sender_id,
#         "receiver_id": receiver_id,
#         "group_id": group_id,
#         "content": content,
#         "is_voice": is_voice,
#         "timestamp": datetime.now(),
#     }
#     messages_collection.insert_one(message)

#     if receiver_id:
#         if receiver_id in active_connections:
#             await active_connections[receiver_id].send_text(json.dumps(message))
#     elif group_id:
#         group = groups_collection.find_one({"id": group_id})
#         if group:
#             for member in group["members"]:
#                 if member in active_connections:
#                     await active_connections[member].send_text(json.dumps(message))

# # Voice message endpoint
# @postRouter.post("/upload_voice/")
# async def upload_voice(file: UploadFile = File(...)):
#     file_id = str(uuid.uuid4())
#     file_path = f"voice_messages/{file_id}.wav"
#     os.makedirs("voice_messages", exist_ok=True)
#     with open(file_path, "wb") as buffer:
#         buffer.write(file.file.read())
#     return {"file_id": file_id}

# # Group endpoints
# @postRouter.post("/create_group/")
# async def create_group(group: GroupCreate):
#     group_id = str(uuid.uuid4())
#     group_data = {"id": group_id, "name": group.name, "members": group.members}
#     groups_collection.insert_one(group_data)
#     return {"group_id": group_id}

# @postRouter.get("/groups/{user_id}")
# async def get_groups(user_id: str):
#     groups = groups_collection.find({"members": user_id})
#     return {"groups": [group for group in groups]}