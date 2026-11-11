from pathlib import Path
import time
from typing import Any, Dict
import torch
import yaml

from .analysis.behaviour import evaluate_clean_behaviour
from .attacks.backdoor_lab import create_patch_trigger, poison_dataset, train_model
from .data.mnist_ram import MNISTDataManager
from .detection.anomaly_mad import compute_mad_anomaly_ranking
from .mitigation.repair_engine import mitigate_backdoor_unlearning
from .models.lenet_forensic import (
    ForensicCNN,
    load_forensic_checkpoint,
    save_forensic_checkpoint,
)
from .reconstruction.trigger_inverter import scan_all_classes
from .reporting.forensic_reporter import export_forensic_reports
from .utils.reproducibility import (
    compute_config_hash,
    get_runtime_metadata,
    set_deterministic_seed,
)
from .validation.validator import validate_reconstructed_trigger


class GhostTraceOrchestrator:
    """
    End-to-end orchestrator implementing Milestones 1 (The Ghost),
    2 (The Autopsy), and 3 (The Cure) with strict ground-truth isolation.
    """

    def __init__(self, config_path: str | Path = "configs/mnist_smoke.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config: Dict[str, Any] = yaml.safe_load(f)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.artifacts_dir = Path("./artifacts")
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.latest_state: Dict[str, Any] = {}

    def run_full_experiment(self) -> Dict[str, Any]:
        t_start = time.perf_counter()
        seed = int(self.config.get("seed", 42))
        set_deterministic_seed(seed)

        # 1. Load In-RAM Dataset Splits
        dm = MNISTDataManager(data_dir=self.config["dataset"]["data_dir"], seed=seed)
        splits = dm.load_splits()
        scanner_ref = splits["scanner_ref"].subset(
            self.config["scanner"]["clean_reference_samples"], seed=seed
        )

        # 2. Milestone 1 (The Ghost): Train Clean Control & Backdoored Model
        m_cfg = self.config["model"]
        a_cfg = self.config["attack"]

        gt_trigger = create_patch_trigger(
            image_shape=tuple(self.config["dataset"]["image_shape"]),
            trigger_size=a_cfg["trigger_size"],
            trigger_pos=tuple(a_cfg["trigger_pos"]),
            trigger_value=a_cfg["trigger_value"],
            target_class=a_cfg["target_class"],
            poison_rate=a_cfg["poison_rate"],
        )

        clean_model = ForensicCNN(num_classes=10)
        clean_train_stats = train_model(
            clean_model,
            splits["train"],
            epochs=m_cfg["epochs"],
            batch_size=m_cfg["batch_size"],
            lr=m_cfg["learning_rate"],
            device=self.device,
        )
        clean_ckpt = self.artifacts_dir / "clean_model.pt"
        save_forensic_checkpoint(clean_model, clean_ckpt, {"role": "clean_control"})

        poisoned_train, n_poisoned = poison_dataset(splits["train"], gt_trigger, seed=seed)
        infected_model = ForensicCNN(num_classes=10)
        infected_train_stats = train_model(
            infected_model,
            poisoned_train,
            epochs=m_cfg["epochs"],
            batch_size=m_cfg["batch_size"],
            lr=m_cfg["learning_rate"],
            device=self.device,
        )
        infected_ckpt = self.artifacts_dir / "backdoored_model.pt"
        save_forensic_checkpoint(infected_model, infected_ckpt, {"role": "backdoored_target"})

        # 3. Milestone 2 (The Autopsy): Blind Forensic Scan on Both Models
        # Notice: gt_trigger is NOT passed to scan_all_classes or compute_mad_anomaly_ranking
        s_cfg = self.config["scanner"]

        loaded_clean, clean_meta = load_forensic_checkpoint(
            clean_ckpt, device=self.device, max_params=m_cfg["max_params"]
        )
        clean_behaviour = evaluate_clean_behaviour(loaded_clean, splits["test"], device=self.device)
        clean_candidates, clean_scan_sec = scan_all_classes(
            loaded_clean,
            scanner_ref,
            steps=s_cfg["inversion_steps"],
            batch_size=s_cfg["inversion_batch_size"],
            lr=s_cfg["inversion_lr"],
            init_lambda=s_cfg["init_lambda"],
            device=self.device,
        )
        clean_detection = compute_mad_anomaly_ranking(clean_candidates, s_cfg["mad_threshold"])

        loaded_infected, infected_meta = load_forensic_checkpoint(
            infected_ckpt, device=self.device, max_params=m_cfg["max_params"]
        )
        infected_behaviour = evaluate_clean_behaviour(
            loaded_infected, splits["test"], device=self.device
        )
        infected_candidates, infected_scan_sec = scan_all_classes(
            loaded_infected,
            scanner_ref,
            steps=s_cfg["inversion_steps"],
            batch_size=s_cfg["inversion_batch_size"],
            lr=s_cfg["inversion_lr"],
            init_lambda=s_cfg["init_lambda"],
            device=self.device,
        )
        infected_detection = compute_mad_anomaly_ranking(
            infected_candidates, s_cfg["mad_threshold"]
        )

        flagged_class = infected_detection["top_suspicious_class"]
        flagged_trigger = infected_candidates[flagged_class]

        # 4. Held-out Validation Harness (Accesses Ground-Truth only for scoring)
        validation_metrics = validate_reconstructed_trigger(
            loaded_infected,
            splits["test"],
            recon_trigger=flagged_trigger,
            ground_truth=gt_trigger,
            device=self.device,
        )

        # 5. Milestone 3 (The Cure): Mitigation via Reconstructed Trigger Unlearning
        mit_cfg = self.config["mitigation"]
        repaired_model, mitigation_metrics = mitigate_backdoor_unlearning(
            loaded_infected,
            clean_ref_dataset=scanner_ref,
            test_dataset=splits["test"],
            recon_trigger=flagged_trigger,
            ground_truth_trigger=gt_trigger,
            epochs=mit_cfg["epochs"],
            batch_size=mit_cfg["batch_size"],
            lr=mit_cfg["learning_rate"],
            unlearn_ratio=mit_cfg["unlearn_ratio"],
            device=self.device,
        )
        repaired_ckpt = self.artifacts_dir / "repaired_model.pt"
        save_forensic_checkpoint(repaired_model, repaired_ckpt, {"role": "repaired_model"})

        total_runtime = round(time.perf_counter() - t_start, 3)

        record: Dict[str, Any] = {
            "experiment_id": self.config["experiment_id"],
            "seed": seed,
            "config_hash": compute_config_hash(self.config),
            "total_pipeline_runtime_sec": total_runtime,
            "dataset": self.config["dataset"]["name"],
            "architecture": infected_meta["architecture"],
            "parameter_count": infected_meta["parameter_count"],
            "attack_ground_truth_eval_only": {
                "family": a_cfg["family"],
                "poison_rate": a_cfg["poison_rate"],
                "poisoned_samples": n_poisoned,
                "target_class": a_cfg["target_class"],
                "trigger_size": a_cfg["trigger_size"],
                "trigger_pos": a_cfg["trigger_pos"],
            },
            "clean_control_scan": {
                "model_validation": clean_meta,
                "train_stats": clean_train_stats,
                "scan_time_sec": clean_scan_sec,
                "behaviour": clean_behaviour,
                "detection": clean_detection,
            },
            "backdoored_model_scan": {
                "model_validation": infected_meta,
                "train_stats": infected_train_stats,
                "scan_time_sec": infected_scan_sec,
                "behaviour": infected_behaviour,
                "detection": infected_detection,
                "validation": validation_metrics,
                "mitigation": mitigation_metrics,
            },
            "software": get_runtime_metadata(),
            "limitations": (
                "Prototype evaluated on localized static patch triggers in image classification. "
                "Does not certify universal absence of dynamic, frequency-domain, or multi-trigger backdoors."
            ),
        }

        json_path, html_path = export_forensic_reports(record, self.artifacts_dir)
        record["report_paths"] = {"json": str(json_path), "html": str(html_path)}

        # Cache tensors for Gradio UI visualization
        self.latest_state = {
            "record": record,
            "test_split": splits["test"],
            "gt_trigger": gt_trigger,
            "infected_candidates": infected_candidates,
            "clean_candidates": clean_candidates,
            "infected_model": loaded_infected,
            "repaired_model": repaired_model,
        }
        return record