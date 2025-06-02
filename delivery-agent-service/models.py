from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    cuisine_type = Column(String(100))
    is_online = Column(Boolean, default=True)
    rating = Column(DECIMAL(3,2), default=0.0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class DeliveryAgent(Base):
    __tablename__ = "delivery_agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    vehicle_type = Column(String(50))
    is_available = Column(Boolean, default=True)
    rating = Column(DECIMAL(3,2), default=0.0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    restaurant_id = Column(Integer)
    delivery_agent_id = Column(Integer)
    status = Column(String(50), default="pending")
    total_amount = Column(DECIMAL(10,2), nullable=False)
    delivery_address = Column(Text)
    special_instructions = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)
