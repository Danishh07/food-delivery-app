from pydantic import BaseModel, EmailStr
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class RestaurantCreate(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    cuisine_type: Optional[str] = None

class RestaurantResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    phone: Optional[str]
    cuisine_type: Optional[str]
    is_online: bool
    rating: Optional[Decimal]
    created_at: datetime
    
    class Config:
        from_attributes = True

class MenuItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    category: Optional[str] = None
    is_available: bool = True

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None

class MenuItemResponse(BaseModel):
    id: int
    restaurant_id: int
    name: str
    description: Optional[str]
    price: Decimal
    is_available: bool
    category: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class MenuUpdate(BaseModel):
    items: List[MenuItemCreate]

class StatusUpdate(BaseModel):
    is_online: bool

class OrderNotification(BaseModel):
    order_id: int

class OrderAction(BaseModel):
    action: str  # "accept" or "reject"

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
    
    class Config:
        from_attributes = True
