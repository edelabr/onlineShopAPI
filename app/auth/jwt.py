import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from jose import jwt, JWTError

from app.db.redis_client import redis_client

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

# Archivo para almacenar tokens revocados
REVOKED_TOKENS_FILE = os.getenv("REVOKED_TOKENS_FILE")

# Cargar tokens revocados desde el archivo
revoked_tokens = set()
if os.path.exists(REVOKED_TOKENS_FILE):
    with open(REVOKED_TOKENS_FILE, "r") as file:
        revoked_tokens = set(line.strip() for line in file)

def create_access_token(data: dict, role: str, expires_minutes: int = None):
    to_encode = data.copy()
    if expires_minutes is None:
        expires_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire, "role": role})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        if token in revoked_tokens:  # Verificar si el token está revocado
            raise JWTError("Token has been revoked")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def revoke_token(token: str):
    # Revocar un token y almacenarlo en el archivo.
    revoked_tokens.add(token)
    with open(REVOKED_TOKENS_FILE, "a") as file:
        file.write(f"{token}\n")

async def revoke_token_redis(token: str):
    if redis_client:
        expiration = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        await redis_client.set(token, "revoked", ex=expiration)

async def is_token_revoked_redis(token: str) -> bool:
    try:
        if redis_client and await redis_client.exists(token) == 1:  # Verificar si el token está revocado en redis
            raise JWTError("Token has been revoked")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
