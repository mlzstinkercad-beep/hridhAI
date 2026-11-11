#!/usr/bin/env python3
"""
GHOSTTRACE End-to-End Smoke Test Runner (MNIST)
Executes:
  - Milestone 1 (The Ghost): Clean & Poisoned Model Training (<500k params)
  - Milestone 2 (The Autopsy): Blind Trigger Inversion & MAD Outlier Detection
  - Milestone 3 (The Cure): Backdoor Unlearning & Utility/Security Verification
Pass `--ui` to launch the interactive Gradio Forensic Workstation after the smoke test.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from ghosttrace.orchestrator import GhostTraceOrchestrator
from ghosttrace.app.dashboard import create_dashboard


def main() -> None:
    parser = argparse.ArgumentParser(description="Run GHOSTTRACE MNIST Smoke Test")
    parser.add_argument("--config", default="configs/mnist_smoke.yaml", help="Path to YAML config")
    parser.add_argument("--ui", action="store_true", help="Launch Gradio forensic workstation")
    args = parser.parse_args()

    print("=" * 72)
    print("GHOSTTRACE // NEURAL NETWORK FORENSICS SMOKE TEST (MNIST)")
    print("=" * 72)

    orchestrator = GhostTraceOrchestrator(config_path=args.config)
    record = orchestrator.run_full_experiment()

    c_scan = record["clean_control_scan"]
    b_scan = record["backdoored_model_scan"]
    det = b_scan["detection"]
    val = b_scan["validation"]
    mit = b_scan["mitigation"]

    print(f"\n[MODEL CHECK] Architecture     : {record['architecture']} ({record['parameter_count']:,} / 500,000 max params)")
    print(f"[MILESTONE 1] Clean Model CA   : {c_scan['behaviour']['clean_accuracy']*100:.2f}%")
    print(f"[MILESTONE 1] Infected Model CA: {b_scan['behaviour']['clean_accuracy']*100:.2f}% | Ground-Truth ASR: {val['ground_truth_comparison']['ground_truth_test_asr']*100:.2f}%")
    print(f"[MILESTONE 2] Clean Control    : Flagged={c_scan['detection']['is_backdoor_flagged']} (Max MAD={c_scan['detection']['max_anomaly_index']})")
    print(f"[MILESTONE 2] Infected Scan    : Flagged={det['is_backdoor_flagged']} | Detected Target Class={det['top_suspicious_class']} (True={record['attack_ground_truth_eval_only']['target_class']}) | MAD={det['max_anomaly_index']}")
    print(f"[MILESTONE 2] Recon Validation : Recon Trigger Test ASR={val['reconstructed_trigger_test_asr']*100:.2f}% | Mask IoU={val['ground_truth_comparison']['trigger_mask_iou']}")
    print(f"[MILESTONE 3] Neural Repair    : Pre-ASR={mit['pre_mitigation_ground_truth_asr']*100:.2f}% -> Post-ASR={mit['post_mitigation_ground_truth_asr']*100:.2f}% | Post-CA={mit['post_mitigation_clean_accuracy']*100:.2f}%")
    print(f"[RUNTIME]     Total Time       : {record['total_pipeline_runtime_sec']}s (Budget: 600.0s)")
    print(f"[ARTIFACTS]   JSON Report      : {record['report_paths']['json']}")
    print(f"[ARTIFACTS]   HTML Report      : {record['report_paths']['html']}")
    print("=" * 72)

    # Smoke-test acceptance assertions (Section 15 of PRD)
    assert record["parameter_count"] <= 500_000, "Exceeded 500k parameter limit!"
    assert record["total_pipeline_runtime_sec"] < 600.0, "Exceeded 10-minute runtime limit!"
    assert b_scan["behaviour"]["clean_accuracy"] >= 0.96, "Infected model clean accuracy too low!"
    assert val["ground_truth_comparison"]["ground_truth_test_asr"] >= 0.95, "Backdoor implantation failed!"
    assert det["is_backdoor_flagged"] is True, "Scanner failed to flag backdoored model!"
    assert det["top_suspicious_class"] == record["attack_ground_truth_eval_only"]["target_class"], "Target class mismatch!"
    assert mit["post_mitigation_ground_truth_asr"] < 0.15, "Mitigation failed to neutralize backdoor!"
    print("ALL PRD ACCEPTANCE CRITERIA PASSED.")

    if args.ui:
        demo = create_dashboard(orchestrator)
        demo.launch(share=False)


if __name__ == "__main__":
    main()