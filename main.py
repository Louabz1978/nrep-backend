import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers.auth.auth_router import router as auth_router
from app.routers.users.users_router import router as users_route
from app.routers.agencies.agencies_router import router as agency_route
from app.routers.properties.properties_router import router as property_route
from app.routers.roles.roles_router import router as roles_router
from app.routers.addresses.addresses_router import router as addresses_router
from app.routers.consumers.consumer_router import router as consumer_router
from app.routers.licenses.licenses_router import router as license_router
from app.routers.cities.cities_router import router as city_router
from app.routers.counties.counties_router import router as county_router
from app.routers.areas.areas_router import router as area_router

from app.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

from app.models import *

app = FastAPI()

Base.metadata.create_all(bind=engine) 

UPLOAD_DIR = os.path.join(os.getcwd(), "static")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_route)
app.include_router(agency_route)
app.include_router(property_route)
app.include_router(roles_router)
app.include_router(addresses_router)
app.include_router(consumer_router)
app.include_router(license_router)

app.include_router(city_router)
app.include_router(county_router)
app.include_router(area_router)
