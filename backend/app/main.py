from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base

from app.api.user import router as user_router


from app.api.event_theme import router as event_theme_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)



app.include_router(event_theme_router, prefix="/api")
app.include_router(user_router, prefix="/api/users")
