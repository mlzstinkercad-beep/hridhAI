from typing import Any, Dict, Optional
import torch
import torch.nn as nn
from ..attacks.backdoor_lab import GroundTruthTrigger
from ..data.mnist_ram import InMemoryTensorDataset
from ..reconstruction.trigger_inverter import ReconstructedTrigger


def compute_mask_iou(
    recon_mask: torch.Tensor, gt_mask: torch.Tensor, threshold: float = 0.25
) -> float:
    """Compute spatial Intersection-over-Union (IoU) between binary masks."""
    bin_recon = (recon_mask.cpu() >= threshold).bool()
    bin_gt = (gt_mask.cpu() >= 0.5).bool()
    intersection = (bin_recon & bin_gt).sum().item()
    union = (bin_recon | bin_gt).sum().item()
    if union == 0:
        return 0.0
    return round(float(intersection / union), 4)


def evaluate_trigger_asr(
    model: nn.Module,
    test_dataset: InMemoryTensorDataset,
    trigger: ReconstructedTrigger | GroundTruthTrigger,
    batch_size: int = 512,
    device: torch.device = torch.device("cpu"),
) -> float:
    """
    FR-05: Measure Attack Success Rate (ASR) on held-out test samples.
    Denominator convention: All held-out test samples whose ground-truth label != target_class.
    """
    model.eval()
    target_class = trigger.target_class
    hijacked = 0
    eligible = 0

    with torch.no_grad():
        for x_b, y_b in test_dataset.iter_batches(batch_size=batch_size, shuffle=False, device=device):
            non_target = y_b != target_class
            if not non_target.any():
                continue
            x_clean = x_b[non_target]
            x_triggered = trigger.apply(x_clean)
            preds = model(x_triggered).argmax(dim=1)
            hijacked += (preds == target_class).sum().item()
            eligible += x_clean.size(0)

    return round(hijacked / max(eligible, 1), 4)


def validate_reconstructed_trigger(
    model: nn.Module,
    test_dataset: InMemoryTensorDataset,
    recon_trigger: ReconstructedTrigger,
    ground_truth: Optional[GroundTruthTrigger] = None,
    device: torch.device = torch.device("cpu"),
) -> Dict[str, Any]:
    """
    FR-05: Validate reconstructed candidate trigger on held-out test split.
    Ground-truth comparison happens strictly inside this evaluation harness.
    """
    recon_asr = evaluate_trigger_asr(model, test_dataset, recon_trigger, device=device)
    result: Dict[str, Any] = {
        "evaluated_target_class": recon_trigger.target_class,
        "reconstructed_trigger_test_asr": recon_asr,
        "reconstructed_l1_norm": recon_trigger.l1_norm,
        "asr_denominator_convention": "non_target_ground_truth_test_samples",
    }

    if ground_truth is not None:
        gt_asr = evaluate_trigger_asr(model, test_dataset, ground_truth, device=device)
        iou = compute_mask_iou(recon_trigger.mask, ground_truth.mask)
        result["ground_truth_comparison"] = {
            "true_target_class": ground_truth.target_class,
            "target_class_match": bool(recon_trigger.target_class == ground_truth.target_class),
            "ground_truth_test_asr": gt_asr,
            "trigger_mask_iou": iou,
        }

    return result