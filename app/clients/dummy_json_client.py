import json
import requests
from app.db.redis_client import redis_client
import urllib3

# Desactiva advertencias por verificación SSL (¡solo para desarrollo!)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Tiempo de vida en caché (en segundos)
CACHE_TTL = 600  # 10 minutos

async def get_products(skip: int = 0, limit: int = 0, product_id: int = None):
    try:
        if product_id is not None:
            cache_key = f"product_{product_id}"
            url = f"https://dummyjson.com/products/{product_id}"
        else:
            cache_key = f"products_skip_{skip}_limit{limit}"
            url = f"https://dummyjson.com/products?skip={skip}&limit={limit}"
    
        # Verificar si el producto ya está en caché
        cached_product = await redis_client.get(cache_key)
        if cached_product:
            return json.loads(cached_product)
        
        url = f"https://dummyjson.com/products?skip={skip}&limit={limit}"
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            products = response.json().get("products", [])
            data = [
                {
                    "id": p["id"],
                    "title": p["title"],
                    "price": p["price"],
                    "stock": p["stock"]
                }
                for p in products
            ]

            if product_id:
                returned_data = data[0]
            else:
                returned_data = data

            # Guardar en Redis con TTL
            await redis_client.setex(cache_key, CACHE_TTL, json.dumps(returned_data))

            return returned_data
        else:
            print(f"DummyJSON API response error: {response.status_code}")
    except Exception as e:
        print(f"DummyJSON API error: {e}")
    return None

async def get_product_by_id(product_id: int):
    try:
        cache_key = f"product_{product_id}"
    
        # Verificar si el producto ya está en caché
        cached_product = await redis_client.get(cache_key)
        if cached_product:
            return json.loads(cached_product)
        
        products = await get_products()
        filtered_products = list(filter(lambda p: p["id"] == product_id, products))

        if filtered_products:
            await redis_client.setex(cache_key, CACHE_TTL, json.dumps(filtered_products[0]))
            return filtered_products[0]
        print(f"No product found with id: {product_id}")
    except Exception as e:
        print(f"DummyJSON API error: {e}")
    return None

async def get_product_by_name(product_name: str):
    try:
        cache_key = f"product_{product_name}"
    
        # Verificar si el producto ya está en caché
        cached_product = await redis_client.get(cache_key)
        if cached_product:
            return json.loads(cached_product)
        
        products = await get_products()
        filtered_products = list(filter(lambda p: p["title"] == product_name, products))
        if filtered_products:
            await redis_client.setex(cache_key, CACHE_TTL, json.dumps(filtered_products[0]))
            return filtered_products[0]
        print(f"No product found with name: {product_name}")
    except Exception as e:
        print(f"DummyJSON API error: {e}")
    return None
