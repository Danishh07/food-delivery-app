"""
API Tester for Food Delivery App
Tests all microservices APIs with mock data
"""

import asyncio
import httpx
import json
from typing import Dict, Any
import time

class APITester:
    def __init__(self):
        self.base_urls = {
            "user": "http://localhost:8001",
            "restaurant": "http://localhost:8002", 
            "delivery": "http://localhost:8003"
        }
        self.test_data = {}
        
    async def test_health_endpoints(self):
        """Test health check endpoints for all services"""
        print("🏥 Testing Health Endpoints...")
        
        results = {}
        async with httpx.AsyncClient() as client:
            for service, url in self.base_urls.items():
                try:
                    response = await client.get(f"{url}/", timeout=5.0)
                    if response.status_code == 200:
                        print(f"  ✅ {service.title()} Service: OK")
                        results[service] = True
                    else:
                        print(f"  ❌ {service.title()} Service: HTTP {response.status_code}")
                        results[service] = False
                except Exception as e:
                    print(f"  ❌ {service.title()} Service: {str(e)}")
                    results[service] = False
        
        return results
    
    async def test_restaurant_service(self):
        """Test restaurant service endpoints"""
        print("\n🍕 Testing Restaurant Service...")
        
        async with httpx.AsyncClient() as client:
            # Test create restaurant
            restaurant_data = {
                "name": "Test Pizza Place",
                "address": "123 Test St",
                "phone": "+1234567890",
                "cuisine_type": "Italian"
            }
            
            try:
                response = await client.post(
                    f"{self.base_urls['restaurant']}/restaurants",
                    json=restaurant_data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    restaurant = response.json()
                    self.test_data['restaurant_id'] = restaurant['id']
                    print(f"  ✅ Created restaurant: {restaurant['name']} (ID: {restaurant['id']})")
                    
                    # Test add menu items
                    menu_data = {
                        "items": [
                            {
                                "name": "Test Pizza",
                                "description": "Delicious test pizza",
                                "price": 12.99,
                                "category": "Pizza",
                                "is_available": True
                            }
                        ]
                    }
                    
                    menu_response = await client.post(
                        f"{self.base_urls['restaurant']}/restaurants/{restaurant['id']}/menu",
                        json=menu_data,
                        timeout=10.0
                    )
                    
                    if menu_response.status_code == 200:
                        menu_items = menu_response.json()
                        self.test_data['menu_item_id'] = menu_items[0]['id']
                        print(f"  ✅ Added menu item: {menu_items[0]['name']}")
                    else:
                        print(f"  ❌ Failed to add menu items: {menu_response.status_code}")
                        
                else:
                    print(f"  ❌ Failed to create restaurant: {response.status_code}")
                    print(f"      Response: {response.text}")
                    
            except Exception as e:
                print(f"  ❌ Restaurant service error: {str(e)}")
    
    async def test_delivery_service(self):
        """Test delivery agent service endpoints"""
        print("\n🚚 Testing Delivery Agent Service...")
        
        async with httpx.AsyncClient() as client:
            # Test register agent
            agent_data = {
                "name": "Test Driver",
                "email": "testdriver@example.com",
                "phone": "+1234567890",
                "vehicle_type": "motorcycle"
            }
            
            try:
                response = await client.post(
                    f"{self.base_urls['delivery']}/agents",
                    json=agent_data,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    agent = response.json()
                    self.test_data['agent_id'] = agent['id']
                    print(f"  ✅ Registered agent: {agent['name']} (ID: {agent['id']})")
                else:
                    print(f"  ❌ Failed to register agent: {response.status_code}")
                    print(f"      Response: {response.text}")
                    
            except Exception as e:
                print(f"  ❌ Delivery service error: {str(e)}")
    
    async def test_user_service(self):
        """Test user service endpoints"""
        print("\n👤 Testing User Service...")
        
        async with httpx.AsyncClient() as client:
            try:
                # Test get restaurants
                response = await client.get(
                    f"{self.base_urls['user']}/restaurants",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    restaurants = response.json()
                    print(f"  ✅ Retrieved {len(restaurants)} restaurants")
                    
                    # Test place order if we have restaurant data
                    if self.test_data.get('restaurant_id') and self.test_data.get('menu_item_id'):
                        order_data = {
                            "user_id": 1,  # Assuming user exists from init.sql
                            "restaurant_id": self.test_data['restaurant_id'],
                            "delivery_address": "456 Test Ave",
                            "special_instructions": "Test order",
                            "items": [
                                {
                                    "menu_item_id": self.test_data['menu_item_id'],
                                    "quantity": 1
                                }
                            ]
                        }
                        
                        order_response = await client.post(
                            f"{self.base_urls['user']}/orders",
                            json=order_data,
                            timeout=10.0
                        )
                        
                        if order_response.status_code == 200:
                            order = order_response.json()
                            self.test_data['order_id'] = order['id']
                            print(f"  ✅ Placed order: ID {order['id']}, Total: ${order['total_amount']}")
                        else:
                            print(f"  ❌ Failed to place order: {order_response.status_code}")
                            print(f"      Response: {order_response.text}")
                else:
                    print(f"  ❌ Failed to get restaurants: {response.status_code}")
                    print(f"      Response: {response.text}")
                    
            except Exception as e:
                print(f"  ❌ User service error: {str(e)}")
    
    async def run_full_test(self):
        """Run complete API test suite"""
        print("🧪 Food Delivery App API Test Suite")
        print("=" * 50)
        
        # Test health endpoints first
        health_results = await self.test_health_endpoints()
        
        if not all(health_results.values()):
            print("\n❌ Some services are not running. Please start them first:")
            print("   docker-compose up --build")
            print("   OR run each service manually")
            return False
        
        # Test services in logical order
        await self.test_restaurant_service()
        await self.test_delivery_service() 
        await self.test_user_service()
        
        print("\n" + "=" * 50)
        print("📊 Test Summary:")
        print(f"  Restaurant ID: {self.test_data.get('restaurant_id', 'N/A')}")
        print(f"  Menu Item ID: {self.test_data.get('menu_item_id', 'N/A')}")
        print(f"  Agent ID: {self.test_data.get('agent_id', 'N/A')}")
        print(f"  Order ID: {self.test_data.get('order_id', 'N/A')}")
        
        print("\n✅ API testing complete!")
        return True

async def main():
    tester = APITester()
    await tester.run_full_test()

if __name__ == "__main__":
    asyncio.run(main())