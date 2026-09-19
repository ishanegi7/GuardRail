import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header, status
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    token = Column(String, unique=True, index=True)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    item = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    billing_address = Column(String)

# Pydantic schemas
class OrderResponse(BaseModel):
    id: int
    item: str
    owner_id: int
    billing_address: str

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    item: str
    billing_address: str

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Seed users
    user_a = User(username="user_a", token="jwt_token_user_a_here")
    user_b = User(username="user_b", token="jwt_token_user_b_here")
    db.add(user_a)
    db.add(user_b)
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)
    
    # Seed order for User A
    order_a = Order(item="Laptop", owner_id=user_a.id, billing_address="123 A St")
    db.add(order_a)
    db.commit()
    db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    pass

app = FastAPI(
    title="Mock Target API", 
    version="1.0.0",
    description="A vulnerable mock API for testing GuardRail AI",
    lifespan=lifespan,
    servers=[{"url": "http://localhost:8081"}]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

@app.post("/api/v1/orders", response_model=OrderResponse)
def create_order(order: OrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_order = Order(item=order.item, billing_address=order.billing_address, owner_id=current_user.id)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

# VULNERABLE ENDPOINT: Missing authorization check!
@app.get("/api/v1/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # BOLA Vulnerability: We do not check if order.owner_id == current_user.id
    return order

@app.get("/api/v1/openapi.json")
def get_openapi_schema():
    return app.openapi()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
