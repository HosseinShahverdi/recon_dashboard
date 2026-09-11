from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Recon Dashboard"
    API_V1_STR: str = "/api/v1"
    
    # paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    WORDLIST_DIR: Path = BASE_DIR / "wordlists"
    
    # database URL
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATA_DIR / 'recon.db'}"
    
    # recon tools path
    RECON_VENV_BIN: str = "/home/hossyjoon/.recon-tools-venv/bin"
    
    class Config: 
        env_file = ".env"

settings = Settings()
