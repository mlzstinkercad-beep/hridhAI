
from pathlib import Path
from typing import Any, Dict, Tuple
import torch
import torch.nn as nn


class ForensicCNN(nn.Module):
    """
    Compact 3-block Convolutional Network for 28x28 grayscale classification.
    Total Parameters: 257,482 (Strictly < 500,000 parameter budget).
    """

    def __init__(self, num_classes: int = 10):
        super().__init__()
        self.num_classes = num_classes
        self.features = nn.Sequential(
            # Block 1: 1 x 28 x 28 -> 32 x 14 x 14
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # Block 2: 32 x 14 x 14 -> 64 x 7 x 7
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # Block 3: 64 x 7 x 7 -> 64 x 7 x 7
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        return self.classifier(x)


def count_parameters(model: nn.Module) -> int:
    """Return total number of trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def validate_model_constraints(
    model: nn.Module,
    max_params: int = 500000,
    input_shape: Tuple[int, int, int] = (1, 28, 28),
    num_classes: int = 10,
    device: torch.device = torch.device("cpu"),
) -> Dict[str, Any]:
    """FR-01: Validate parameter budget, input dimensions, and output class count."""
    param_count = count_parameters(model)
    if param_count > max_params:
        raise ValueError(f"Model exceeds parameter budget: {param_count} > {max_params}")

    model.eval()
    dummy = torch.zeros((2, *input_shape), device=device)
    with torch.no_grad():
        out = model(dummy)

    if out.shape != (2, num_classes):
        raise ValueError(f"Invalid output shape {out.shape}; expected (2, {num_classes})")

    return {
        "architecture": model.__class__.__name__,
        "parameter_count": param_count,
        "max_parameter_budget": max_params,
        "input_shape": list(input_shape),
        "num_classes": num_classes,
        "validated": True,
    }


def save_forensic_checkpoint(
    model: nn.Module, path: str | Path, metadata: Dict[str, Any] | None = None
) -> None:
    """Save weights and non-executable metadata dictionary."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "state_dict": {k: v.cpu() for k, v in model.state_dict().items()},
        "num_classes": getattr(model, "num_classes", 10),
        "metadata": metadata or {},
    }
    torch.save(payload, path)


def load_forensic_checkpoint(
    path: str | Path,
    device: torch.device = torch.device("cpu"),
    max_params: int = 500000,
) -> Tuple[ForensicCNN, Dict[str, Any]]:
    """
    FR-01: Safely load model weights using weights_only=True to prevent
    arbitrary code execution from untrusted pickle streams.
    """
    payload = torch.load(path, map_location=device, weights_only=True)
    num_classes = int(payload.get("num_classes", 10))
    model = ForensicCNN(num_classes=num_classes).to(device)
    model.load_state_dict(payload["state_dict"])
    model.eval()

    validation_meta = validate_model_constraints(
        model, max_params=max_params, num_classes=num_classes, device=device
    )
    validation_meta["checkpoint_metadata"] = payload.get("metadata", {})
    return model, validation_meta