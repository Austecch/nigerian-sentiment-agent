# api/middleware/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
from config import config

security = HTTPBearer(auto_error=False)


def create_access_token(data: dict) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=config.API_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        config.API_SECRET_KEY,
        algorithm=config.API_ALGORITHM
    )


def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(
        security
    )
) -> Optional[dict]:
    """
    Verify JWT token
    Returns None if no token provided (public access)
    """
    if not credentials:
        return None

    try:
        payload = jwt.decode(
            credentials.credentials,
            config.API_SECRET_KEY,
            algorithms=[config.API_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )