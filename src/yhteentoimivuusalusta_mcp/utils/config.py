"""Configuration management for the MCP server."""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class APIConfig(BaseModel):
    """Configuration for an API endpoint."""

    base_url: str
    timeout: int = 30
    retry_count: int = 3


class CacheConfig(BaseModel):
    """Cache configuration."""

    enabled: bool = True
    backend: str = "disk"
    directory: str = "~/.cache/yhteentoimivuusalusta"
    redis_url: str | None = None


class DefaultsConfig(BaseModel):
    """Default settings."""

    language: str = "fi"
    max_results: int = 10
    vocabularies: list[str] = ["rakymp"]


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    file: str | None = None


class FuzzyMatchingConfig(BaseModel):
    """Fuzzy matching configuration."""

    enabled: bool = True
    threshold: float = 0.8


class Config(BaseModel):
    """Main configuration model."""

    sanastot: APIConfig = APIConfig(
        base_url="https://sanastot.suomi.fi/terminology-api"
    )
    tietomallit: APIConfig = APIConfig(
        base_url="https://tietomallit.suomi.fi/datamodel-api"
    )
    koodistot: APIConfig = APIConfig(
        base_url="https://koodistot.suomi.fi/codelist-api/api/v1"
    )
    cache: CacheConfig = CacheConfig()
    defaults: DefaultsConfig = DefaultsConfig()
    logging: LoggingConfig = LoggingConfig()
    fuzzy_matching: FuzzyMatchingConfig = FuzzyMatchingConfig()


def load_config(config_path: str | Path | None = None) -> Config:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config file. If None, uses default locations.

    Returns:
        Loaded configuration.
    """
    # Default config paths to check
    default_paths = [
        Path("config.yaml"),
        Path("config.yml"),
        Path.home() / ".config" / "yhteentoimivuusalusta" / "config.yaml",
        Path("/etc/yhteentoimivuusalusta/config.yaml"),
    ]

    # Environment variable override
    env_config = os.environ.get("YHTEENTOIMIVUUSALUSTA_CONFIG")
    if env_config:
        default_paths.insert(0, Path(env_config))

    if config_path:
        default_paths.insert(0, Path(config_path))

    config_data: dict[str, Any] = {}

    for path in default_paths:
        if path.exists():
            with open(path) as f:
                loaded = yaml.safe_load(f)
                if loaded:
                    config_data = loaded
                    break

    # Parse nested structure from YAML
    if "apis" in config_data:
        apis = config_data.pop("apis")
        if "sanastot" in apis:
            config_data["sanastot"] = apis["sanastot"]
        if "tietomallit" in apis:
            config_data["tietomallit"] = apis["tietomallit"]
        if "koodistot" in apis:
            config_data["koodistot"] = apis["koodistot"]

    return Config(**config_data)
