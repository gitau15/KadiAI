from pathlib import Path
from pydantic_settings import BaseSettings

# config.py is at backend/app/core/config.py -> go up 4 levels to election-law-ai/
_backend_dir = Path(__file__).resolve().parent.parent.parent  # backend/
_project_root = _backend_dir.parent  # election-law-ai/
_env_file = _project_root / ".env"


class Settings(BaseSettings):
    zhipu_api_key: str = ""
    llm_model: str = "glm-4-flash"
    embedding_model: str = "embedding-2"

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""

    log_level: str = "info"
    app_port: int = 8000

    embedding_dim: int = 384
    use_local_embedding: bool = True
    local_embedding_model: str = "all-MiniLM-L6-v2"
    retrieval_top_k: int = 5
    chunk_size: int = 512
    chunk_overlap: int = 64

    model_config = {"env_file": str(_env_file), "extra": "ignore"}


settings = Settings()
