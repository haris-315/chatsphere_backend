from fastapi import HTTPException, Depends, APIRouter
from dependencies.database import get_db
from dependencies.upload_to_cloudinary import delete_image
from dependencies.verify_user import verifyUser
from pymongo.database import Database

deleteRouter = APIRouter()


@deleteRouter.delete("/delete-user")
async def register(user: dict = Depends(verifyUser),db: Database = Depends(get_db)):
    try:
        delete_image(user.get("public_id"))
        db.get_collection("users").delete_one({"id":user.get("id")})
        return {"msg": f"Successfully delted user {user.get('id')}"}
    except Exception as e:
        raise HTTPException(status_code=502,detail="Unable to delete user.")
    

       

