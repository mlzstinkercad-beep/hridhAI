from typing import Any, Dict
import numpy as np
from ..reconstruction.trigger_inverter import ReconstructedTrigger


def compute_mad_anomaly_ranking(
    candidates: Dict[int, ReconstructedTrigger],
    mad_threshold: float = 2.0,
) -> Dict[str, Any]:
    """
    FR-03: Suspicious target-class analysis using Median Absolute Deviation (MAD).
    A backdoored target class requires an abnormally SMALL trigger L1 norm compared
    to clean classes.
    """
    classes = sorted(candidates.keys())
    norms = np.array([candidates[c].l1_norm for c in classes], dtype=np.float64)

    median_norm = float(np.median(norms))
    abs_dev = np.abs(norms - median_norm)
    # 1.4826 scales MAD to match standard deviation under a Gaussian assumption
    mad = float(1.4826 * np.median(abs_dev)) + 1e-6

    # One-sided small-norm anomaly index: positive when class L1 norm < median
    anomaly_scores = {
        c: round(float((median_norm - candidates[c].l1_norm) / mad), 4) for c in classes
    }

    ranked_classes = sorted(classes, key=lambda c: anomaly_scores[c], reverse=True)
    top_class = ranked_classes[0]
    max_score = anomaly_scores[top_class]
    is_flagged = bool(max_score >= mad_threshold)

    ranking_table = [
        {
            "rank": idx + 1,
            "class_id": c,
            "l1_norm": candidates[c].l1_norm,
            "anomaly_index": anomaly_scores[c],
            "ref_hijack_asr": candidates[c].final_asr_on_ref,
            "suspicious": bool(anomaly_scores[c] >= mad_threshold),
        }
        for idx, c in enumerate(ranked_classes)
    ]

    return {
        "is_backdoor_flagged": is_flagged,
        "mad_threshold": mad_threshold,
        "max_anomaly_index": max_score,
        "top_suspicious_class": int(top_class),
        "median_l1_norm": round(median_norm, 4),
        "mad_value": round(mad, 4),
        "class_ranking": ranking_table,
    }