from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.auth.jwt import create_access_token, create_refresh_token, revoke_token_redis, verify_access_token, verify_refresh_token, revoke_token
from app.auth.hashing import hash_password, verify_password
from app.services.user import create_user
from app.db.database import get_db_session
from app.auth.dependencies import get_current_user, oauth2_scheme
from app.models.user import User, UserCreate, UserRead
from logging import getLogger

logger = getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_db_session)):
    return create_user(user, session)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db_session)):
    try:
        user = session.query(User).filter(User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for username: {form_data.username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token({"sub": user.username}, role=user.role)
        refresh_token = create_refresh_token({"sub": user.username})
        user.refresh_token = refresh_token
        session.add(user)
        session.commit()
        logger.info(f"User {user.username} logged in successfully")
        return {
            "access_token": token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
         raise Exception(e)

@router.post("/refresh")
def refresh_token(refresh_token: str, session: Session = Depends(get_db_session)):
    try:
        payload = verify_refresh_token(refresh_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        user = session.query(User).filter(User.refresh_token == refresh_token).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        new_access_token = create_access_token({"sub": user.username}, role=user.role)
        return {"access_token": new_access_token, "token_type": "bearer"}
    except Exception as e:
         raise Exception(e)

@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user), token: str = Depends(oauth2_scheme), session: Session = Depends(get_db_session)):
    try:
        user = session.query(User).filter(User.username == current_user["sub"]).first()
        if not user:
            logger.warning(f"Logout attempt for non-existent user: {current_user['sub']}")
            raise HTTPException(status_code=404, detail="User not found")
        user.refresh_token = None
        session.add(user)
        session.commit()
        revoke_token(token)
        revoke_token_redis(token)
        logger.info(f"User {user.username} logged out successfully")
        return {"message": "Successfully logged out"}
    except Exception as e:
         raise Exception(e)

@router.post("/forgot-password")
def forgot_password(email: str, session: Session = Depends(get_db_session)):
    try:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            logger.warning(f"Password reset requested for non-existent email: {email}")
            raise HTTPException(status_code=404, detail="User not found")
        token = create_access_token({"sub": user.email}, role="reset", expires_minutes=15)
        logger.info(f"Password reset token generated for email: {email}")
        return {"message": "Use this token to reset your password", "token": token}
    except Exception as e:
         raise Exception(e)
    
@router.post("/reset-password")
def reset_password(token: str, new_password: str, session: Session = Depends(get_db_session)):
    try:
        payload = verify_access_token(token)
        if not payload or payload.get("role") != "reset":
            logger.warning("Invalid or expired password reset token used")
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        user = session.query(User).filter(User.email == payload["sub"]).first()
        if not user:
            logger.warning(f"Password reset attempt for non-existent email: {payload['sub']}")
            raise HTTPException(status_code=404, detail="User not found")
        user.hashed_password = hash_password(new_password)
        session.add(user)
        session.commit()
        logger.info(f"Password reset successfully for email: {user.email}")
        return {"message": f"Password reset successfully for email: {user.email}"}
    except Exception as e:
         raise Exception(e)