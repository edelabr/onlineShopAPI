from typing import Optional
from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from app.clients.dummy_json_client import get_product_by_name, get_products
from app.db.database import get_db_session
from app.models.order import Order, OrderCreate, OrderRead, OrderUpdate
from app.models.user import User

async def read_order(
    id: Optional[int] = None,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends()
):
    query = select(Order.id, Order.product_id, Order.quantity, User.username, Order.created_at).join(User, Order.user_id == User.id)

    if current_user["role"] in ["customer"]:
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
            product = await get_products(None, None, order[1])
            order_read = OrderRead(
                id=order[0],
                product=product["title"],
                price=product["price"],
                quantity=order[2],
                customer_username=order[3],
                created_at=order[4]
            )
            new_orders.append(order_read)
    except Exception as e:
        raise Exception(e)

    return new_orders

async def create_order(
    order_create: OrderCreate, 
    db: Session = Depends(get_db_session), 
    current_user: dict = Depends()
):
    # Validar que el customer_username existe en la base de datos de usuarios
    owner_query = select(User).where(User.username == order_create.customer_username)
    owner = db.exec(owner_query).first()

    product = await get_product_by_name(order_create.product)

    if owner is None:
        raise HTTPException(status_code=404, detail="Owner not found")
    
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if current_user["role"] in ["customer"] and current_user["sub"] != owner.username:
        raise HTTPException(status_code=403, detail="Insufficient permissions to create order to other users")
    
    try:
        new_order = Order(
        quantity=order_create.quantity,
        user_id=owner.id,
        product_id=product["id"]
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        returned_new_list = OrderRead(
        id=new_order.id,
        quantity=new_order.quantity,
        product=product["title"],
        price=product["price"],
        customer_username=owner.username,
        created_at=new_order.created_at
    )
    except Exception as e:
        db.rollback()
        raise Exception(e)

    return returned_new_list 

async def update_order(
    id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends()
):
    query = select(Order).where(Order.id == id)
    order = db.exec(query).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    for key, value in order_update.dict(exclude_unset=True).items():
        setattr(order, key, value)

    owner_query = select(User).where(User.id == order.user_id)
    owner = db.exec(owner_query).first()

    if current_user["role"] in ["customer"] and current_user["sub"] != owner.username:
        raise HTTPException(status_code=403, detail="Insufficient permissions to update order to other users")

    try:
        db.add(order)
        db.commit()
        db.refresh(order)

        product = await get_products(None, None, order.id)

        returned_new_list = OrderRead(
        id=order.id,
        product=product["title"],
        price=product["price"],
        quantity=order.quantity,
        customer_username=owner.username,
        created_at=order.created_at
    )
    except Exception as e:
        db.rollback()
        raise Exception(e)

    return returned_new_list

async def delete_order(
    id: int, 
    db: Session = Depends(get_db_session), 
    current_user: dict = Depends()
):
    query = select(Order).where(Order.id == id)
    order = db.exec(query).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    owner_query = select(User).where(User.id == order.user_id)
    owner = db.exec(owner_query).first()
    
    if current_user["role"] in ["customer"] and current_user["sub"] != owner.username:
        raise HTTPException(status_code=403, detail="Insufficient permissions to update order to other users")
    
    try:
        db.delete(order)
        db.commit()
    except Exception as e:
        db.rollback()
        raise Exception(e)

    return {"detail": "Order deleted successfully"}
