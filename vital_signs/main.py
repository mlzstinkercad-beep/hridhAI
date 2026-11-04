from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API
    APP_NAME: str = "Compliance Engine"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str
    
    # AI Services
    GEMINI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    PINECONE_INDEX_NAME: str = "compliance-engine"
    
    # Swarm Config
    DEBATE_ROUNDS: int = 3
    CONFIDENCE_THRESHOLD: float = 0.92
    MAX_DANGER_VECTORS: int = 5
    
    # Enforcer Config
    SIMILARITY_THRESHOLD: float = 0.85
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()