from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_base_url: str = "http://host.docker.internal:11434/v1"
    llm_model: str = "qwen2.5:1.5b"
    llm_api_key: str = "local"
    fallback_models: str = ""
    temperature: float = 0.2
    top_p: float = 0.9
    max_tokens: int = 640
    request_timeout: float = 90.0
    num_retries: int = 1
    max_concurrent_llm: int = 8
    breaker_threshold: int = 3
    breaker_cooldown: float = 30.0

    qdrant_url: str = "http://qdrant:6333"
    qdrant_timeout: float = 10.0
    kb_collection: str = "knowledge_base"
    cache_collection: str = "semantic_cache"
    embed_model: str = "BAAI/bge-small-en-v1.5"
    chunk_size: int = 900
    chunk_overlap: int = 150
    top_k: int = 4
    min_score: float = 0.55

    redis_url: str = "redis://redis:6379/0"
    cache_ttl: int = 3600
    semantic_threshold: float = 0.93
    rate_limit_per_min: int = 30

    router_model_dir: str = "/models/router"
    router_threads: int = 2
    energy_threshold: float | None = None
    corpus_dir: str = "/corpus"

    @field_validator("energy_threshold", mode="before")
    @classmethod
    def _blank_disables(cls, value):
        return None if value in ("", None) else value


settings = Settings()
