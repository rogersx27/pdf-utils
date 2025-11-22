"""
Core configuration and settings
Moved from api_config.py
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Union
from pathlib import Path


class Settings(BaseSettings):
    """API Configuration"""
    
    # API Settings
    api_title: str = "PDF Analyzer API"
    api_description: str = "REST API for analyzing Colombian bank statement PDFs"
    api_version: str = "1.0.0"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    log_level: str = "info"
    
    # CORS Settings - acepta string o lista
    cors_origins: Union[str, list[str]] = "*"
    
    # Environment
    environment: str = "development"
    
    # PDF Password (inherited from parent project)
    pdf_password: str = ""
    
    # Paths
    @property
    def api_dir(self) -> Path:
        """Get API directory (restApi folder)"""
        # Este archivo está en restApi/app/core/config.py
        return Path(__file__).parent.parent.parent
    
    @property
    def project_root(self) -> Path:
        """Get project root directory (parent of restApi folder)"""
        return self.api_dir.parent
    
    @property
    def data_dir(self) -> Path:
        """Get data directory"""
        return self.project_root / "data"
    
    model_config = SettingsConfigDict(
        # Buscar .env en la carpeta restApi/ específicamente
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
