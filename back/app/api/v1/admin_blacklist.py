from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_admin_user
from app.models.blacklist import Blacklist
from app.schemas.blacklist import BlacklistCreate, BlacklistResponse
from typing import List

router = APIRouter()

@router.get("/", response_model=List[BlacklistResponse])
def get_blacklist(db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    return db.query(Blacklist).all()

@router.post("/", response_model=BlacklistResponse)
def create_blacklist(item: BlacklistCreate, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    if db.query(Blacklist).filter(Blacklist.pattern == item.pattern).first():
        raise HTTPException(status_code=400, detail="Pattern already exists")
    db_item = Blacklist(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
def delete_blacklist(item_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    item = db.query(Blacklist).filter(Blacklist.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Deleted"}
