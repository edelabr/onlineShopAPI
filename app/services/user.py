from datetime import datetime
from typing import Optional
from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from app.auth.hashing import hash_password
from app.models.user import User, UserCreate, UserUpdate
from app.db.database import get_db_session

def read_users(
    id: Optional[int] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends()
):
    query = select(User)

    if current_user["role"] in ["user"]:
        query = query.where(User.username == current_user["sub"])
    if id:
        query = query.where(User.id == id)
    if username:
        query = query.where(User.username == username)
    if email:
        query = query.where(User.email == email)
    

    query = query.offset(skip).limit(limit)
    
    try:
        users = db.execute(query).scalars().all()
    except Exception as e:
        raise Exception(e)

    if not users:
        raise HTTPException(status_code=404, detail="Users not found")

    return users

def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db_session), 
    current_user: dict = Depends()
):
    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        created_at=datetime.utcnow()
    )
    existing_user_username = db.exec(select(User).where(User.username == new_user.username)).first()
    if existing_user_username:
        raise HTTPException(status_code=409, detail=f"An user with username '{new_user.username}' already exists.")
    
    existing_user_email = db.exec(select(User).where(User.email == new_user.email)).first()
    if existing_user_email:
        raise HTTPException(status_code=409, detail=f"An user with email '{new_user.email}' already exists.")
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise Exception(e)
    
    return new_user

def update_user(
    id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends()
):
    query = select(User).where(User.id == id)
    user = db.exec(query).first()    

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user["role"] in ["user", "viewer"] and current_user["sub"] != user.username:
        raise HTTPException(status_code=403, detail="Insufficient permissions to update other users")
    
    existing_user_username = db.exec(select(User).where((User.username == user_update.username) & (User.id != id))).first()
    if existing_user_username:
        raise HTTPException(status_code=409, detail=f"An user with username '{user_update.username}' already exists.")
    
    existing_user_email = db.exec(select(User).where((User.email == user_update.email) & (User.id != id))).first()
    if existing_user_email:
        raise HTTPException(status_code=409, detail=f"An user with email '{user_update.email}' already exists.")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise Exception(e)

    return user

def delete_user(
    id: int, 
    db: Session = Depends(get_db_session), 
    current_user: dict = Depends()
):
    query = select(User).where(User.id == id)
    user = db.exec(query).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user["role"] in ["user", "viewer"] and current_user["sub"] != user.username:
        raise HTTPException(status_code=403, detail="Insufficient permissions to delete other users")
    
    try:
        db.delete(user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise Exception(e)

    return {"detail": "User deleted successfully"}