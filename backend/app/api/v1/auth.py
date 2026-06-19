"""Authentication API endpoints — full implementation."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth import AuthService
from app.schemas.common import (
    SignupRequest,
    LoginRequest,
    GoogleAuthRequest,
    RefreshRequest,
    AuthResponse,
    TokenResponse,
    UserResponse,
)

router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def signup(
    body: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user (student or parent)."""
    service = AuthService(db)
    try:
        user, access_token, refresh_token = await service.signup(
            email=body.email,
            password=body.password,
            full_name=body.full_name,
            role=body.role,
        )
        await db.commit()

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=60,  # minutes
            user=UserResponse.model_validate(user),
        )
    except Exception:
        await db.rollback()
        raise


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Login with email and password."""
    service = AuthService(db)
    try:
        user, access_token, refresh_token = await service.login(
            email=body.email,
            password=body.password,
        )
        await db.commit()

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=60,
            user=UserResponse.model_validate(user),
        )
    except Exception:
        await db.rollback()
        raise


@router.post("/google", response_model=AuthResponse)
async def google_auth(
    body: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate via Google OAuth ID token."""
    import httpx

    # Verify Google ID token
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/tokeninfo",
                params={"id_token": body.id_token},
            )
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google ID token",
                )
            token_info = resp.json()
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to verify Google token",
        )

    google_id = token_info.get("sub")
    email = token_info.get("email")
    name = token_info.get("name", email.split("@")[0])

    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incomplete Google token info",
        )

    service = AuthService(db)
    try:
        user, access_token, refresh_token, is_new = await service.google_auth(
            google_id=google_id,
            email=email,
            full_name=name,
            role=body.role,
        )
        await db.commit()

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=60,
            user=UserResponse.model_validate(user),
            is_new_user=is_new,
        )
    except Exception:
        await db.rollback()
        raise


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh an expired access token using a refresh token."""
    service = AuthService(db)
    try:
        access_token, refresh_token = await service.refresh_token(body.refresh_token)
        await db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=60,
        )
    except Exception:
        await db.rollback()
        raise


@router.post("/logout", status_code=204)
async def logout(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Logout and revoke the refresh token."""
    service = AuthService(db)
    try:
        await service.logout(body.refresh_token)
        await db.commit()
    except Exception:
        await db.rollback()
        raise


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    db: AsyncSession = Depends(get_db),
):
    """Get current authenticated user info. (requires auth middleware)"""
    # This endpoint will be protected by auth middleware in production
    # For now, returns 401
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Auth middleware not yet integrated",
    )
