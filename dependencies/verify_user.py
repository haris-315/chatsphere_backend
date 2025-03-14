
from os import getenv
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Header
from jwt import InvalidTokenError, PyJWT
from pymongo.database import Database

from dependencies.database import get_db
load_dotenv(".env")
def verifyUser(token: str = Header(None,alias="Authorization"),db: Database = Depends(get_db)):
    try:
        if (token):
            requestInfo = PyJWT().decode(token,key=getenv("JWT_KEY"),algorithms=['HS256'])
            user = db.get_collection("users").find_one({"id": requestInfo.get("uid")})
            if (not user):
                raise HTTPException(status_code=404, detail="User not found")
            return user
        else:
            raise HTTPException(status_code=400,detail="No Token")

    except InvalidTokenError as e:
        print(e)
        raise HTTPException(status_code=400,detail="Invalid Token")