from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import httpx
from datetime import datetime

from database import get_db
from models import Restaurant, MenuItem, Order, DeliveryAgent
from schemas import (
    RestaurantCreate, 
    RestaurantResponse, 
    MenuItemCreate, 
    MenuItemUpdate,
    MenuItemResponse, 
    MenuUpdate, 
    StatusUpdate, 
    OrderNotification,
    OrderAction,
    OrderResponse
)

app = FastAPI(title="Restaurant Service", description="Food Delivery Restaurant Service API", version="1.0.0")

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "Restaurant Service is running"}

@app.post("/restaurants", response_model=RestaurantResponse, tags=["Restaurants"])
def create_restaurant(restaurant_data: RestaurantCreate, db: Session = Depends(get_db)):
    """Create a new restaurant"""
    new_restaurant = Restaurant(
        name=restaurant_data.name,
        address=restaurant_data.address,
        phone=restaurant_data.phone,
        cuisine_type=restaurant_data.cuisine_type
    )
    
    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)
    
    return new_restaurant

@app.get("/restaurants/{restaurant_id}", response_model=RestaurantResponse, tags=["Restaurants"])
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    """Get restaurant details"""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    return restaurant

@app.put("/restaurants/{restaurant_id}/status", response_model=RestaurantResponse, tags=["Restaurants"])
def update_restaurant_status(restaurant_id: int, status_data: StatusUpdate, db: Session = Depends(get_db)):
    """Update restaurant online/offline status"""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    restaurant.is_online = status_data.is_online
    db.commit()
    db.refresh(restaurant)
    
    return restaurant

@app.post("/restaurants/{restaurant_id}/menu", response_model=List[MenuItemResponse], tags=["Menu"])
def add_menu_items(restaurant_id: int, menu_data: MenuUpdate, db: Session = Depends(get_db)):
    """Add menu items to a restaurant"""
    
    # Verify restaurant exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    created_items = []
    for item_data in menu_data.items:
        new_item = MenuItem(
            restaurant_id=restaurant_id,
            name=item_data.name,
            description=item_data.description,
            price=item_data.price,
            category=item_data.category,
            is_available=item_data.is_available
        )
        db.add(new_item)
        created_items.append(new_item)
    
    db.commit()
    for item in created_items:
        db.refresh(item)
    
    return created_items

@app.put("/restaurants/{restaurant_id}/menu/{item_id}", response_model=MenuItemResponse, tags=["Menu"])
def update_menu_item(restaurant_id: int, item_id: int, item_data: MenuItemUpdate, db: Session = Depends(get_db)):
    """Update a menu item"""
    
    menu_item = db.query(MenuItem).filter(
        MenuItem.id == item_id,
        MenuItem.restaurant_id == restaurant_id
    ).first()
    
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Update only provided fields
    if item_data.name is not None:
        menu_item.name = item_data.name
    if item_data.description is not None:
        menu_item.description = item_data.description
    if item_data.price is not None:
        menu_item.price = item_data.price
    if item_data.category is not None:
        menu_item.category = item_data.category
    if item_data.is_available is not None:
        menu_item.is_available = item_data.is_available
    
    db.commit()
    db.refresh(menu_item)
    
    return menu_item

@app.get("/restaurants/{restaurant_id}/menu", response_model=List[MenuItemResponse], tags=["Menu"])
def get_restaurant_menu(restaurant_id: int, db: Session = Depends(get_db)):
    """Get all menu items for a restaurant"""
    
    # Verify restaurant exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    menu_items = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).all()
    return menu_items

@app.post("/orders/notify", tags=["Orders"])
async def receive_order_notification(notification: OrderNotification, db: Session = Depends(get_db)):
    """Receive notification about new order"""
    
    # Check if order already exists
    existing_order = db.query(Order).filter(Order.id == notification.order_id).first()
    if existing_order:
        return {"message": f"Order {notification.order_id} already exists"}
    
    # Fetch order details from user service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://user-service:8000/orders/{notification.order_id}")
            if response.status_code == 200:
                order_data = response.json()
                  # Create order in restaurant service database
                new_order = Order(
                    id=order_data["id"],
                    user_id=order_data["user_id"],
                    restaurant_id=order_data["restaurant_id"],
                    status=order_data["status"],
                    total_amount=order_data["total_amount"],
                    delivery_address=order_data["delivery_address"],
                    special_instructions=order_data.get("special_instructions"),
                    created_at=datetime.fromisoformat(order_data["created_at"]),
                    updated_at=datetime.utcnow()
                )
                
                db.add(new_order)
                db.commit()
                db.refresh(new_order)
                
                return {"message": f"Order {notification.order_id} synchronized successfully"}
            else:
                raise HTTPException(status_code=400, detail="Failed to fetch order details")
    except Exception as e:
        print(f"Failed to sync order: {e}")
        raise HTTPException(status_code=400, detail="Failed to synchronize order")
    
    return {"message": f"Order {notification.order_id} notification received"}

@app.put("/orders/{order_id}/accept", response_model=OrderResponse, tags=["Orders"])
async def accept_order(order_id: int, db: Session = Depends(get_db)):
    """Accept an order and assign delivery agent"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order cannot be accepted")
    
    # Find available delivery agent
    available_agent = db.query(DeliveryAgent).filter(
        DeliveryAgent.is_available == True
    ).first()
    
    if not available_agent:
        raise HTTPException(status_code=400, detail="No delivery agents available")
    
    # Update order status and assign agent
    order.status = "accepted"
    order.delivery_agent_id = available_agent.id
    order.updated_at = datetime.utcnow()
    
    # Mark agent as unavailable
    available_agent.is_available = False
    
    db.commit()
    db.refresh(order)
    
    # Notify delivery agent service
    try:
        print(f"RESTAURANT: Assigning order {order_id} to agent {available_agent.id}")
        assignment_data = {
            "order_id": order_id,
            "agent_id": available_agent.id
        }
        print(f"RESTAURANT: Assignment data: {assignment_data}")
        
        async with httpx.AsyncClient() as client:
            # Import config here to avoid circular imports
            import sys
            sys.path.append('..') 
            try:
                from config import DELIVERY_SERVICE_URL, DELIVERY_SERVICE_DOCKER_URL
            except ImportError:
                # Default URLs if config can't be imported
                DELIVERY_SERVICE_URL = "http://localhost:8003"
                DELIVERY_SERVICE_DOCKER_URL = "http://delivery-agent-service:8000"
                
            # Try primary URL first (from environment or localhost)
            try:
                delivery_url = f"{DELIVERY_SERVICE_URL}/orders/assign"
                print(f"RESTAURANT: Trying to notify delivery service at: {delivery_url}")
                response = await client.post(
                    delivery_url,
                    json=assignment_data,
                    timeout=5.0
                )
                print(f"RESTAURANT: Notified delivery service: {response.status_code}")
                print(f"RESTAURANT: Response: {response.text}")
            except Exception as primary_e:
                print(f"RESTAURANT: Failed to notify primary delivery service: {primary_e}")
                # Fallback to Docker service name
                try:
                    response = await client.post(
                        f"{DELIVERY_SERVICE_DOCKER_URL}/orders/assign",
                        json=assignment_data
                    )
                    print(f"RESTAURANT: Notified Docker delivery service: {response.status_code}")
                except Exception as docker_e:
                    print(f"RESTAURANT: Failed to notify Docker delivery service: {docker_e}")
    except Exception as e:
        print(f"RESTAURANT: Failed to notify any delivery agent service: {e}")
    
    return order

@app.put("/orders/{order_id}/reject", response_model=OrderResponse, tags=["Orders"])
def reject_order(order_id: int, db: Session = Depends(get_db)):
    """Reject an order"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order cannot be rejected")
    
    order.status = "rejected"
    order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return order

@app.get("/orders/pending", response_model=List[OrderResponse], tags=["Orders"])
def get_pending_orders(restaurant_id: int, db: Session = Depends(get_db)):
    """Get all pending orders for a restaurant"""
    
    orders = db.query(Order).filter(
        Order.restaurant_id == restaurant_id,
        Order.status == "pending"
    ).all()
    
    return orders

@app.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order details"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
