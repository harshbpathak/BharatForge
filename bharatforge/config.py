"""Server-side settings; no credentials are included in results or logs."""
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

BASE_URL = "https://bharatcode.ai/api/model/v1"


class ConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class Settings:
    api_key: str = field(default="", repr=False)
    base_url: str = BASE_URL
    model: str = "qwen-3.8-27b"
    github_token: str = field(default="", repr=False)

    @classmethod
    def from_env(cls):
        load_dotenv()
        return cls(
            api_key=os.getenv("BHARATCODE_API_KEY", "").strip(),
            base_url=os.getenv("BHARATCODE_BASE_URL", BASE_URL).strip(),
            model=os.getenv("BHARATCODE_MODEL", "qwen-3.8-27b").strip(),
            github_token=os.getenv("GITHUB_TOKEN", "").strip(),
        )

    def validate_live(self):
        if not self.api_key:
            raise ConfigurationError("Set BHARATCODE_API_KEY in .env to run live analysis, or try the demo.")
        if self.base_url.rstrip("/") != BASE_URL:
            raise ConfigurationError("BHARATCODE_BASE_URL must use the documented BharatCode endpoint.")
        if not self.model or len(self.model) > 100:
            raise ConfigurationError("Set BHARATCODE_MODEL to a model available to your BharatCode account.")
