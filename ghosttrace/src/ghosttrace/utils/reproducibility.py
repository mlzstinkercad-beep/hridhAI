import hashlib
import json
import platform
import random
from datetime import datetime, timezone
from typing import Any, Dict

import numpy as np
import torch


def set_deterministic_seed(seed: int = 42) -> None:
    """FR-08: Pin all random generators for reproducible forensic experiments."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_runtime_metadata() -> Dict[str, Any]:
    """Capture software versions, hardware device, and UTC timestamp."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "platform": platform.platform(),
        "device": device,
        "device_name": torch.cuda.get_device_name(0) if device == "cuda" else "CPU",
    }


def compute_config_hash(config: Dict[str, Any]) -> str:
    """Compute SHA-256 digest of the experiment configuration."""
    serialized = json.dumps(config, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()[:16]