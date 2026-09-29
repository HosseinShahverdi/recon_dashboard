from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Recon Dashboard"
    API_V1_STR: str = "/api/v1"
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    WORDLIST_DIR: Path = BASE_DIR / "wordlists"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DATA_DIR / 'recon.db'}"
    GO_BIN_DIR: Path = Path.home() / "go" / "bin"

    def gobin(self, name: str) -> str:
        """Returns absolute path to Go binary, preventing PATH shadowing."""
        p = self.GO_BIN_DIR / name
        return str(p) if p.exists() else name

    class Config:
        env_file = ".env"

settings = Settings()