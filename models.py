from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    username: str

class MessageCreate(BaseModel):
    sender_id: str
    receiver_id: Optional[str] = None
    group_id: Optional[str] = None
    content: str
    is_voice: bool = False

class Message(BaseModel):
    id: str
    sender_id: str
    receiver_id: Optional[str] = None
    group_id: Optional[str] = None
    content: str
    is_voice: bool
    timestamp: datetime

class GroupCreate(BaseModel):
    name: str
    members: List[str]

class Group(BaseModel):
    id: str
    name: str
    members: List[str]