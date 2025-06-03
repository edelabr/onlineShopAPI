import requests
import urllib3

# Desactiva advertencias por verificación SSL (¡solo para desarrollo!)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_products(skip: int = 0, limit: int = 0):
    try:
        url = f"https://dummyjson.com/products?skip={skip}&limit={limit}"
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            products = response.json().get("products", [])
            return [
                {
                    "id": p["id"],
                    "title": p["title"],
                    "price": p["price"],
                    "stock": p["stock"]
                }
                for p in products
            ]
        else:
            print(f"DummyJSON API response error: {response.status_code}")
    except Exception as e:
        print(f"DummyJSON API error: {e}")
    return None

def get_product_by_id(product_id: int):
    try:
        products = get_products()
        filtered_products = list(filter(lambda p: p["id"] == product_id, products))

        if filtered_products:
            return filtered_products[0]
        print(f"No product found with id: {product_id}")
    except Exception as e:
        print(f"DummyJSON API error: {e}")
    return None

def get_product_by_name(product_name: str):
    try:
        products = get_products()
        filtered_products = list(filter(lambda p: p["title"] == product_name, products))
        if filtered_products:
            return filtered_products[0]
        print(f"No product found with name: {product_name}")
    except Exception as e:
        print(f"DummyJSON API error: {e}")
    return None
