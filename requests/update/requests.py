import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, File, UploadFile,APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Dict, Optional
from dependencies.database import users_collection, messages_collection, groups_collection
from models import UserCreate, MessageCreate, GroupCreate
import uuid
from datetime import datetime
import os

router = APIRouter()

# WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Helper functions
def get_user_by_username(username: str):
    return users_collection.find_one({"username": username})

def create_user(username: str, password: str):
    user_id = str(uuid.uuid4())
    user = {"id": user_id, "username": username, "password": password}
    users_collection.insert_one(user)
    return user_id

# Authentication endpoints
@router.post("/register")
async def register(user: UserCreate):
    if get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    user_id = create_user(user.username, user.password)
    return {"user_id": user_id}

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"access_token": user["id"], "token_type": "bearer"}

# WebSocket endpoint
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    active_connections[user_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            await broadcast_message(
                sender_id=user_id,
                receiver_id=message_data.get("receiver_id"),
                group_id=message_data.get("group_id"),
                content=message_data["content"],
                is_voice=message_data.get("is_voice", False),
            )
    except WebSocketDisconnect:
        del active_connections[user_id]

async def broadcast_message(sender_id: str, receiver_id: Optional[str], group_id: Optional[str], content: str, is_voice: bool = False):
    message_id = str(uuid.uuid4())
    message = {
        "id": message_id,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "group_id": group_id,
        "content": content,
        "is_voice": is_voice,
        "timestamp": datetime.now(),
    }
    messages_collection.insert_one(message)

    if receiver_id:
        if receiver_id in active_connections:
            await active_connections[receiver_id].send_text(json.dumps(message))
    elif group_id:
        group = groups_collection.find_one({"id": group_id})
        if group:
            for member in group["members"]:
                if member in active_connections:
                    await active_connections[member].send_text(json.dumps(message))

# Voice message endpoint
@router.post("/upload_voice/")
async def upload_voice(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = f"voice_messages/{file_id}.wav"
    os.makedirs("voice_messages", exist_ok=True)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return {"file_id": file_id}

# Group endpoints
@router.post("/create_group/")
async def create_group(group: GroupCreate):
    group_id = str(uuid.uuid4())
    group_data = {"id": group_id, "name": group.name, "members": group.members}
    groups_collection.insert_one(group_data)
    return {"group_id": group_id}

@router.get("/groups/{user_id}")
async def get_groups(user_id: str):
    groups = groups_collection.find({"members": user_id})
    return {"groups": [group for group in groups]}