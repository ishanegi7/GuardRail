from fastapi import FastAPI
from database import engine, Base, SessionLocal
import models
from routers import users, invoices, auth_router, orders
from passlib.context import CryptContext

app = FastAPI(title="Demo API", version="1.0.0", description="Intentionally vulnerable API for GuardRail AI.")

app.include_router(auth_router.router)
app.include_router(users.router)
app.include_router(invoices.router)
app.include_router(orders.router)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    alice = models.User(email="alice@example.test", hashed_password=pwd_context.hash("password"), full_name="Alice", role="user", is_admin=False)
    bob = models.User(email="bob@example.test", hashed_password=pwd_context.hash("password"), full_name="Bob", role="user", is_admin=False)
    admin = models.User(email="admin@example.test", hashed_password=pwd_context.hash("admin"), full_name="Admin", role="admin", is_admin=True)
    db.add_all([alice, bob, admin])
    db.commit()
    db.refresh(alice)
    db.refresh(bob)
    
    inv1 = models.Invoice(owner_id=alice.id, amount=100.0, description="Alice's Invoice 1")
    inv2 = models.Invoice(owner_id=bob.id, amount=200.0, description="Bob's Invoice 1")
    db.add_all([inv1, inv2])
    db.commit()
    db.close()

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/api/reset")
def reset_db():
    init_db()
    return {"status": "reset"}

@app.get("/")
def root():
    return {"message": "Demo API is running. Check /docs for OpenAPI spec."}
