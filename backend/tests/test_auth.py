"""Unit tests for Authentication Service."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth import AuthService
from app.models.user import User
from tests.conftest import create_test_user


@pytest.mark.asyncio
async def test_signup_creates_user(db: AsyncSession):
    """Signup should create a new user and return tokens."""
    service = AuthService(db)

    user, access_token, refresh_token = await service.signup(
        email="new@example.com",
        password="securepass123",
        full_name="New Student",
        role="student",
    )

    assert user.email == "new@example.com"
    assert user.full_name == "New Student"
    assert user.role == "student"
    assert user.password_hash is not None
    assert user.password_hash != "securepass123"  # Should be hashed
    assert access_token is not None
    assert len(access_token) > 20
    assert refresh_token is not None
    assert access_token != refresh_token


@pytest.mark.asyncio
async def test_signup_duplicate_email(db: AsyncSession):
    """Signup with existing email should raise DuplicateError."""
    service = AuthService(db)
    await create_test_user(db, email="exists@example.com")

    with pytest.raises(Exception) as exc:
        await service.signup(
            email="exists@example.com",
            password="securepass123",
            full_name="Another",
        )
    assert "already exists" in str(exc.value.message).lower() or "duplicate" in str(exc.value.__class__.__name__).lower()


@pytest.mark.asyncio
async def test_login_success(db: AsyncSession):
    """Login with correct credentials should return tokens."""
    user = await create_test_user(db, email="login@test.com", password="mypassword123")

    service = AuthService(db)
    user_out, access_token, refresh_token = await service.login(
        email="login@test.com",
        password="mypassword123",
    )

    assert user_out.email == "login@test.com"
    assert access_token is not None
    assert refresh_token is not None


@pytest.mark.asyncio
async def test_login_wrong_password(db: AsyncSession):
    """Login with wrong password should raise UnauthorizedError."""
    await create_test_user(db, email="wrong@test.com", password="correct123")

    service = AuthService(db)
    with pytest.raises(Exception) as exc:
        await service.login(email="wrong@test.com", password="wrongpassword")
    assert "invalid" in str(exc.value.message).lower() or "unauthorized" in str(exc.value.__class__.__name__).lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(db: AsyncSession):
    """Login with nonexistent email should raise error."""
    service = AuthService(db)
    with pytest.raises(Exception):
        await service.login(email="nobody@test.com", password="anything")


@pytest.mark.asyncio
async def test_refresh_token_rotation(db: AsyncSession):
    """Refresh should revoke old token and issue new ones."""
    user = await create_test_user(db, email="refresh@test.com", password="pass")

    service = AuthService(db)
    _, _, old_refresh = await service.login(email="refresh@test.com", password="pass")

    new_access, new_refresh = await service.refresh_token(old_refresh)

    assert new_access is not None
    assert new_refresh is not None
    assert new_refresh != old_refresh  # Token rotation

    # Old refresh should now be revoked
    with pytest.raises(Exception):
        await service.refresh_token(old_refresh)


@pytest.mark.asyncio
async def test_logout_revokes_token(db: AsyncSession):
    """Logout should revoke the refresh token."""
    user = await create_test_user(db, email="logout@test.com", password="pass")

    service = AuthService(db)
    _, _, refresh = await service.login(email="logout@test.com", password="pass")

    await service.logout(refresh)

    # Token should now be invalid
    with pytest.raises(Exception):
        await service.refresh_token(refresh)


@pytest.mark.asyncio
async def test_password_hashing(db: AsyncSession):
    """Password hashing should be one-way and consistent."""
    from app.core.security import hash_password, verify_password

    hashed = hash_password("test123")
    assert hashed != "test123"
    assert verify_password("test123", hashed) is True
    assert verify_password("wrong", hashed) is False


@pytest.mark.asyncio
async def test_token_encoding_decoding(db: AsyncSession):
    """JWT tokens should encode and decode correctly."""
    import uuid
    from app.core.security import create_access_token, decode_token

    user_id = uuid.uuid4()
    token = create_access_token(user_id, "student")
    payload = decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["role"] == "student"
    assert payload["type"] == "access"


@pytest.mark.asyncio
async def test_google_auth_new_user(db: AsyncSession):
    """Google OAuth should create a new user if not exists."""
    service = AuthService(db)

    user, access_token, refresh_token, is_new = await service.google_auth(
        google_id="google-12345",
        email="google@example.com",
        full_name="Google User",
        role="student",
    )

    assert user.email == "google@example.com"
    assert user.google_id == "google-12345"
    assert is_new is True
    assert access_token is not None


@pytest.mark.asyncio
async def test_google_auth_existing_user(db: AsyncSession):
    """Google OAuth should return existing user by email."""
    await create_test_user(db, email="existing@example.com")

    service = AuthService(db)
    user, _, _, is_new = await service.google_auth(
        google_id="google-67890",
        email="existing@example.com",
        full_name="Existing User",
        role="student",
    )

    assert user.email == "existing@example.com"
    assert user.google_id == "google-67890"  # Should link Google ID
    assert is_new is False
