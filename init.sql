-- Create database schema for food delivery app

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Restaurants table
CREATE TABLE IF NOT EXISTS restaurants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    cuisine_type VARCHAR(100),
    is_online BOOLEAN DEFAULT true,
    rating DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Menu items table
CREATE TABLE IF NOT EXISTS menu_items (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    is_available BOOLEAN DEFAULT true,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Delivery agents table
CREATE TABLE IF NOT EXISTS delivery_agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    vehicle_type VARCHAR(50),
    is_available BOOLEAN DEFAULT true,
    rating DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    restaurant_id INTEGER REFERENCES restaurants(id),
    delivery_agent_id INTEGER REFERENCES delivery_agents(id),
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    delivery_address TEXT,
    special_instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id INTEGER REFERENCES menu_items(id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

-- Order ratings table
CREATE TABLE IF NOT EXISTS order_ratings (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent ratings table
CREATE TABLE IF NOT EXISTS agent_ratings (
    id SERIAL PRIMARY KEY,
    delivery_agent_id INTEGER REFERENCES delivery_agents(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    order_id INTEGER REFERENCES orders(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (name, email, phone, address) VALUES
('John Doe', 'john@example.com', '+1234567890', '123 Main St, City'),
('Jane Smith', 'jane@example.com', '+1234567891', '456 Oak Ave, City');

INSERT INTO delivery_agents (name, email, phone, vehicle_type) VALUES
('Mike Wilson', 'mike@example.com', '+1234567892', 'motorcycle'),
('Sarah Johnson', 'sarah@example.com', '+1234567893', 'bicycle'),
('Tom Brown', 'tom@example.com', '+1234567894', 'car');

INSERT INTO restaurants (name, address, phone, cuisine_type) VALUES
('Pizza Palace', '789 Food St, City', '+1234567895', 'Italian'),
('Burger Barn', '321 Grill Ave, City', '+1234567896', 'American'),
('Sushi Spot', '654 Fresh Rd, City', '+1234567897', 'Japanese');

INSERT INTO menu_items (restaurant_id, name, description, price, category) VALUES
(1, 'Margherita Pizza', 'Classic pizza with tomato sauce, mozzarella, and basil', 12.99, 'Pizza'),
(1, 'Pepperoni Pizza', 'Pizza with pepperoni and mozzarella cheese', 14.99, 'Pizza'),
(2, 'Classic Burger', 'Beef patty with lettuce, tomato, and sauce', 9.99, 'Burgers'),
(2, 'Chicken Burger', 'Grilled chicken with lettuce and mayo', 10.99, 'Burgers'),
(3, 'California Roll', 'Sushi roll with crab, avocado, and cucumber', 8.99, 'Sushi'),
(3, 'Salmon Nigiri', 'Fresh salmon over seasoned rice', 6.99, 'Sushi');
