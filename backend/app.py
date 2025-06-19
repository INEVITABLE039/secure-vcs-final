# 📁 File: backend/app.py (FastAPI Backend)
from fastapi import FastAPI, Depends, HTTPException, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
import shutil

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- MODELS ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50))
    email = Column(String(100), unique=True, index=True)
    password = Column(String(100))
    role = Column(String(50))

class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(Text)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    action = Column(String(200))
    timestamp = Column(DateTime, default=datetime.utcnow)

class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    start_time = Column(DateTime)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    chatroom_id = Column(Integer)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTES ---
@app.post("/signup")
def signup_user(data: dict = Body(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == data["email"]).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        role=data["role"]
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully"}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.put("/users/{email}")
def update_user(email: str, data: dict = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = data["username"]
    user.role = data["role"]
    db.commit()
    return {"message": "User updated"}

@app.delete("/users/{email}")
def delete_user(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

@app.get("/user-role/{username}")
def get_user_role(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"role": user.role}

@app.post("/announcements/")
def create_announcement(data: dict = Body(...), db: Session = Depends(get_db)):
    new_announcement = Announcement(
        title=data["title"],
        content=data["content"],
        created_by=data.get("created_by", "admin")
    )
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    return {"message": "Announcement posted", "announcement": new_announcement}

@app.get("/announcements/")
def get_announcements(db: Session = Depends(get_db)):
    return db.query(Announcement).order_by(Announcement.created_at.desc()).all()

@app.get("/logs/")
def get_logs(db: Session = Depends(get_db)):
    return db.query(ActivityLog).order_by(ActivityLog.timestamp.desc()).all()

@app.post("/meetings")
def create_meeting(data: dict = Body(...), db: Session = Depends(get_db)):
    meeting = Meeting(title=data["title"], start_time=datetime.fromisoformat(data["start_time"]))
    db.add(meeting)
    db.commit()
    return {"message": "Meeting created"}

@app.post("/messages")
def send_message(data: dict = Body(...), db: Session = Depends(get_db)):
    msg = Message(chatroom_id=data["chatroom_id"], content=data["content"])
    db.add(msg)
    db.commit()
    return {"message": "Message sent"}

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "File uploaded", "filename": file.filename}
