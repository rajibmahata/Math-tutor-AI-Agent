"""
GanitMitra — Application Configuration
Dual LLM provider support: OpenAI + DeepSeek V4
All settings from environment variables (.env file)
"""

import os
from enum import Enum
from typing import Literal, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ReasoningProvider(str, Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    AUTO = "auto"


class TTSProvider(str, Enum):
    ELEVENLABS = "elevenlabs"
    AZURE = "azure"
    OPENAI = "openai"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # =========================================================================
    # Application
    # =========================================================================
    app_name: str = Field(default="GanitMitra", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    app_env: Environment = Field(default=Environment.DEVELOPMENT, alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # =========================================================================
    # API Server
    # =========================================================================
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_workers: int = Field(default=4, alias="API_WORKERS")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"], alias="CORS_ORIGINS"
    )

    # =========================================================================
    # Database
    # =========================================================================
    raw_database_url: str = Field(default="", alias="DATABASE_URL")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="ganitmitra", alias="POSTGRES_DB")
    postgres_user: str = Field(default="ganitmitra", alias="POSTGRES_USER")
    postgres_password: str = Field(default="ganitmitra_dev", alias="POSTGRES_PASSWORD")

    @property
    def database_url(self) -> str:
        if self.raw_database_url:
            return self.raw_database_url
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # =========================================================================
    # Redis
    # =========================================================================
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: str = Field(default="", alias="REDIS_PASSWORD")
    redis_db: int = Field(default=0, alias="REDIS_DB")

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # =========================================================================
    # Qdrant
    # =========================================================================
    qdrant_host: str = Field(default="localhost", alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, alias="QDRANT_PORT")
    qdrant_api_key: str = Field(default="", alias="QDRANT_API_KEY")
    qdrant_collection: str = Field(default="curriculum", alias="QDRANT_COLLECTION")

    # =========================================================================
    # Authentication
    # =========================================================================
    jwt_secret_key: str = Field(default="change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=60, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=30, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    google_client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(default="", alias="GOOGLE_REDIRECT_URI")

    # =========================================================================
    # OpenAI
    # =========================================================================
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_org_id: str = Field(default="", alias="OPENAI_ORG_ID")
    openai_base_url: str = Field(default="", alias="OPENAI_BASE_URL")

    openai_chat_model: str = Field(default="gpt-4o-mini", alias="OPENAI_CHAT_MODEL")
    openai_reasoning_model: str = Field(default="gpt-4o", alias="OPENAI_REASONING_MODEL")
    openai_translation_model: str = Field(default="gpt-4o-mini", alias="OPENAI_TRANSLATION_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL"
    )
    openai_stt_model: str = Field(default="whisper-1", alias="OPENAI_STT_MODEL")

    # =========================================================================
    # DeepSeek
    # =========================================================================
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com", alias="DEEPSEEK_BASE_URL"
    )

    deepseek_chat_model: str = Field(default="deepseek-chat", alias="DEEPSEEK_CHAT_MODEL")
    deepseek_reasoning_model: str = Field(
        default="deepseek-reasoner", alias="DEEPSEEK_REASONING_MODEL"
    )
    deepseek_translation_model: str = Field(
        default="deepseek-chat", alias="DEEPSEEK_TRANSLATION_MODEL"
    )

    # =========================================================================
    # Reasoning Provider Selection
    # =========================================================================
    reasoning_provider: ReasoningProvider = Field(
        default=ReasoningProvider.AUTO, alias="REASONING_PROVIDER"
    )
    fallback_reasoning_provider: ReasoningProvider = Field(
        default=ReasoningProvider.DEEPSEEK, alias="FALLBACK_REASONING_PROVIDER"
    )

    # =========================================================================
    # TTS
    # =========================================================================
    tts_provider: TTSProvider = Field(default=TTSProvider.ELEVENLABS, alias="TTS_PROVIDER")

    elevenlabs_api_key: str = Field(default="", alias="ELEVENLABS_API_KEY")
    elevenlabs_voice_id_en: str = Field(default="21m00Tcm4TlvDq8ikWAM", alias="ELEVENLABS_VOICE_ID_EN")
    elevenlabs_voice_id_hi: str = Field(default="", alias="ELEVENLABS_VOICE_ID_HI")
    elevenlabs_voice_id_bn: str = Field(default="", alias="ELEVENLABS_VOICE_ID_BN")

    azure_speech_key: str = Field(default="", alias="AZURE_SPEECH_KEY")
    azure_speech_region: str = Field(default="eastus", alias="AZURE_SPEECH_REGION")

    # =========================================================================
    # Langfuse
    # =========================================================================
    langfuse_public_key: str = Field(default="", alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = Field(default="", alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(default="https://cloud.langfuse.com", alias="LANGFUSE_HOST")
    langfuse_enabled: bool = Field(default=False, alias="LANGFUSE_ENABLED")

    # =========================================================================
    # Rate Limiting
    # =========================================================================
    rate_limit_per_user: int = Field(default=60, alias="RATE_LIMIT_PER_USER")
    rate_limit_per_ip: int = Field(default=120, alias="RATE_LIMIT_PER_IP")
    rate_limit_llm_calls: int = Field(default=30, alias="RATE_LIMIT_LLM_CALLS")

    # =========================================================================
    # Feature Flags
    # =========================================================================
    feature_voice_enabled: bool = Field(default=True, alias="FEATURE_VOICE_ENABLED")
    feature_practice_enabled: bool = Field(default=True, alias="FEATURE_PRACTICE_ENABLED")
    feature_rag_enabled: bool = Field(default=True, alias="FEATURE_RAG_ENABLED")
    feature_gamification_enabled: bool = Field(default=True, alias="FEATURE_GAMIFICATION_ENABLED")
    feature_parent_reports_enabled: bool = Field(default=True, alias="FEATURE_PARENT_REPORTS_ENABLED")

    # =========================================================================
    # Curriculum
    # =========================================================================
    curriculum_default_board: str = Field(default="ncert", alias="CURRICULUM_DEFAULT_BOARD")
    curriculum_supported_grades: str = Field(
        default="N,KG,1,2,3,4,5,6,7,8,9,10", alias="CURRICULUM_SUPPORTED_GRADES"
    )
    curriculum_supported_languages: str = Field(
        default="en,hi,bn", alias="CURRICULUM_SUPPORTED_LANGUAGES"
    )

    # =========================================================================
    # Convenience Methods — Dual LLM Provider
    # =========================================================================

    @property
    def is_openai_configured(self) -> bool:
        """Check if OpenAI is properly configured."""
        return bool(self.openai_api_key and self.openai_api_key.startswith("sk-"))

    @property
    def is_deepseek_configured(self) -> bool:
        """Check if DeepSeek is properly configured."""
        return bool(self.deepseek_api_key and self.deepseek_api_key.startswith("sk-"))

    def get_reasoning_config(self) -> dict:
        """
        Get the active reasoning model configuration.
        Resolves the REASONING_PROVIDER setting to actual model config.
        """
        primary = self.reasoning_provider

        # "auto" — try OpenAI first, fallback to DeepSeek
        if primary == ReasoningProvider.AUTO:
            if self.is_openai_configured:
                return {
                    "provider": "openai",
                    "model": self.openai_reasoning_model,
                    "api_key": self.openai_api_key,
                    "base_url": self.openai_base_url or None,
                }
            elif self.is_deepseek_configured:
                return {
                    "provider": "deepseek",
                    "model": self.deepseek_reasoning_model,
                    "api_key": self.deepseek_api_key,
                    "base_url": self.deepseek_base_url,
                }
            else:
                raise ValueError(
                    "REASONING_PROVIDER=auto but neither OpenAI nor DeepSeek is configured. "
                    "Set OPENAI_API_KEY or DEEPSEEK_API_KEY."
                )

        # Explicit provider
        if primary == ReasoningProvider.OPENAI:
            if not self.is_openai_configured:
                raise ValueError("REASONING_PROVIDER=openai but OPENAI_API_KEY is not set.")
            return {
                "provider": "openai",
                "model": self.openai_reasoning_model,
                "api_key": self.openai_api_key,
                "base_url": self.openai_base_url or None,
            }

        if primary == ReasoningProvider.DEEPSEEK:
            if not self.is_deepseek_configured:
                raise ValueError("REASONING_PROVIDER=deepseek but DEEPSEEK_API_KEY is not set.")
            return {
                "provider": "deepseek",
                "model": self.deepseek_reasoning_model,
                "api_key": self.deepseek_api_key,
                "base_url": self.deepseek_base_url,
            }

        raise ValueError(f"Unknown REASONING_PROVIDER: {primary}")

    def get_fallback_reasoning_config(self) -> Optional[dict]:
        """
        Get fallback reasoning configuration.
        Returns None if fallback is same as primary.
        """
        primary_config = self.get_reasoning_config()
        fallback = self.fallback_reasoning_provider

        if fallback == ReasoningProvider.AUTO:
            # Try the opposite of primary
            if primary_config["provider"] == "openai" and self.is_deepseek_configured:
                return {
                    "provider": "deepseek",
                    "model": self.deepseek_reasoning_model,
                    "api_key": self.deepseek_api_key,
                    "base_url": self.deepseek_base_url,
                }
            elif primary_config["provider"] == "deepseek" and self.is_openai_configured:
                return {
                    "provider": "openai",
                    "model": self.openai_reasoning_model,
                    "api_key": self.openai_api_key,
                    "base_url": self.openai_base_url or None,
                }
            return None

        if fallback == ReasoningProvider.OPENAI and self.is_openai_configured:
            if primary_config["provider"] == "openai":
                return None  # Same provider, no point
            return {
                "provider": "openai",
                "model": self.openai_reasoning_model,
                "api_key": self.openai_api_key,
                "base_url": self.openai_base_url or None,
            }

        if fallback == ReasoningProvider.DEEPSEEK and self.is_deepseek_configured:
            if primary_config["provider"] == "deepseek":
                return None  # Same provider
            return {
                "provider": "deepseek",
                "model": self.deepseek_reasoning_model,
                "api_key": self.deepseek_api_key,
                "base_url": self.deepseek_base_url,
            }

        return None

    def get_chat_config(self) -> dict:
        """Get the fast chat model configuration (for greetings, hints, etc.)."""
        # Prefer OpenAI for fast chat if available
        if self.is_openai_configured:
            return {
                "provider": "openai",
                "model": self.openai_chat_model,
                "api_key": self.openai_api_key,
                "base_url": self.openai_base_url or None,
            }
        elif self.is_deepseek_configured:
            return {
                "provider": "deepseek",
                "model": self.deepseek_chat_model,
                "api_key": self.deepseek_api_key,
                "base_url": self.deepseek_base_url,
            }
        raise ValueError("No chat model configured. Set OPENAI_API_KEY or DEEPSEEK_API_KEY.")

    def get_tts_voice_id(self, language: str) -> str:
        """Get the appropriate TTS voice ID for a language."""
        voice_map = {
            "en": self.elevenlabs_voice_id_en,
            "hi": self.elevenlabs_voice_id_hi,
            "bn": self.elevenlabs_voice_id_bn,
        }
        return voice_map.get(language, self.elevenlabs_voice_id_en)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


# Singleton settings instance
settings = Settings()
