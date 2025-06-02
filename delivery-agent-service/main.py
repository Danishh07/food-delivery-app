from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import httpx

from database import get_db
from models import DeliveryAgent, Order
from schemas import (
    AgentCreate, 
    AgentResponse, 
    AgentStatusUpdate, 
    OrderStatusUpdate,
    OrderAssignment,
    OrderResponse
)

app = FastAPI(title="Delivery Agent Service", description="Food Delivery Agent Service API", version="1.0.0")

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "Delivery Agent Service is running"}

@app.post("/agents", response_model=AgentResponse, tags=["Agents"])
def register_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Register a new delivery agent"""
    
    # Check if email already exists
    existing_agent = db.query(DeliveryAgent).filter(DeliveryAgent.email == agent_data.email).first()
    if existing_agent:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_agent = DeliveryAgent(
        name=agent_data.name,
        email=agent_data.email,
        phone=agent_data.phone,
        vehicle_type=agent_data.vehicle_type
    )
    
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    
    return new_agent

@app.get("/agents", response_model=List[AgentResponse], tags=["Agents"])
def get_all_agents(db: Session = Depends(get_db)):
    """Get all delivery agents"""
    agents = db.query(DeliveryAgent).all()
    return agents

@app.get("/agents/{agent_id}", response_model=AgentResponse, tags=["Agents"])
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Get delivery agent details"""
    agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent

@app.put("/agents/{agent_id}/status", response_model=AgentResponse, tags=["Agents"])
def update_agent_status(agent_id: int, status_data: AgentStatusUpdate, db: Session = Depends(get_db)):
    """Update delivery agent availability status"""
    agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.is_available = status_data.is_available
    db.commit()
    db.refresh(agent)
    
    return agent

@app.get("/agents/available", response_model=List[AgentResponse], tags=["Agents"])
def get_available_agents(db: Session = Depends(get_db)):
    """Get all available delivery agents"""
    agents = db.query(DeliveryAgent).filter(DeliveryAgent.is_available == True).all()
    return agents

@app.post("/orders/assign", tags=["Orders"])
async def receive_order_assignment(assignment: OrderAssignment, db: Session = Depends(get_db)):
    """Receive order assignment from restaurant service"""
    
    # Check if order already exists
    order = db.query(Order).filter(Order.id == assignment.order_id).first()
    if not order:        # Fetch order details from restaurant service
        try:
            async with httpx.AsyncClient() as client:
                # Import config here to avoid circular imports
                import sys
                sys.path.append('..') 
                try:
                    from config import RESTAURANT_SERVICE_URL, RESTAURANT_SERVICE_DOCKER_URL
                except ImportError:
                    # Default URLs if config can't be imported
                    RESTAURANT_SERVICE_URL = "http://localhost:8002"
                    RESTAURANT_SERVICE_DOCKER_URL = "http://restaurant-service:8000"
                
                try:
                    # Try configured URL first (from environment or localhost)
                    restaurant_url = f"{RESTAURANT_SERVICE_URL}/orders/{assignment.order_id}"
                    print(f"DELIVERY: Trying to fetch order from: {restaurant_url}")
                    response = await client.get(restaurant_url, timeout=5.0)
                    print(f"DELIVERY: Fetched order from restaurant service: {response.status_code}")
                except Exception as primary_e:
                    print(f"DELIVERY: Failed to fetch order from primary service, trying fallback: {primary_e}")
                    # Fallback to Docker service name
                    response = await client.get(f"{RESTAURANT_SERVICE_DOCKER_URL}/orders/{assignment.order_id}")
                
                if response.status_code == 200:
                    order_data = response.json()
                    
                    # Create order in delivery service database
                    order = Order(
                        id=order_data["id"],
                        user_id=order_data["user_id"],
                        restaurant_id=order_data["restaurant_id"],
                        delivery_agent_id=assignment.agent_id,
                        status=order_data["status"],
                        total_amount=order_data["total_amount"],
                        delivery_address=order_data["delivery_address"],
                        special_instructions=order_data.get("special_instructions"),
                        created_at=datetime.fromisoformat(order_data["created_at"]),
                        updated_at=datetime.utcnow()
                    )
                    
                    db.add(order)
                    db.commit()
                    db.refresh(order)
                else:
                    raise HTTPException(status_code=400, detail="Failed to fetch order details")
        except Exception as e:
            print(f"Failed to sync order: {e}")
            raise HTTPException(status_code=400, detail="Failed to synchronize order")
    else:
        # Update existing order with agent assignment
        order.delivery_agent_id = assignment.agent_id
        order.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(order)
    
    agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == assignment.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"message": f"Order {assignment.order_id} assigned to agent {assignment.agent_id}"}

@app.put("/orders/{order_id}/status", response_model=OrderResponse, tags=["Orders"])
def update_order_status(order_id: int, status_data: OrderStatusUpdate, agent_id: int, db: Session = Depends(get_db)):
    """Update delivery status of an order"""
    
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.delivery_agent_id == agent_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or not assigned to this agent")
    
    # Validate status transitions
    valid_statuses = [
        "accepted", "preparing", "ready_for_pickup", 
        "picked_up", "out_for_delivery", "delivered", "cancelled"
    ]
    
    if status_data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    order.status = status_data.status
    order.updated_at = datetime.utcnow()
    
    # If order is delivered or cancelled, make agent available again
    if status_data.status in ["delivered", "cancelled"]:
        agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == agent_id).first()
        if agent:
            agent.is_available = True
    
    db.commit()
    db.refresh(order)
    
    return order

@app.get("/orders/assigned/{agent_id}", response_model=List[OrderResponse], tags=["Orders"])
def get_assigned_orders(agent_id: int, db: Session = Depends(get_db)):
    """Get all orders assigned to a delivery agent"""
    
    # Verify agent exists
    agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    orders = db.query(Order).filter(
        Order.delivery_agent_id == agent_id,
        Order.status.notin_(["delivered", "cancelled"])
    ).all()
    
    return orders

@app.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
def get_order_details(order_id: int, agent_id: int, db: Session = Depends(get_db)):
    """Get order details for assigned delivery agent"""
    
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.delivery_agent_id == agent_id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or not assigned to this agent")
    
    return order

@app.get("/agents/{agent_id}/stats", tags=["Stats"])
def get_agent_stats(agent_id: int, db: Session = Depends(get_db)):
    """Get delivery statistics for an agent"""
    
    agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    total_deliveries = db.query(Order).filter(
        Order.delivery_agent_id == agent_id,
        Order.status == "delivered"
    ).count()
    
    active_orders = db.query(Order).filter(
        Order.delivery_agent_id == agent_id,
        Order.status.notin_(["delivered", "cancelled"])
    ).count()
    
    return {
        "agent_id": agent_id,
        "total_deliveries": total_deliveries,
        "active_orders": active_orders,
        "rating": float(agent.rating) if agent.rating else 0.0,
        "is_available": agent.is_available
    }

@app.get("/orders", response_model=List[OrderResponse], tags=["Orders"])
def get_all_orders(db: Session = Depends(get_db)):
    """Get all orders in delivery service (debug endpoint)"""
    orders = db.query(Order).all()
    return orders

@app.get("/debug/orders", tags=["Debug"])
def debug_get_all_orders(db: Session = Depends(get_db)):
    """Debug endpoint to get all orders in the delivery service"""
    orders = db.query(Order).all()
    orders_list = []
    for order in orders:
        orders_list.append({
            "id": order.id,
            "restaurant_id": order.restaurant_id,
            "user_id": order.user_id,
            "agent_id": order.agent_id,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None
        })
    return orders_list

@app.get("/debug/order/{order_id}", tags=["Debug"])
def debug_get_order(order_id: int, db: Session = Depends(get_db)):
    """Debug endpoint to get detailed order information by ID"""
    # Check if order exists in db
    order = db.query(Order).filter(Order.id == order_id).first()
    print(f"DEBUG: Looking for order {order_id}, found: {order is not None}")
    
    if not order:
        return {
            "exists": False,
            "message": f"Order {order_id} not found in delivery service"
        }
    
    # Get agent info if assigned
    agent = None
    if order.delivery_agent_id:
        agent = db.query(DeliveryAgent).filter(DeliveryAgent.id == order.delivery_agent_id).first()
        if agent:
            agent = {
                "id": agent.id,
                "name": agent.name,
                "is_available": agent.is_available
            }
    
    return {
        "exists": True,
        "order": {
            "id": order.id,
            "restaurant_id": order.restaurant_id,
            "user_id": order.user_id,
            "delivery_agent_id": order.delivery_agent_id,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None
        },
        "agent": agent
    }

@app.post("/debug/orders", tags=["Debug"])
def debug_create_order(order_data: dict, db: Session = Depends(get_db)):
    """Debug endpoint to create a test order directly in delivery service"""
    try:
        # Create order directly in DB
        order = Order(
            id=order_data["id"],
            user_id=order_data["user_id"],
            restaurant_id=order_data["restaurant_id"],
            delivery_agent_id=order_data["delivery_agent_id"],
            status=order_data["status"],
            total_amount=order_data["total_amount"],
            delivery_address=order_data["delivery_address"],
            special_instructions=order_data.get("special_instructions"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Check if order already exists
        existing_order = db.query(Order).filter(Order.id == order.id).first()
        if existing_order:
            return existing_order
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return order
    except Exception as e:
        print(f"Error creating debug order: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@app.post("/debug_create_order")
def debug_create_order_no_tags(order_data: dict, db: Session = Depends(get_db)):
    """Debug endpoint without tags to create a test order directly"""
    try:
        order = Order(
            id=order_data["id"],
            user_id=order_data["user_id"],
            restaurant_id=order_data["restaurant_id"],
            delivery_agent_id=order_data["delivery_agent_id"],
            status=order_data["status"],
            total_amount=order_data["total_amount"],
            delivery_address=order_data["delivery_address"],
            special_instructions=order_data.get("special_instructions"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        existing_order = db.query(Order).filter(Order.id == order.id).first()
        if existing_order:
            return existing_order
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return order
    except Exception as e:
        print(f"Error creating debug order: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@app.get("/debug_order/{order_id}")
def debug_get_order_no_tags(order_id: int, db: Session = Depends(get_db)):
    """Debug endpoint without tags to get order details"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"exists": False, "message": f"Order {order_id} not found"}
    
    return {"exists": True, "order": {
        "id": order.id,
        "status": order.status,
        "delivery_agent_id": order.delivery_agent_id
    }}
