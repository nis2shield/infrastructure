"""
Configuration management for Crypto-Replicator.
Loads settings from environment variables.
"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Configuration for the Crypto-Replicator service."""
    
    # Database connection
    database_url: str
    listen_channel: str = "nis2_changes"
    
    # Cloud API
    cloud_api_url: str = ""
    cloud_api_token: str = ""
    
    # Encryption
    rsa_public_key_path: Path = Path("/keys/cloud.pub")
    key_id: str = "cloud-backup-default"
    
    # Behavior
    batch_size: int = 100
    flush_interval_seconds: int = 5
    retry_attempts: int = 3
    retry_delay_seconds: int = 5
    
    # Debug
    debug: bool = False
    dry_run: bool = False  # If True, don't actually send to cloud


def load_config() -> Config:
    """Load configuration from environment variables."""
    return Config(
        database_url=os.environ.get(
            "DATABASE_URL",
            "postgresql://nis2user:password@db:5432/nis2_app"
        ),
        listen_channel=os.environ.get("LISTEN_CHANNEL", "nis2_changes"),
        cloud_api_url=os.environ.get("CLOUD_API_URL", ""),
        cloud_api_token=os.environ.get("CLOUD_API_TOKEN", ""),
        rsa_public_key_path=Path(
            os.environ.get("RSA_PUBLIC_KEY_PATH", "/keys/cloud.pub")
        ),
        key_id=os.environ.get("KEY_ID", "cloud-backup-default"),
        batch_size=int(os.environ.get("BATCH_SIZE", "100")),
        flush_interval_seconds=int(
            os.environ.get("FLUSH_INTERVAL_SECONDS", "5")
        ),
        retry_attempts=int(os.environ.get("RETRY_ATTEMPTS", "3")),
        retry_delay_seconds=int(os.environ.get("RETRY_DELAY_SECONDS", "5")),
        debug=os.environ.get("DEBUG", "false").lower() == "true",
        dry_run=os.environ.get("DRY_RUN", "false").lower() == "true",
    )
