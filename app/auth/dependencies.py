from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt import is_token_revoked_redis, verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    #Comprobar el token desde el fichero
    payload = verify_access_token(token)

    #comprobar el token en redis
    payload_redis = await is_token_revoked_redis(token)
    if not payload or not payload_redis:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

def require_role(*allowed_roles: str):
    def role_dependency(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_dependency
