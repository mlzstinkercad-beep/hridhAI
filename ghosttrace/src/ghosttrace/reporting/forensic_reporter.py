import json
from pathlib import Path
from typing import Any, Dict, Tuple


def export_forensic_reports(
    record: Dict[str, Any], output_dir: str | Path = "./artifacts"
) -> Tuple[Path, Path]:
    """FR-07: Export structured JSON record and standalone cyber-forensics HTML report."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    exp_id = record.get("experiment_id", "ghosttrace-run")

    json_path = out_dir / f"{exp_id}_report.json"
    html_path = out_dir / f"{exp_id}_report.html"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    det = record["backdoored_model_scan"]["detection"]
    mit = record["backdoored_model_scan"]["mitigation"]
    val = record["backdoored_model_scan"]["validation"]
    clean_ctrl = record["clean_control_scan"]["detection"]

    rows_html = ""
    for item in det["class_ranking"]:
        badge = (
            '<span style="color:#ff2a85;font-weight:bold;">FLAGGED</span>'
            if item["suspicious"]
            else '<span style="color:#00f5d4;">NOMINAL</span>'
        )
        rows_html += (
            f"<tr><td>#{item['rank']}</td><td>Class {item['class_id']}</td>"
            f"<td>{item['l1_norm']:.3f}</td><td>{item['anomaly_index']:.3f}</td>"
            f"<td>{item['ref_hijack_asr']*100:.1f}%</td><td>{badge}</td></tr>"
        )

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>GHOSTTRACE // Forensic Report ({exp_id})</title>
<style>
  body {{ background:#0b0f19; color:#e2e8f0; font-family:'Courier New',monospace; margin:32px; }}
  h1, h2 {{ color:#00f5d4; border-bottom:1px solid #1e293b; padding-bottom:8px; }}
  .grid {{ display:grid; grid-template-columns:repeat(3, 1fr); gap:16px; margin-bottom:24px; }}
  .card {{ background:#111827; border:1px solid #1f2937; padding:16px; border-radius:6px; }}
  .alert {{ border-color:#ff2a85; }}
  .metric {{ font-size:24px; font-weight:bold; color:#00f5d4; }}
  .metric-alert {{ font-size:24px; font-weight:bold; color:#ff2a85; }}
  table {{ width:100%; border-collapse:collapse; margin-top:12px; background:#111827; }}
  th, td {{ padding:10px; border:1px solid #1f293b; text-align:left; }}
  th {{ background:#1e293b; color:#00f5d4; }}
</style>
</head>
<body>
  <h1>GHOSTTRACE // NEURAL NETWORK FORENSIC REPORT</h1>
  <p>Experiment ID: <b>{exp_id}</b> | Config Hash: <b>{record['config_hash']}</b> | Timestamp: <b>{record['software']['timestamp_utc']}</b></p>

  <div class="grid">
    <div class="card alert">
      <div>INFECTED MODEL VERDICT</div>
      <div class="metric-alert">{'BACKDOOR DETECTED' if det['is_backdoor_flagged'] else 'CLEAN'}</div>
      <p>Hijacked Target: Class {det['top_suspicious_class']} (MAD Score: {det['max_anomaly_index']})</p>
    </div>
    <div class="card">
      <div>CLEAN CONTROL VERDICT</div>
      <div class="metric">{'FALSE POSITIVE' if clean_ctrl['is_backdoor_flagged'] else 'CLEAN VERIFIED'}</div>
      <p>Max Anomaly Score: {clean_ctrl['max_anomaly_index']} (Threshold: {clean_ctrl['mad_threshold']})</p>
    </div>
    <div class="card">
      <div>NEURAL REPAIR (THE CURE)</div>
      <div class="metric">ASR: {mit['pre_mitigation_ground_truth_asr']*100:.1f}% &rarr; {mit['post_mitigation_ground_truth_asr']*100:.1f}%</div>
      <p>Clean Accuracy: {mit['pre_mitigation_clean_accuracy']*100:.2f}% &rarr; {mit['post_mitigation_clean_accuracy']*100:.2f}%</p>
    </div>
  </div>

  <h2>Candidate Target-Class Anomaly Ranking (Infected Model)</h2>
  <table>
    <thead>
      <tr><th>Rank</th><th>Target Class</th><th>Reconstructed L1 Norm</th><th>MAD Anomaly Index</th><th>Ref Hijack ASR</th><th>Status</th></tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>

  <h2>Limitations & Threat Scope</h2>
  <p>{record['limitations']}</p>
</body>
</html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return json_path, html_path