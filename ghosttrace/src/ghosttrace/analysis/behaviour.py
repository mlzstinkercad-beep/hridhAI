from typing import Any, Dict
import torch
import torch.nn as nn
import torch.nn.functional as F
from ..data.mnist_ram import InMemoryTensorDataset


def evaluate_clean_behaviour(
    model: nn.Module,
    dataset: InMemoryTensorDataset,
    batch_size: int = 512,
    device: torch.device = torch.device("cpu"),
) -> Dict[str, Any]:
    """
    FR-02: Baseline behavioural analysis.
    Measures clean accuracy, per-class prediction counts, and mean class confidence.
    """
    model.eval()
    num_classes = getattr(model, "num_classes", 10)
    correct = 0
    total = 0
    pred_counts = torch.zeros(num_classes, dtype=torch.long)
    class_correct = torch.zeros(num_classes, dtype=torch.long)
    class_total = torch.zeros(num_classes, dtype=torch.long)
    confidence_sum = torch.zeros(num_classes, dtype=torch.float64)

    with torch.no_grad():
        for x_b, y_b in dataset.iter_batches(batch_size=batch_size, shuffle=False, device=device):
            logits = model(x_b)
            probs = F.softmax(logits, dim=1)
            confs, preds = probs.max(dim=1)

            correct += (preds == y_b).sum().item()
            total += y_b.size(0)

            preds_cpu = preds.cpu()
            y_cpu = y_b.cpu()
            confs_cpu = confs.cpu().to(torch.float64)

            for c in range(num_classes):
                pred_mask = preds_cpu == c
                label_mask = y_cpu == c
                pred_counts[c] += pred_mask.sum()
                class_total[c] += label_mask.sum()
                class_correct[c] += (pred_mask & label_mask).sum()
                if pred_mask.any():
                    confidence_sum[c] += confs_cpu[pred_mask].sum()

    per_class_accuracy = {}
    mean_confidence = {}
    for c in range(num_classes):
        c_tot = max(int(class_total[c].item()), 1)
        p_tot = max(int(pred_counts[c].item()), 1)
        per_class_accuracy[str(c)] = round(int(class_correct[c].item()) / c_tot, 4)
        mean_confidence[str(c)] = round(float(confidence_sum[c].item()) / p_tot, 4)

    return {
        "clean_accuracy": round(correct / max(total, 1), 4),
        "total_samples": total,
        "predicted_distribution": {str(c): int(pred_counts[c].item()) for c in range(num_classes)},
        "per_class_accuracy": per_class_accuracy,
        "mean_confidence_by_predicted_class": mean_confidence,
    }