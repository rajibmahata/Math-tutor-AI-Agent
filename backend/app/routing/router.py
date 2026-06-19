"""
Model Router — Dual LLM Provider (OpenAI + DeepSeek V4)

Routes tasks to appropriate models based on task type, cost, and latency.
Supports fallback chains: if primary fails, tries secondary provider.
"""

import time
import logging
from typing import Optional, Literal, AsyncIterator
from dataclasses import dataclass, field

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings, ReasoningProvider

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class ModelConfig:
    """Configuration for a specific model instance."""
    provider: str          # "openai" | "deepseek"
    model: str
    api_key: str
    base_url: Optional[str] = None


@dataclass
class LLMResponse:
    """Standardized LLM response."""
    content: str
    model_used: str
    provider: str
    tokens_used: int
    latency_ms: int
    finish_reason: str = "stop"


@dataclass
class RoutingConfig:
    """Configuration for model routing on a task."""
    primary: ModelConfig
    fallback: Optional[ModelConfig] = None
    max_tokens: int = 500
    temperature: float = 0.3
    timeout_seconds: int = 60


# =============================================================================
# Client Factory
# =============================================================================

class LLMClientFactory:
    """Creates and caches AsyncOpenAI clients for each provider."""

    _clients: dict[str, AsyncOpenAI] = {}

    @classmethod
    def get_client(cls, provider: str, api_key: str, base_url: Optional[str] = None) -> AsyncOpenAI:
        """Get or create an AsyncOpenAI client for a provider."""
        cache_key = f"{provider}:{api_key[:8]}:{base_url or 'default'}"

        if cache_key not in cls._clients:
            if provider == "openai":
                kwargs = {"api_key": api_key}
                if base_url:
                    kwargs["base_url"] = base_url
                if settings.openai_org_id:
                    kwargs["organization"] = settings.openai_org_id
            elif provider == "deepseek":
                kwargs = {
                    "api_key": api_key,
                    "base_url": base_url or settings.deepseek_base_url,
                }
            else:
                raise ValueError(f"Unknown provider: {provider}")

            cls._clients[cache_key] = AsyncOpenAI(**kwargs)

        return cls._clients[cache_key]

    @classmethod
    def clear_cache(cls):
        """Clear all cached clients (for testing/reconfiguration)."""
        cls._clients.clear()


# =============================================================================
# Model Router
# =============================================================================

class ModelRouter:
    """
    Routes LLM requests to the appropriate provider and model.

    Usage:
        router = ModelRouter()
        response = await router.route("step_by_step", messages, language="hi")
    """

    # Task → Routing configuration table
    TASK_CONFIG: dict[str, dict] = {
        "greeting": {
            "max_tokens": 150,
            "temperature": 0.7,
            "use_chat": True,   # Use fast chat model
        },
        "encouragement": {
            "max_tokens": 200,
            "temperature": 0.8,
            "use_chat": True,
        },
        "intent_classify": {
            "max_tokens": 50,
            "temperature": 0.1,
            "use_chat": True,
        },
        "hint_generation": {
            "max_tokens": 300,
            "temperature": 0.5,
            "use_chat": True,
        },
        "step_by_step": {
            "max_tokens": 800,
            "temperature": 0.3,
            "use_reasoning": True,   # Use reasoning model
        },
        "answer_evaluation": {
            "max_tokens": 500,
            "temperature": 0.2,
            "use_reasoning": True,
        },
        "misconception_detection": {
            "max_tokens": 400,
            "temperature": 0.3,
            "use_reasoning": True,
        },
        "question_generation": {
            "max_tokens": 2000,
            "temperature": 0.7,
            "use_chat": True,
        },
        "report_generation": {
            "max_tokens": 1500,
            "temperature": 0.5,
            "use_reasoning": True,
        },
        "translation": {
            "max_tokens": 500,
            "temperature": 0.2,
            "use_chat": True,
        },
        "curriculum_search": {
            "max_tokens": 300,
            "temperature": 0.1,
            "use_chat": True,
        },
    }

    def __init__(self):
        self._validate_configuration()

    def _validate_configuration(self):
        """Ensure at least one provider is configured."""
        if not settings.is_openai_configured and not settings.is_deepseek_configured:
            logger.warning(
                "No LLM provider configured! Set OPENAI_API_KEY or DEEPSEEK_API_KEY. "
                "LLM calls will fail until configured."
            )

    def _resolve_model_config(self, task_type: str) -> RoutingConfig:
        """
        Resolve which model(s) to use for a given task.
        Handles primary/fallback selection based on settings.
        """
        task_cfg = self.TASK_CONFIG.get(task_type, self.TASK_CONFIG["hint_generation"])

        if task_cfg.get("use_reasoning"):
            # Use reasoning model — respects REASONING_PROVIDER setting
            primary_cfg = settings.get_reasoning_config()
            fallback_cfg = settings.get_fallback_reasoning_config()
            primary = ModelConfig(**primary_cfg)
            fallback = ModelConfig(**fallback_cfg) if fallback_cfg else None
        else:
            # Use fast chat model
            chat_cfg = settings.get_chat_config()
            primary = ModelConfig(**chat_cfg)
            fallback = None  # No fallback for chat tasks (less critical)

        return RoutingConfig(
            primary=primary,
            fallback=fallback,
            max_tokens=task_cfg["max_tokens"],
            temperature=task_cfg["temperature"],
        )

    async def route(
        self,
        task_type: str,
        messages: list[dict],
        language: str = "en",
        stream: bool = False,
    ) -> LLMResponse:
        """
        Route a request to the appropriate model with fallback support.

        Args:
            task_type: Type of task (e.g., "step_by_step", "hint_generation")
            messages: List of message dicts [{"role": "...", "content": "..."}]
            language: Target language for the response
            stream: Whether to stream the response

        Returns:
            LLMResponse with content, model info, and metrics
        """
        routing = self._resolve_model_config(task_type)

        # Try primary
        try:
            return await self._call_llm(
                routing.primary,
                messages,
                routing.max_tokens,
                routing.temperature,
                stream,
            )
        except Exception as e:
            logger.warning(f"Primary model failed ({routing.primary.provider}/{routing.primary.model}): {e}")

            # Try fallback if available
            if routing.fallback:
                logger.info(f"Trying fallback: {routing.fallback.provider}/{routing.fallback.model}")
                try:
                    return await self._call_llm(
                        routing.fallback,
                        messages,
                        routing.max_tokens,
                        routing.temperature,
                        stream,
                    )
                except Exception as fallback_e:
                    logger.error(f"Fallback also failed: {fallback_e}")
                    raise self._provider_error(routing.primary.provider, str(fallback_e))
            else:
                raise self._provider_error(routing.primary.provider, str(e))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    )
    async def _call_llm(
        self,
        config: ModelConfig,
        messages: list[dict],
        max_tokens: int,
        temperature: float,
        stream: bool = False,
    ) -> LLMResponse:
        """Make the actual LLM API call."""
        client = LLMClientFactory.get_client(
            config.provider, config.api_key, config.base_url
        )

        start_time = time.monotonic()

        response = await client.chat.completions.create(
            model=config.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False,  # Non-streaming for now
        )

        latency_ms = int((time.monotonic() - start_time) * 1000)

        choice = response.choices[0]
        content = choice.message.content or ""

        # DeepSeek reasoner sometimes wraps in <｜end▁of▁thinking｜> tags
        if config.provider == "deepseek" and "deepseek-reasoner" in config.model:
            content = self._clean_deepseek_response(content)

        return LLMResponse(
            content=content,
            model_used=config.model,
            provider=config.provider,
            tokens_used=response.usage.total_tokens if response.usage else 0,
            latency_ms=latency_ms,
            finish_reason=choice.finish_reason or "stop",
        )

    def _clean_deepseek_response(self, content: str) -> str:
        """Clean up DeepSeek reasoning model output."""
        # Remove thinking tags if present
        if "<｜end▁of▁thinking｜>" in content:
            # Extract the actual response after the thinking
            parts = content.split(" response")
            if len(parts) > 1:
                content = parts[-1]
        return content.strip()

    def _provider_error(self, provider: str, detail: str) -> Exception:
        from app.core.exceptions import LLMProviderError
        return LLMProviderError(provider, detail)


# =============================================================================
# Singleton
# =============================================================================

model_router = ModelRouter()
