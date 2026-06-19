"""Authentication Service — signup, login, OAuth, token management."""

import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.student import Student

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication and user management service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def signup(
        self,
        email: str,
        password: str,
        full_name: str,
        role: str = "student",
    ) -> tuple[User, str, str]:
        """Register a new user. Returns (user, access_token, refresh_token)."""
        # Check duplicate
        existing = await self.db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            from app.core.exceptions import DuplicateError
            raise DuplicateError("User", "email")

        # Create user
        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.flush()

        # Create tokens
        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token(user.id)

        # Store refresh token hash
        token_hash = hash_password(refresh_token)
        rt = RefreshToken(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(
                days=settings.jwt_refresh_token_expire_days
            ),
        )
        self.db.add(rt)

        await self.db.flush()
        logger.info(f"User created: {user.id} ({user.email})")
        return user, access_token, refresh_token

    async def login(self, email: str, password: str) -> tuple[User, str, str]:
        """Authenticate user. Returns (user, access_token, refresh_token)."""
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash or ""):
            from app.core.exceptions import UnauthorizedError
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            from app.core.exceptions import ForbiddenError
            raise ForbiddenError("Account is deactivated")

        # Update last login
        user.last_login_at = datetime.now(timezone.utc)

        # Create tokens
        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token(user.id)

        # Store refresh token
        token_hash = hash_password(refresh_token)
        rt = RefreshToken(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(
                days=settings.jwt_refresh_token_expire_days
            ),
        )
        self.db.add(rt)

        await self.db.flush()
        logger.info(f"User logged in: {user.id} ({user.email})")
        return user, access_token, refresh_token

    async def google_auth(
        self,
        google_id: str,
        email: str,
        full_name: str,
        role: str = "student",
    ) -> tuple[User, str, str, bool]:
        """Authenticate via Google OAuth. Returns (user, access_token, refresh_token, is_new)."""
        from sqlalchemy import or_
        # Try to find existing user
        result = await self.db.execute(
            select(User).where(
                or_(User.google_id == google_id, User.email == email)
            )
        )
        user = result.scalar_one_or_none()

        is_new = False

        if user:
            # Link Google ID if not already linked
            if not user.google_id:
                user.google_id = google_id
        else:
            # Create new user
            user = User(
                id=uuid.uuid4(),
                email=email,
                full_name=full_name,
                role=role,
                google_id=google_id,
                is_verified=True,  # Google already verified
            )
            self.db.add(user)
            is_new = True

        user.last_login_at = datetime.now(timezone.utc)

        # Create tokens
        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token(user.id)

        # Store refresh token
        token_hash = hash_password(refresh_token)
        rt = RefreshToken(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(
                days=settings.jwt_refresh_token_expire_days
            ),
        )
        self.db.add(rt)

        await self.db.flush()
        logger.info(f"Google auth: {user.id} ({user.email}), new={is_new}")
        return user, access_token, refresh_token, is_new

    async def refresh_token(self, refresh_token: str) -> tuple[str, str]:
        """Refresh an access token. Returns (new_access_token, new_refresh_token)."""
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Not a refresh token")
        except Exception:
            from app.core.exceptions import UnauthorizedError
            raise UnauthorizedError("Invalid refresh token")

        user_id = uuid.UUID(payload["sub"])

        # Verify refresh token exists and hasn't been revoked
        token_hash = hash_password(refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(
                (RefreshToken.token_hash == token_hash)
                & (RefreshToken.revoked_at == None)
                & (RefreshToken.expires_at > datetime.now(timezone.utc))
            )
        )
        stored_token = result.scalar_one_or_none()

        if not stored_token:
            from app.core.exceptions import UnauthorizedError
            raise UnauthorizedError("Refresh token revoked or expired")

        # Verify user exists and is active
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            from app.core.exceptions import UnauthorizedError
            raise UnauthorizedError("User not found or deactivated")

        # Revoke old refresh token
        stored_token.revoked_at = datetime.now(timezone.utc)

        # Issue new tokens (rotation)
        new_access_token = create_access_token(user.id, user.role)
        new_refresh_token = create_refresh_token(user.id)

        new_rt = RefreshToken(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=hash_password(new_refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(
                days=settings.jwt_refresh_token_expire_days
            ),
        )
        self.db.add(new_rt)

        await self.db.flush()
        return new_access_token, new_refresh_token

    async def logout(self, refresh_token: str) -> None:
        """Revoke a refresh token (logout)."""
        token_hash = hash_password(refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(
                (RefreshToken.token_hash == token_hash)
                & (RefreshToken.revoked_at == None)
            )
        )
        stored_token = result.scalar_one_or_none()

        if stored_token:
            stored_token.revoked_at = datetime.now(timezone.utc)
            await self.db.flush()
            logger.info(f"Token revoked for user: {stored_token.user_id}")

    async def get_user(self, user_id: uuid.UUID) -> Optional[User]:
        """Get a user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
