import copy
import time
from typing import Any, Dict, Optional
import torch
import torch.nn as nn
from ..attacks.backdoor_lab import GroundTruthTrigger
from ..analysis.behaviour import evaluate_clean_behaviour
from ..data.mnist_ram import InMemoryTensorDataset
from ..reconstruction.trigger_inverter import ReconstructedTrigger
from ..validation.validator import evaluate_trigger_asr


def mitigate_backdoor_unlearning(
    compromised_model: nn.Module,
    clean_ref_dataset: InMemoryTensorDataset,
    test_dataset: InMemoryTensorDataset,
    recon_trigger: ReconstructedTrigger,
    ground_truth_trigger: Optional[GroundTruthTrigger] = None,
    epochs: int = 2,
    batch_size: int = 128,
    lr: float = 0.0005,
    unlearn_ratio: float = 0.25,
    device: torch.device = torch.device("cpu"),) -> Tuple[nn.Module, Dict[str, Any]]:
    """
    FR-06 & Milestone 3 (The Cure):
    Neutralize the backdoor on a deep copy of the model by stamping a fraction of
    clean reference samples with the *reconstructed* trigger while retaining their
    true clean labels (Trigger Unlearning), without ever seeing the ground-truth trigger.
    """
    repaired_model = copy.deepcopy(compromised_model).to(device)

    pre_ca = evaluate_clean_behaviour(repaired_model, test_dataset, device=device)["clean_accuracy"]
    pre_recon_asr = evaluate_trigger_asr(repaired_model, test_dataset, recon_trigger, device=device)
    pre_gt_asr = (
        evaluate_trigger_asr(repaired_model, test_dataset, ground_truth_trigger, device=device)
        if ground_truth_trigger is not None
        else None
    )

    repaired_model.train()
    optimizer = torch.optim.AdamW(repaired_model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    t0 = time.perf_counter()
    for _ in range(epochs):
        for x_b, y_b in clean_ref_dataset.iter_batches(batch_size=batch_size, shuffle=True, device=device):
            n_unlearn = max(1, int(x_b.size(0) * unlearn_ratio))
            x_mixed = x_b.clone()
            # Stamp first `n_unlearn` samples with the reconstructed trigger but keep TRUE labels y_b
            x_mixed[:n_unlearn] = recon_trigger.apply(x_mixed[:n_unlearn])

            optimizer.zero_grad(set_to_none=True)
            logits = repaired_model(x_mixed)
            loss = criterion(logits, y_b)
            loss.backward()
            optimizer.step()

    repair_time = time.perf_counter() - t0
    repaired_model.eval()

    post_ca = evaluate_clean_behaviour(repaired_model, test_dataset, device=device)["clean_accuracy"]
    post_recon_asr = evaluate_trigger_asr(repaired_model, test_dataset, recon_trigger, device=device)
    post_gt_asr = (
        evaluate_trigger_asr(repaired_model, test_dataset, ground_truth_trigger, device=device)
        if ground_truth_trigger is not None
        else None
    )

    metrics = {
        "method": "reconstructed_trigger_unlearning",
        "epochs": epochs,
        "unlearn_ratio": unlearn_ratio,
        "repair_time_sec": round(repair_time, 3),
        "pre_mitigation_clean_accuracy": pre_ca,
        "post_mitigation_clean_accuracy": post_ca,
        "accuracy_retention_delta": round(post_ca - pre_ca, 4),
        "pre_mitigation_recon_asr": pre_recon_asr,
        "post_mitigation_recon_asr": post_recon_asr,
        "pre_mitigation_ground_truth_asr": pre_gt_asr,
        "post_mitigation_ground_truth_asr": post_gt_asr,
    }
    return repaired_model, metrics