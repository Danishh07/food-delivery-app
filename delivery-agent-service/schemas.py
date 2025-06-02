from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal
from datetime import datetime

class AgentCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    vehicle_type: str

class AgentResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    vehicle_type: str
    is_available: bool
    rating: Optional[Decimal]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AgentStatusUpdate(BaseModel):
    is_available: bool

class OrderStatusUpdate(BaseModel):
    status: str

class OrderAssignment(BaseModel):
    order_id: int
    agent_id: int

class OrderResponse(BaseModel):
    id: int
    user_id: int
    restaurant_id: int
    delivery_agent_id: Optional[int]
    status: str
    total_amount: Decimal
    delivery_address: str
    special_instructions: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
