import json
from os import getenv
from fastapi import APIRouter, Depends, HTTPException, Header
from jwt import InvalidTokenError, PyJWT
from pymongo.database import Database
from dotenv import load_dotenv
from dependencies.verify_user import verifyUser
from dependencies.database import get_db
load_dotenv
getRouter = APIRouter()

@getRouter.get("/user/")
async def userInfo(user: dict = Depends(verifyUser)):
    user.pop("password")
    user.pop("_id")
    return json.dumps(user)
