from pydantic import BaseModel, EmailStr
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

class RestaurantResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    phone: Optional[str]
    cuisine_type: Optional[str]
    is_online: bool
    rating: Optional[Decimal]
    
    class Config:
        from_attributes = True

class MenuItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    is_available: bool
    category: Optional[str]
    
    class Config:
        from_attributes = True

class RestaurantWithMenuResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    phone: Optional[str]
    cuisine_type: Optional[str]
    is_online: bool
    rating: Optional[Decimal]
    menu_items: List[MenuItemResponse]
    
    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int

class OrderCreate(BaseModel):
    user_id: int
    restaurant_id: int
    delivery_address: str
    special_instructions: Optional[str] = None
    items: List[OrderItemCreate]

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

class RatingCreate(BaseModel):
    rating: int
    comment: Optional[str] = None

class RatingResponse(BaseModel):
    id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
