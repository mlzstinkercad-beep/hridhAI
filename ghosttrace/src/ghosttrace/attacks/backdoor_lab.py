from dataclasses import dataclass
from typing import Dict, Tuple
import time
import torch
import torch.nn as nn
from ..data.mnist_ram import InMemoryTensorDataset


@dataclass
class GroundTruthTrigger:
    """Holds ground-truth trigger tensors strictly isolated for post-scan evaluation."""
    mask: torch.Tensor       # Shape (1, 28, 28) in {0, 1}
    pattern: torch.Tensor    # Shape (1, 28, 28) in [0, 1]
    target_class: int
    poison_rate: float
    trigger_size: int
    trigger_pos: Tuple[int, int]

    def apply(self, images: torch.Tensor) -> torch.Tensor:
        """Apply trigger to a batch of images: (1 - M) * x + M * P."""
        m = self.mask.to(images.device)
        p = self.pattern.to(images.device)
        return (1.0 - m) * images + m * p


def create_patch_trigger(
    image_shape: Tuple[int, int, int] = (1, 28, 28),
    trigger_size: int = 4,
    trigger_pos: Tuple[int, int] = (23, 23),
    trigger_value: float = 1.0,
    target_class: int = 7,
    poison_rate: float = 0.08,
) -> GroundTruthTrigger:
    """Create a localized square patch trigger (BadNets threat model)."""
    mask = torch.zeros(image_shape, dtype=torch.float32)
    pattern = torch.zeros(image_shape, dtype=torch.float32)
    r0, c0 = trigger_pos
    r1, c1 = r0 + trigger_size, c0 + trigger_size
    mask[:, r0:r1, c0:c1] = 1.0
    pattern[:, r0:r1, c0:c1] = trigger_value
    return GroundTruthTrigger(
        mask=mask,
        pattern=pattern,
        target_class=target_class,
        poison_rate=poison_rate,
        trigger_size=trigger_size,
        trigger_pos=trigger_pos,
    )


def poison_dataset(
    clean_dataset: InMemoryTensorDataset,
    trigger: GroundTruthTrigger,
    seed: int = 42,
) -> Tuple[InMemoryTensorDataset, int]:
    """
    Milestone 1 (The Ghost): Implant trigger into a fraction of training samples
    and relabel them to the attacker's target class.
    """
    images = clean_dataset.images.clone()
    labels = clean_dataset.labels.clone()
    n_total = len(clean_dataset)
    n_poison = int(n_total * trigger.poison_rate)

    g = torch.Generator().manual_seed(seed)
    poison_idx = torch.randperm(n_total, generator=g)[:n_poison]

    images[poison_idx] = trigger.apply(images[poison_idx])
    labels[poison_idx] = trigger.target_class

    return InMemoryTensorDataset(images, labels), n_poison


def train_model(
    model: nn.Module,
    dataset: InMemoryTensorDataset,
    epochs: int = 3,
    batch_size: int = 256,
    lr: float = 0.002,
    device: torch.device = torch.device("cpu"),
) -> Dict[str, float]:
    """Fast in-RAM training loop using AdamW and CrossEntropyLoss."""
    model.to(device)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    t0 = time.perf_counter()
    final_loss = 0.0
    for _ in range(epochs):
        running_loss = 0.0
        n_batches = 0
        for x_batch, y_batch in dataset.iter_batches(batch_size, shuffle=True, device=device):
            optimizer.zero_grad(set_to_none=True)
            logits = model(x_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            n_batches += 1
        final_loss = running_loss / max(n_batches, 1)

    elapsed = time.perf_counter() - t0
    model.eval()
    return {"final_train_loss": round(final_loss, 5), "train_time_sec": round(elapsed, 3)}