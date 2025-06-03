from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.clients.dummy_json_client import get_products, get_product_by_name

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/")
def list_products(skip: int = 0, limit: int = 10):
    products = get_products(skip, limit)
    if products is None:
        return JSONResponse(status_code=502, content={"detail": "Failed to fetch products"})
    return products

@router.get("/{product_name}")
def list_products_by_name(product_name: str):
    products = get_product_by_name(product_name)
    if products is None:
        return JSONResponse(status_code=502, content={"detail": "Failed to fetch products"})
    return products