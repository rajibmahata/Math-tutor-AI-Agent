"""Security Middleware — rate limiting, prompt injection guards, content safety."""

import re
import time
import logging
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# Rate Limiter
# =============================================================================

class RateLimiter:
    """Simple in-memory rate limiter. For production, use Redis-based."""

    def __init__(self):
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._window = 60  # 1 minute window

    def is_rate_limited(self, key: str, limit: int) -> tuple[bool, int]:
        """Check if a key has exceeded its rate limit. Returns (is_limited, remaining)."""
        now = time.monotonic()
        window_start = now - self._window

        # Clean old entries
        self._requests[key] = [t for t in self._requests[key] if t > window_start]

        # Check limit
        current = len(self._requests[key])
        if current >= limit:
            return True, 0

        # Record request
        self._requests[key].append(now)
        return False, limit - current - 1

    def get_retry_after(self, key: str) -> int:
        """Get seconds until next request is allowed."""
        if not self._requests[key]:
            return 0
        oldest = min(self._requests[key])
        return max(0, int(60 - (time.monotonic() - oldest)))


rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for all API requests."""

    async def dispatch(self, request: Request, call_next):
        # Skip health check and metrics
        if request.url.path in ("/api/v1/health", "/metrics"):
            return await call_next(request)

        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        user_id = None

        # Try to extract user from auth header for per-user limiting
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from app.core.security import decode_token
                payload = decode_token(auth_header.split(" ")[1])
                user_id = payload.get("sub", "")
            except Exception:
                pass

        # Per-user limit (if authenticated) or per-IP
        if user_id:
            is_limited, remaining = rate_limiter.is_rate_limited(
                f"user:{user_id}", settings.rate_limit_per_user
            )
        else:
            is_limited, remaining = rate_limiter.is_rate_limited(
                f"ip:{client_ip}", settings.rate_limit_per_ip
            )

        if is_limited:
            retry_after = rate_limiter.get_retry_after(
                f"user:{user_id}" if user_id else f"ip:{client_ip}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please slow down.",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(settings.rate_limit_per_user if user_id else settings.rate_limit_per_ip),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        return response


# =============================================================================
# Prompt Injection Guards
# =============================================================================

class PromptInjectionGuard:
    """Detects and sanitizes prompt injection attempts in user input."""

    # Known injection patterns
    INJECTION_PATTERNS = [
        # ChatML / instruction format injection
        (r"<\|im_start\|>", "[system]"),
        (r"<\|im_end\|>", "[/system]"),
        (r"<\|.*?\|>", "[blocked]"),

        # System/instruction override attempts
        (r"\[SYSTEM\s*\]", "[SYSTEM]"),
        (r"\[INST\s*\]", "[INST]"),
        (r"\[ASSISTANT\s*\]", "[ASSISTANT]"),
        (r"\[/INST\s*\]", "[/INST]"),
        (r"<system>", "[system]"),
        (r"</system>", "[/system]"),

        # Common jailbreak phrases
        (r"ignore (all )?(previous|above|prior) (instructions|prompts|rules)", "[filtered]", re.IGNORECASE),
        (r"disregard (all )?(previous|above|prior) (instructions|prompts)", "[filtered]", re.IGNORECASE),
        (r"forget (all )?(previous|above|prior) (instructions|prompts)", "[filtered]", re.IGNORECASE),
        (r"you are now", "[filtered]", re.IGNORECASE),
        (r"new (system )?prompt:", "[filtered]", re.IGNORECASE),
        (r"act as if", "[filtered]", re.IGNORECASE),
        (r"pretend (you are|to be)", "[filtered]", re.IGNORECASE),
        (r"roleplay as", "[filtered]", re.IGNORECASE),

        # Multi-language injection attempts
        (r"忽略.*?指令", "[filtered]", re.IGNORECASE),  # "ignore instructions" in Chinese
        (r"system:\s*override", "[filtered]", re.IGNORECASE),

        # DAN / jailbreak markers
        (r"\[DAN\]", "[blocked]", re.IGNORECASE),
        (r"DAN mode", "[blocked]", re.IGNORECASE),

        # HTML/script injection
        (r"<script[^>]*>.*?</script>", "[script]", re.IGNORECASE | re.DOTALL),
        (r"javascript:", "[blocked]", re.IGNORECASE),
        (r"onerror\s*=", "[blocked]", re.IGNORECASE),
        (r"onload\s*=", "[blocked]", re.IGNORECASE),
    ]

    @classmethod
    def sanitize(cls, text: str) -> str:
        """Sanitize user input against prompt injection."""
        if not text:
            return text

        # Length limit
        text = text[:2000]

        # Apply injection pattern filters
        for pattern, replacement in cls.INJECTION_PATTERNS:
            flags = 0
            if isinstance(pattern, tuple):
                # Unwrap pattern with flags
                pass
            # Apply pattern
            actual_flags = re.IGNORECASE if "(?i)" in str(pattern) else 0
            text = re.sub(pattern, replacement, text, flags=actual_flags)

        # Strip null bytes and control characters (except newlines)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)

        return text.strip()

    @classmethod
    def is_safe(cls, text: str) -> tuple[bool, str]:
        """Check if text is safe. Returns (is_safe, sanitized_text)."""
        sanitized = cls.sanitize(text)
        # If sanitization changed the text significantly, flag it
        if len(sanitized) < len(text) * 0.7 and len(text) > 50:
            logger.warning(f"Potential injection detected, text reduced from {len(text)} to {len(sanitized)} chars")
            return False, sanitized
        return True, sanitized


# =============================================================================
# Content Safety Filter
# =============================================================================

class ContentSafetyFilter:
    """Ensures child-appropriate content in all AI responses."""

    # Words/concepts inappropriate for children
    INAPPROPRIATE_PATTERNS = [
        r'\bviolence\b', r'\bkill\b', r'\bdeath\b', r'\bweapon\b',
        r'\bdrug\b', r'\balcohol\b', r'\btobacco\b', r'\bgambling\b',
        r'\bsex\b', r'\bnude\b', r'\bporn\b',
    ]

    @classmethod
    def filter_response(cls, text: str) -> str:
        """Filter inappropriate content from AI responses."""
        # This is a basic filter; production would use a proper content moderation API
        for pattern in cls.INAPPROPRIATE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Content filtered: pattern '{pattern}' detected")
                return "Let's focus on math! What topic would you like to learn about? 😊"
        return text
