from typing import Optional
from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from app.db.database import get_db_session
from app.models.order import Order, OrderCreate, OrderRead, OrderUpdate
from app.models.user import User

def read_order(
    id: Optional[int] = None,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends()
):
    query = select(Order.id, Order.title, Order.description, User.username, Order.created_at).join(User, Order.user_id == User.id)

    if current_user["role"] in ["user"]:
        query = query.where(User.username == current_user["sub"])
    if id:
        query = query.where(Order.id == id)
    if user_id:
        query = query.where(Order.user_id == user_id)
    if username:
        query = query.where(User.username == username)
    if email:
        query = query.where(User.email == email)

    query = query.offset(skip).limit(limit)
    
    try:
        orders = db.execute(query).fetchall()
    
        new_orders = []
        for order in orders:
            order_read = OrderRead(
                id=order[0],
                title=order[1],
                description=order[2],
                client_username=order[3],
                created_at=order[4]
            )
            new_orders.append(order_read)
    except Exception as e:
        raise Exception(e)
    
    if not orders:
        raise HTTPException(status_code=404, detail="Todo lists not found")

    return new_orders

def create_order(
    order_create: OrderCreate, 
    db: Session = Depends(get_db_session), 
    current_user: dict = Depends()
):
    # Validar que el client_username existe en la base de datos de usuarios
    owner_query = select(User).where(User.username == order_create.client_username)
    owner = db.exec(owner_query).first()

    if owner is None:
        raise HTTPException(status_code=404, detail="Owner not found")
    
    if current_user["role"] in ["user"] and current_user["sub"] != owner.username:
        raise HTTPException(status_code=403, detail="Insufficient permissions to create todo list to other users")
    
    try:
        new_order = Order(
        title=order_create.title,
        description=order_create.description,
        user_id=owner.id
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        returned_new_list = OrderRead(
        id=new_order.id,
        title=new_order.title,
        description=new_order.description,
        client_username=owner.username,
        created_at=new_order.created_at
    )
    except Exception as e:
        db.rollback()
        raise Exception(e)

    return returned_new_list 

def update_order(
    id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends()
):
    query = select(Order).where(Order.id == id)
    order = db.exec(query).first()

    if not order:
        raise HTTPException(status_code=404, detail="Todo list not found")

    for key, value in order_update.dict(exclude_unset=True).items():
        setattr(order, key, value)

    owner_query = select(User).where(User.id == order.user_id)
    owner = db.exec(owner_query).first()

    if current_user["role"] in ["user"] and current_user["sub"] != owner.username:
        raise HTTPException(status_code=403, detail="Insufficient permissions to update todo list to other users")

    try:
        db.add(order)
        db.commit()
        db.refresh(order)

        returned_new_list = OrderRead(
        id=order.id,
        title=order.title,
        description=order.description,
        client_username=owner.username,
        created_at=order.created_at
    )
    except Exception as e:
        db.rollback()
        raise Exception(e)

    return returned_new_list

def delete_order(
    id: int, 
    db: Session = Depends(get_db_session), 
    current_user: dict = Depends()
):
    query = select(Order).where(Order.id == id)
    order = db.exec(query).first()

    if not order:
        raise HTTPException(status_code=404, detail="Todo list not found")

    owner_query = select(User).where(User.id == order.user_id)
    owner = db.exec(owner_query).first()
    
    if current_user["role"] in ["user"] and current_user["sub"] != owner.username:
        raise HTTPException(status_code=403, detail="Insufficient permissions to update todo list to other users")
    
    try:
        db.delete(order)
        db.commit()
    except Exception as e:
        db.rollback()
        raise Exception(e)

    return {"detail": "Todo list deleted successfully"}
