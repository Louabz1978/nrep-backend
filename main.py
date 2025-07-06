from fastapi import FastAPI

from app.routers.auth.auth_router import router as auth_router
from app.routers.users.users_router import router as users_route
from app.routers.agencies.agencies_router import router as agency_route
from app.routers.properties.properties_router import router as property_route

from app.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

from app.models import *

app = FastAPI()

Base.metadata.create_all(bind=engine) 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_route)
app.include_router(agency_route)
app.include_router(property_route)

