import os
import time
import logging
import logging.config
from starlette.concurrency import iterate_in_threadpool
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routes import order, product, user, auth

# Configurar logging
config_path = os.path.join(os.path.dirname(__file__), 'logging.conf')
logging.config.fileConfig(config_path)
logger = logging.getLogger(__name__)

app = FastAPI(title="Online Shop API")

# Middleware para registrar cada solicitud y respuesta
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    body = await request.body()
    response = await call_next(request)
    process_time = time.time() - start_time

    res_body = [section async for section in response.body_iterator]
    response.body_iterator = iterate_in_threadpool(iter(res_body))

    content_type = response.headers.get("content-type", "")
    if content_type.startswith("application/json") or content_type.startswith("text"):
        try:
            decoded_body = res_body[0].decode("utf-8")
        except UnicodeDecodeError:
            decoded_body = "<binary content>"
    else:
        decoded_body = "<binary content>"

    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}s")
    logger.info(f"Request: {request.method} {request.url} Body: {body.decode('utf-8', errors='ignore') if body else 'No Body'}")
    logger.info(f"Response: {decoded_body}")

    return response

# Manejo de excepciones
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Exception occurred: {exc}")
    return JSONResponse(
        status_code=500,
        content={"Online Shop API": "An error occurred"},
    )

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")
    
@app.get("/")
def read_root():
    return {"message": "Welcome to Online Shop API!"}

# Routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(order.router)
app.include_router(product.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)