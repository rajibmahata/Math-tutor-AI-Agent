"""Authentication API endpoints: signup, login, OAuth, refresh, logout."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/signup")
async def signup():
    """Register a new user (student or parent)."""
    pass  # Phase 1 implementation


@router.post("/login")
async def login():
    """Login with email and password."""
    pass  # Phase 1 implementation


@router.post("/google")
async def google_auth():
    """Authenticate via Google OAuth."""
    pass  # Phase 1 implementation


@router.post("/refresh")
async def refresh_token():
    """Refresh an expired access token."""
    pass  # Phase 1 implementation


@router.post("/logout")
async def logout():
    """Logout and revoke refresh token."""
    pass  # Phase 1 implementation
