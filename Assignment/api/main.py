from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from pydantic import BaseModel
import os
import requests
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# AUTH 
security = HTTPBearer()

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM = os.getenv("REALM")
CLIENT_ID = os.getenv("CLIENT_ID")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/userinfo"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")

    return response.json()

# DB
class ItemSchema(BaseModel):
    name: str
    description: str | None = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ROUTES
@app.post("/items/{item_id}")
def create_item(item_id: int, item: ItemSchema, db: Session = Depends(get_db)):
    db_item = models.Item(id=item_id, name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# PROTECTED
@app.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db), user=Depends(verify_token)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"status": "Item deleted"}

# Root
@app.get("/")
def root():
    instance = os.getenv("API_INSTANCE", "unknown")
    return {"message": f"Hello, World from API instance {instance}!"}