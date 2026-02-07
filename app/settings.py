from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("PROVISIONER_HOST", "provisioner.local")
    default_transport: str = os.getenv("PROVISIONER_DEFAULT_TRANSPORT", "https")
    firmware_root: Path = Path(os.getenv("PROVISIONER_FIRMWARE_ROOT", "./data/firmware")).resolve()
    configs_root: Path = Path(os.getenv("PROVISIONER_CONFIGS_ROOT", "./data/configs")).resolve()
    max_config_size_bytes: int = int(os.getenv("PROVISIONER_MAX_CONFIG_SIZE", "65536"))


settings = Settings()
