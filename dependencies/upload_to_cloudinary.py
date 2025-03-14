import os
from tkinter.tix import STATUS
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from fastapi import File, HTTPException, UploadFile

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

def upload_to_cloudinary(file: UploadFile = File(...), folder: str = "chatsphere"):
    """
    Dependency to upload a file to a specific folder in Cloudinary.
    """
    try:
        # Read file content
        file_bytes = file.file.read()

        # Upload file using the `file` parameter (Cloudinary expects a file-like object)
        result = cloudinary.uploader.upload(file_bytes, folder=folder)

        return {"url": result["secure_url"], "public_id": result["public_id"]}
    
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error uploading file to Cloudinary: {e}")
    
def delete_image(public_id: str):
    """
    Deletes an image from Cloudinary using its public_id.
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        if result["result"] == "ok":
            return {"message": "Image deleted successfully", "public_id": public_id}
    except Exception as e:
        raise "there was an error deleting the image: {e}"