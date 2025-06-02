from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
import httpx
from decimal import Decimal

from database import get_db
from models import Restaurant, MenuItem, Order, OrderItem, OrderRating, AgentRating, User
from schemas import (
    RestaurantResponse, 
    RestaurantWithMenuResponse, 
    OrderCreate, 
    OrderResponse, 
    RatingCreate, 
    RatingResponse
)

app = FastAPI(title="User Service", description="Food Delivery User Service API", version="1.0.0")

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "User Service is running"}

@app.get("/restaurants", response_model=List[RestaurantWithMenuResponse], tags=["Restaurants"])
def get_online_restaurants(db: Session = Depends(get_db)):
    """Get all restaurants that are currently online with their menu items"""
    restaurants = db.query(Restaurant).options(
        joinedload(Restaurant.menu_items)
    ).filter(Restaurant.is_online == True).all()
    
    # Convert to response format
    result = []
    for restaurant in restaurants:
        menu_items = db.query(MenuItem).filter(
            MenuItem.restaurant_id == restaurant.id,
            MenuItem.is_available == True
        ).all()
        
        restaurant_dict = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "phone": restaurant.phone,
            "cuisine_type": restaurant.cuisine_type,
            "is_online": restaurant.is_online,
            "rating": restaurant.rating,
            "menu_items": menu_items
        }
        result.append(restaurant_dict)
    
    return result

@app.post("/orders", response_model=OrderResponse, tags=["Orders"])
async def place_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """Place a new order"""
    
    # Verify user exists
    user = db.query(User).filter(User.id == order_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify restaurant exists and is online
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == order_data.restaurant_id,
        Restaurant.is_online == True
    ).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found or offline")
    
    # Calculate total amount and verify menu items
    total_amount = Decimal('0.00')
    order_items_data = []
    
    for item in order_data.items:
        menu_item = db.query(MenuItem).filter(
            MenuItem.id == item.menu_item_id,
            MenuItem.restaurant_id == order_data.restaurant_id,
            MenuItem.is_available == True
        ).first()
        
        if not menu_item:
            raise HTTPException(
                status_code=404, 
                detail=f"Menu item {item.menu_item_id} not found or unavailable"
            )
        
        item_total = menu_item.price * item.quantity
        total_amount += item_total
        
        order_items_data.append({
            "menu_item_id": item.menu_item_id,
            "quantity": item.quantity,
            "price": menu_item.price
        })
    
    # Create order
    new_order = Order(
        user_id=order_data.user_id,
        restaurant_id=order_data.restaurant_id,
        total_amount=total_amount,
        delivery_address=order_data.delivery_address,
        special_instructions=order_data.special_instructions,
        status="pending"
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Create order items
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            **item_data
        )
        db.add(order_item)
    
    db.commit()
    
    # Notify restaurant service about new order
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://restaurant-service:8000/orders/notify",
                json={"order_id": new_order.id}
            )
    except Exception as e:
        # Log error but don't fail the order creation
        print(f"Failed to notify restaurant service: {e}")
    
    return new_order

@app.post("/orders/{order_id}/rate", response_model=RatingResponse, tags=["Ratings"])
def rate_order(order_id: int, rating_data: RatingCreate, user_id: int, db: Session = Depends(get_db)):
    """Rate an order"""
    
    # Verify order exists and belongs to user
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user already rated this order
    existing_rating = db.query(OrderRating).filter(
        OrderRating.order_id == order_id,
        OrderRating.user_id == user_id
    ).first()
    if existing_rating:
        raise HTTPException(status_code=400, detail="Order already rated")
    
    # Validate rating value
    if rating_data.rating < 1 or rating_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Create rating
    new_rating = OrderRating(
        order_id=order_id,
        user_id=user_id,
        rating=rating_data.rating,
        comment=rating_data.comment
    )
    
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    
    return new_rating

@app.post("/agents/{agent_id}/rate", response_model=RatingResponse, tags=["Ratings"])
def rate_delivery_agent(agent_id: int, rating_data: RatingCreate, user_id: int, order_id: int, db: Session = Depends(get_db)):
    """Rate a delivery agent"""
    
    # Verify order exists and belongs to user
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id,
        Order.delivery_agent_id == agent_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or agent not assigned to this order")
    
    # Check if user already rated this agent for this order
    existing_rating = db.query(AgentRating).filter(
        AgentRating.delivery_agent_id == agent_id,
        AgentRating.user_id == user_id,
        AgentRating.order_id == order_id
    ).first()
    if existing_rating:
        raise HTTPException(status_code=400, detail="Agent already rated for this order")
    
    # Validate rating value
    if rating_data.rating < 1 or rating_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Create rating
    new_rating = AgentRating(
        delivery_agent_id=agent_id,
        user_id=user_id,
        order_id=order_id,
        rating=rating_data.rating,
        comment=rating_data.comment
    )
    
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    
    return new_rating

@app.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
def get_order(order_id: int, user_id: int, db: Session = Depends(get_db)):
    """Get order details"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
