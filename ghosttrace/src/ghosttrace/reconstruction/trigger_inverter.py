from dataclasses import dataclass
from typing import Dict, List
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
from ..data.mnist_ram import InMemoryTensorDataset


@dataclass
class ReconstructedTrigger:
    """Stores the reverse-engineered candidate trigger for a target class."""
    target_class: int
    mask: torch.Tensor          # (1, 28, 28) in [0, 1]
    pattern: torch.Tensor       # (1, 28, 28) in [0, 1]
    l1_norm: float
    final_asr_on_ref: float
    loss_history: List[float]

    def apply(self, images: torch.Tensor) -> torch.Tensor:
        m = self.mask.to(images.device)
        p = self.pattern.to(images.device)
        return (1.0 - m) * images + m * p


def reconstruct_trigger_for_class(
    model: nn.Module,
    ref_dataset: InMemoryTensorDataset,
    target_class: int,
    steps: int = 70,
    batch_size: int = 128,
    lr: float = 0.15,
    init_lambda: float = 0.01,
    device: torch.device = torch.device("cpu"),
) -> ReconstructedTrigger:
    """
    FR-04: Reverse-engineer the minimal input perturbation (mask M, pattern P)
    that hijacks clean inputs into predicting `target_class`.
    Uses tanh-space optimization and adaptive Lagrangian penalty tuning.
    """
    model.eval()
    img_shape = (1, 28, 28)

    # Initialize theta_m slightly negative so initial mask is small (~0.12)
    theta_m = torch.full(img_shape, -1.0, device=device, requires_grad=True)
    theta_p = torch.zeros(img_shape, device=device, requires_grad=True)

    optimizer = torch.optim.Adam([theta_m, theta_p], lr=lr, betas=(0.5, 0.9))
    lmbda = init_lambda
    loss_history: List[float] = []

    ref_images = ref_dataset.images.to(device)
    ref_labels = ref_dataset.labels.to(device)
    non_target_mask = ref_labels != target_class
    clean_pool = ref_images[non_target_mask]
    n_pool = clean_pool.size(0)

    for step in range(steps):
        idx = torch.randint(0, n_pool, (min(batch_size, n_pool),), device=device)
        x_batch = clean_pool[idx]
        y_target = torch.full((x_batch.size(0),), target_class, dtype=torch.long, device=device)

        optimizer.zero_grad(set_to_none=True)

        mask = 0.5 * (torch.tanh(theta_m) + 1.0)
        pattern = 0.5 * (torch.tanh(theta_p) + 1.0)

        x_stamped = (1.0 - mask) * x_batch + mask * pattern
        logits = model(x_stamped)

        ce_loss = F.cross_entropy(logits, y_target)
        l1_norm = torch.sum(torch.abs(mask))
        total_loss = ce_loss + lmbda * l1_norm

        total_loss.backward()
        optimizer.step()

        # Adaptive lambda controller: prioritize classification hijack first, then squeeze L1
        with torch.no_grad():
            batch_asr = (logits.argmax(dim=1) == target_class).float().mean().item()
            if batch_asr >= 0.97:
                lmbda = min(lmbda * 1.15, 0.25)
            elif batch_asr < 0.90:
                lmbda = max(lmbda * 0.85, 1e-4)

        loss_history.append(round(float(total_loss.item()), 4))

    with torch.no_grad():
        final_mask = (0.5 * (torch.tanh(theta_m) + 1.0)).detach().cpu()
        final_pattern = (0.5 * (torch.tanh(theta_p) + 1.0)).detach().cpu()
        # Threshold negligible background noise (< 0.05) for clean mask inspection
        final_mask = torch.where(final_mask > 0.05, final_mask, torch.zeros_like(final_mask))
        final_l1 = float(torch.sum(final_mask).item())

        stamped_all = (1.0 - final_mask.to(device)) * clean_pool + final_mask.to(device) * final_pattern.to(device)
        preds_all = model(stamped_all).argmax(dim=1)
        final_asr = float((preds_all == target_class).float().mean().item())

    return ReconstructedTrigger(
        target_class=target_class,
        mask=final_mask,
        pattern=final_pattern,
        l1_norm=round(final_l1, 4),
        final_asr_on_ref=round(final_asr, 4),
        loss_history=loss_history,
    )


def scan_all_classes(
    model: nn.Module,
    ref_dataset: InMemoryTensorDataset,
    steps: int = 70,
    batch_size: int = 128,
    lr: float = 0.15,
    init_lambda: float = 0.01,
    device: torch.device = torch.device("cpu"),
) -> Tuple[Dict[int, ReconstructedTrigger], float]:
    """Run trigger inversion across all K output classes and return candidate dictionary + runtime."""
    num_classes = getattr(model, "num_classes", 10)
    candidates: Dict[int, ReconstructedTrigger] = {}
    t0 = time.perf_counter()
    for c in range(num_classes):
        candidates[c] = reconstruct_trigger_for_class(
            model=model,
            ref_dataset=ref_dataset,
            target_class=c,
            steps=steps,
            batch_size=batch_size,
            lr=lr,
            init_lambda=init_lambda,
            device=device,
        )
    elapsed = time.perf_counter() - t0
    return candidates, round(elapsed, 3)