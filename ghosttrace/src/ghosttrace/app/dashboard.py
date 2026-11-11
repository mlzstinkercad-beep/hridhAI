import json
import numpy as np
import plotly.graph_objects as go
import gradio as gr
import torch

from ..orchestrator import GhostTraceOrchestrator

CYBER_CSS = """
.gradio-container { background-color: #0b0f19 !important; color: #e2e8f0 !important; font-family: 'JetBrains Mono', 'Courier New', monospace; }
.forensic-banner { background: linear-gradient(90deg, #0f172a 0%, #1e1b4b 100%); border: 1px solid #00f5d4; padding: 16px; border-radius: 8px; margin-bottom: 12px; }
"""


def tensor_to_rgb_image(tensor_1hw: torch.Tensor, scale: int = 8) -> np.ndarray:
    """Upscale a (1, 28, 28) tensor in [0, 1] into a crisp (224, 224, 3) uint8 image."""
    arr = tensor_1hw.squeeze(0).detach().cpu().clamp(0.0, 1.0).numpy()
    arr_uint8 = (arr * 255.0).astype(np.uint8)
    upscaled = np.repeat(np.repeat(arr_uint8, scale, axis=0), scale, axis=1)
    return np.stack([upscaled] * 3, axis=-1)


def build_mad_chart(ranking: list, threshold: float) -> go.Figure:
    classes = [f"Class {r['class_id']}" for r in ranking]
    scores = [r["anomaly_index"] for r in ranking]
    norms = [r["l1_norm"] for r in ranking]
    colors = ["#ff2a85" if r["suspicious"] else "#00f5d4" for r in ranking]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=classes,
            y=scores,
            marker_color=colors,
            text=[f"L1={n:.2f}" for n in norms],
            textposition="outside",
            name="MAD Anomaly Score",
        )
    )
    fig.add_hline(
        y=threshold,
        line_dash="dash",
        line_color="#ffbe0b",
        annotation_text=f"Flag Threshold ({threshold})",
    )
    fig.update_layout(
        title="Ghost Hunter // MAD Anomaly Index by Candidate Class",
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        yaxis_title="Signed MAD Anomaly Index",
    )
    return fig


def build_loss_chart(loss_history: list, target_class: int) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(range(1, len(loss_history) + 1)),
            y=loss_history,
            mode="lines+markers",
            line=dict(color="#00f5d4", width=2),
            name="Combined CE + L1 Loss",
        )
    )
    fig.update_layout(
        title=f"Trigger Inversion Optimization Curve (Candidate Class {target_class})",
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        xaxis_title="Optimization Step",
        yaxis_title="Lagrangian Loss",
    )
    return fig


def build_mitigation_chart(mit: dict) -> go.Figure:
    categories = ["Clean Accuracy (CA)", "Ground-Truth ASR", "Reconstructed Trigger ASR"]
    pre_vals = [
        mit["pre_mitigation_clean_accuracy"] * 100,
        (mit["pre_mitigation_ground_truth_asr"] or 0.0) * 100,
        mit["pre_mitigation_recon_asr"] * 100,
    ]
    post_vals = [
        mit["post_mitigation_clean_accuracy"] * 100,
        (mit["post_mitigation_ground_truth_asr"] or 0.0) * 100,
        mit["post_mitigation_recon_asr"] * 100,
    ]
    fig = go.Figure(
        data=[
            go.Bar(name="Pre-Mitigation (Infected)", x=categories, y=pre_vals, marker_color="#ff2a85"),
            go.Bar(name="Post-Mitigation (Repaired)", x=categories, y=post_vals, marker_color="#00f5d4"),
        ]
    )
    fig.update_layout(
        barmode="group",
        title="Neural Repair // Security vs. Utility Trade-Off (%)",
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        yaxis_title="Percentage (%)",
    )
    return fig


def create_dashboard(orchestrator: GhostTraceOrchestrator | None = None) -> gr.Blocks:
    orch = orchestrator or GhostTraceOrchestrator()

    def execute_pipeline():
        rec = orch.run_full_experiment()
        state = orch.latest_state
        det = rec["backdoored_model_scan"]["detection"]
        val = rec["backdoored_model_scan"]["validation"]
        mit = rec["backdoored_model_scan"]["mitigation"]
        beh = rec["backdoored_model_scan"]["behaviour"]
        c_det = rec["clean_control_scan"]["detection"]

        top_c = det["top_suspicious_class"]
        recon_trig = state["infected_candidates"][top_c]
        gt_trig = state["gt_trigger"]

        # Pick a clean non-target test sample to demonstrate the hijack
        test_ds = state["test_split"]
        non_target_idx = (test_ds.labels != top_c).nonzero(as_tuple=True)[0][0].item()
        sample_clean = test_ds.images[non_target_idx]
        sample_gt_stamped = gt_trig.apply(sample_clean.unsqueeze(0)).squeeze(0)
        sample_recon_stamped = recon_trig.apply(sample_clean.unsqueeze(0)).squeeze(0)