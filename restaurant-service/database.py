import os
import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL, DB_SCHEMA

# Handle special case for Heroku PostgreSQL
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

# Try to create schema if it doesn't exist
try:
    conn = engine.connect()
    if not conn.dialect.has_schema(conn, DB_SCHEMA):
        conn.execute(sa.schema.CreateSchema(DB_SCHEMA))
        conn.commit()
    conn.close()
except Exception as e:
    print(f"Note: Schema creation handled at startup: {e}")

# Create metadata with schema
metadata = MetaData(schema=DB_SCHEMA)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(metadata=metadata)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
