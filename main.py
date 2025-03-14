from fastapi import FastAPI
from requests.post.requests import postRouter
from requests.get.requests import getRouter
from requests.delete.requests import deleteRouter
app = FastAPI()

app.include_router(postRouter)
app.include_router(getRouter)
app.include_router(deleteRouter)