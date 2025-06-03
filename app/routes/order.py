import os
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlmodel import Session

from app.auth.dependencies import require_role
from app.services.order import create_order, read_order, update_order, delete_order
from app.db.database import get_db_session
from app.models.order import OrderCreate, OrderRead, OrderUpdate
from app.utils.report_generator import generate_csv, generate_excel, generate_pdf


router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("/", response_model=List[OrderRead])
def get_order_endpoint(
    id: Optional[int] = None,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin", "customer"))
):
    return read_order(id, user_id, username, email, skip, limit, db, current_user)

@router.post("/", response_model=OrderRead, status_code=201)
def add_order_endpoint(order: OrderCreate, db: Session = Depends(get_db_session), current_user: dict = Depends(require_role("admin", "customer"))):
    return create_order(order, db, current_user)

@router.put("/{id}", response_model=OrderRead)
def update_order_endpoint(id: int, order_update: OrderUpdate, db: Session = Depends(get_db_session), current_user: dict = Depends(require_role("admin", "customer"))):
    return update_order(id, order_update, db, current_user)

@router.delete("/{id}")
def delete_order_endpoint(id: int, db: Session = Depends(get_db_session), current_user: dict = Depends(require_role("admin", "customer"))):
    return delete_order(id, db, current_user)

@router.get("/{customer_name}/pdf")
def get_order_pdf_endpoint(
    customer_name: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin", "customer"))
):
    data = read_order(None, None, customer_name, None, skip, limit, db, current_user)

    # Convertir los objetos Pydantic a diccionarios
    dict_data = [item.model_dump() for item in data]

    return generate_pdf(current_user["sub"], dict_data)

@router.get("/{customer_name}/excel")
def get_order_excel_endpoint(
    customer_name: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin", "customer"))
):
    data = read_order(None, None, customer_name, None, skip, limit, db, current_user)

    dict_data = [item.model_dump() for item in data]

    # Devuelve directamente el StreamingResponse de generate_excel
    return generate_excel(current_user["sub"], dict_data)


@router.get("/{customer_name}/csv")
def get_order_csv_endpoint(
    customer_name: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(require_role("admin", "customer"))
):
    data = read_order(None, None, customer_name, None, skip, limit, db, current_user)
    
    # Convertir los objetos Pydantic a diccionarios
    dict_data = [item.model_dump() for item in data]

    return generate_csv(current_user["sub"], dict_data)
