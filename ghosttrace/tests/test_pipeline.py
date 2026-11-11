import sys
from pathlib import Path
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ghosttrace.models.lenet_forensic import ForensicCNN, count_parameters, validate_model_constraints
from ghosttrace.attacks.backdoor_lab import create_patch_trigger
from ghosttrace.detection.anomaly_mad import compute_mad_anomaly_ranking
from ghosttrace.reconstruction.trigger_inverter import ReconstructedTrigger


def test_parameter_budget_under_500k():
    """Verify FR-01 and strict <500k parameter limit."""
    model = ForensicCNN(num_classes=10)
    params = count_parameters(model)
    assert params < 500_000, f"Expected <500k params, got {params}"
    meta = validate_model_constraints(model, max_params=500_000)
    assert meta["validated"] is True


def test_patch_trigger_application():
    """Verify trigger stamping math (1 - M) * x + M * P."""
    trig = create_patch_trigger(trigger_size=4, trigger_pos=(23, 23), target_class=7)
    x = torch.zeros((2, 1, 28, 28))
    stamped = trig.apply(x)
    assert stamped[:, :, 23:27, 23:27].mean().item() == 1.0
    assert stamped[:, :, :20, :20].mean().item() == 0.0


def test_mad_anomaly_detection_flags_small_norm_outlier():
    """Verify FR-03 MAD outlier scoring accurately flags an abnormally small trigger mask."""
    candidates = {}
    for c in range(10):
        norm = 3.2 if c == 7 else 28.0 + (c * 0.5)
        candidates[c] = ReconstructedTrigger(
            target_class=c,
            mask=torch.zeros((1, 28, 28)),
            pattern=torch.zeros((1, 28, 28)),
            l1_norm=norm,
            final_asr_on_ref=0.99,
            loss_history=[1.0, 0.1],
        )
    res = compute_mad_anomaly_ranking(candidates, mad_threshold=2.0)
    assert res["is_backdoor_flagged"] is True
    assert res["top_suspicious_class"] == 7
    assert res["max_anomaly_index"] > 4.0