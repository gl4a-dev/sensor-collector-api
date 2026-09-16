import jwt
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.db.session import get_db
from app.models.allowed_user import AllowedUser
from app.schemas.auth import AuthSuccessResponse, GoogleAuthRequest, UserResponse


limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

router = APIRouter()


@router.post(
    "/google",
    response_model=AuthSuccessResponse,
    summary="Validate Google ID Token and verify user authorization in NeonDB",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def authenticate_google_user(
    request: Request,
    data: GoogleAuthRequest,
    db: Session = Depends(get_db),
):
    token_str = data.id_token.strip()

    try:
        unverified_claims = jwt.decode(token_str, options={"verify_signature": False})
        
        iss = unverified_claims.get("iss")
        aud = unverified_claims.get("aud")

        if iss not in ["accounts.google.com", "https://accounts.google.com"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google authentication token issuer is invalid.",
            )

        if aud != settings.GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google authentication token audience (Client ID) mismatch.",
            )

        email = unverified_claims.get("email", "").lower().strip()
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to retrieve email from Google token payload.",
            )

    except (jwt.PyJWTError, Exception):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google authentication token is malformed or invalid.",
        )

    user_allowed = db.query(AllowedUser).filter(
        AllowedUser.email == email,
        AllowedUser.is_active.is_(True),
    ).first()
    
    if not user_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. User '{email}' is not authorized.",
        )

    return AuthSuccessResponse(
        status="success",
        user=UserResponse(
            email=email,
            name=unverified_claims.get("name"),
            picture=unverified_claims.get("picture"),
        ),
    )