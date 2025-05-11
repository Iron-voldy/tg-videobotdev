from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import uuid
from config.settings import DATABASE_URL

# Create database engine
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Define models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String, nullable=True)
    free_generations = Column(Integer, default=3)
    stars = Column(Integer, default=0)
    referral_code = Column(String, unique=True)
    referred_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    free_plan_expires_at = Column(DateTime)
    
    def __init__(self, user_id, username=None):
        self.user_id = user_id
        self.username = username
        self.free_generations = 3
        self.stars = 0
        self.referral_code = str(uuid.uuid4())[:8]
        self.free_plan_expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=30)

class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    prompt = Column(String)
    video_url = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    used_free = Column(Boolean, default=False)
    used_stars = Column(Integer, default=0)

# Create tables
Base.metadata.create_all(engine)

# Create session factory
Session = sessionmaker(bind=engine)

def get_session():
    return Session()