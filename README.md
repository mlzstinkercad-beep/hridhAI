# hridhAI — AI That Protects

**hridhAI** is a student-led research and engineering workspace exploring how AI, signal processing, mathematics, and software can protect people from emerging threats.

We are interested in systems that do more than classify a problem: systems that investigate, prevent, contain, or recover from it.

Our work spans model security, voice authenticity, privacy-preserving sensing, AI oversight, and resilient infrastructure. Some entries are active prototype directions; others are research hypotheses that still need feasibility tests. We distinguish ideas from validated implementations.

---

## 🧭 The project map

| Direction | What it explores | Current position |
|---|---|---|
| GHOSTTRACE | Finding, reconstructing, and mitigating hidden backdoors in AI models | Main research build |
| MAYA | On-device detection of synthetic or cloned voices | Practical MVP direction |
| RF sensing | Detecting presence, movement, or distress without cameras | Feasibility research |
| Zero-Trust Geometric Firewall | Enforcing safety constraints inside model representations | Research wildcard |
| PQC Readiness | Measuring the work needed to migrate systems to post-quantum cryptography | Research / benchmarking |
| Other explorations | Privacy, AI oversight, disaster response, infrastructure, space, and science | Idea backlog |

---

## 🧪 Active project directions

### 👻 GHOSTTRACE — Neural Network Forensics

**The question:** Can we investigate an AI model that behaves normally but has been secretly modified to produce a targeted wrong answer when a hidden trigger appears?

GHOSTTRACE is a proposed forensic pipeline for image-classification models. It aims to:

1. Establish the model's normal behaviour on clean inputs.
2. Detect suspicious trigger-dependent behaviour.
3. Reconstruct a candidate trigger without being told what it is.
4. Identify the output class that the trigger appears to hijack.
5. Test mitigation and measure the effect on clean accuracy.

**Research milestones**

- **The Ghost:** Create a controlled backdoored model and verify the behaviour.
- **The Autopsy:** Give the scanner the model without revealing the trigger; attempt to reconstruct it.
- **The Cure:** Test mitigation and compare attack success rate and clean accuracy before and after.

**Initial scope:** Small image-classification models and controlled datasets such as MNIST or CIFAR-10. A practical stack could use PyTorch, NumPy, OpenCV, Matplotlib/Plotly, Gradio, and a Colab GPU.

**Research honesty:** Backdoor detection and trigger reconstruction already have substantial prior work, including Neural Cleanse, BaDExpert, and DeBackdoor. Our contribution must be demonstrated through the pipeline, constraints, evaluation, and failure analysis—not by claiming the entire problem is new.

Project notes: [GhostTrace.md](GhostTrace.md) · [GHOSTTRACE PRD](GHOSTTRACE_PRD_v1.docx)

### 🛡️ MAYA — Voice Authenticity Protection

**The question:** Can a phone help someone recognise when a familiar-sounding voice may be synthetic?

MAYA is an Android-first concept for privacy-conscious voice anti-spoofing. The proposed MVP uses an on-device model to analyse short audio segments and present an understandable risk signal, with no audio upload by design.

Potential components:

- Audio feature extraction and anti-spoofing inference.
- A compact model such as an appropriately validated AASIST-derived model.
- A clear verdict with confidence and evidence indicators.
- Local-only processing and minimal diagnostic logging.

**Important platform constraint:** Ordinary Android apps generally cannot freely capture the audio stream of every cellular call. Call-audio access depends on Android versions, permissions, device/OEM behaviour, and approved roles or APIs. Live-call monitoring is therefore a technical validation task—not a capability to promise before proving it on the target phone. A safe first demo can analyse supplied or app-captured audio samples.

**Evaluation goals:** Test real and synthetic voices across speakers, languages, recording conditions, codecs, and unseen generators. Report false alarms and missed detections, not just headline accuracy.

Project notes: [MAYA-PRD.md](MAYA-PRD.md)

---

## 🔎 Prioritised from `must_read.md`

These are the current planning shortlist and rough effort estimates recorded in the repository. They are estimates for scoping—not measured build times, guarantees, or independent feasibility results.

| Priority / type | Direction | Planning estimate | Why it is here | Main question to resolve |
|---|---|---:|---|---|
| Main research build | **GHOSTTRACE** | **~30 hours** | Important model-security problem with a strong forensic demo | Can trigger reconstruction and mitigation be evaluated reliably with limited data and compute? |
| Feasibility study | **RF sensing** | **~4 hours** | Camera-free sensing could protect privacy while detecting presence or distress | Who is the user, what is the real deployment use case, and does it generalise across rooms and hardware? |
| Practical MVP | **MAYA (upgraded)** | **~5 hours** | Focused, understandable problem with a potentially buildable prototype | Can the chosen Android audio-capture route actually work on the target device? |
| Research wildcard | **Post-quantum cryptography readiness** | **~12 hours** | Highly relevant to long-term security and migration planning | Can we produce a concrete benchmark or migration audit rather than a purely conceptual presentation? |
| Research wildcard | **Zero-Trust Geometric Firewall** | **~20 hours** | Interesting attempt to enforce safety within a model's hidden representations | Can a projection-based intervention reduce harmful behaviour without unacceptable utility loss or latency? |

### How to read the shortlist

- **Buildable first:** MAYA, provided the audio-capture scope is validated early.
- **Strong research challenge:** GHOSTTRACE, with a deliberately narrow first experiment.
- **Do a fast feasibility spike before committing:** RF sensing.
- **Keep as deeper research tracks:** PQC readiness and the geometric firewall. Both need a measurable prototype and careful comparison against existing work.

---

## 🧠 The wider research backlog

These concepts are retained as directions to investigate. They are not all selected for the hackathon, and none should be described as novel or working until tested against prior work and real baselines.

<details>
<summary><strong>🛰️ RF sensing and privacy-preserving awareness</strong></summary>

Explore Wi-Fi Channel State Information (CSI), radio or acoustic reflections for device-free presence, movement, breathing, or fall-related signals. The promise is useful awareness without conventional video surveillance.

Research questions:

- How well does a model transfer between rooms, people, and hardware?
- Can it separate multiple people or distinguish movement from environmental noise?
- What consent, security, and misuse protections are needed for sensing that may operate without a person's awareness?

A first experiment should be modest: collect consent-based data in one room, test a second room, and quantify the performance drop. Do not claim that RF sensing provides perfect privacy or reliable through-wall identification.

</details>

<details>
<summary><strong>🧱 Zero-Trust Geometric Firewall</strong></summary>

Investigate whether intermediate representations in an AI model can be monitored or constrained to reduce unsafe actions, prompt-injection effects, or sensitive-data leakage.

A proposed experiment is to identify activation directions associated with a controlled set of unsafe behaviours, then test whether a geometric intervention changes those behaviours while preserving useful outputs.

Key measurements: attack success rate, benign-task performance, false blocks, latency, and transfer to unseen attacks. This is a research hypothesis, not a proven universal jailbreak defence.

</details>

<details>
<summary><strong>👁️ Guardians Watching the Machines — AI Oversight</strong></summary>

Build a controlled sandbox in which one agent performs a task and a separate monitor checks for policy violations, deception-like behaviour, or suspicious tool use. The research value is in testing where the monitor fails when scenarios, incentives, and environments change.

The goal is not to claim that an AI can reliably read another AI's intentions. Measure generalisation, false positives, false negatives, and monitor evasion.

</details>

<details>
<summary><strong>🕶️ Anti-AI Shield — Adversarial Privacy</strong></summary>

Study consent-based ways to reduce unwanted AI inference from images, audio, or other personal data. Evaluate existing protection methods under realistic transformations and adaptive attacks.

Keep the scope ethical and defensive: use consented subjects and controlled datasets, and report the impact on legitimate safety or accessibility systems as well as privacy protection.

</details>

<details>
<summary><strong>🔐 AEGIS — Self-Defending Data System</strong></summary>

A protected-data workflow combining identity, purpose-aware access control, least privilege, audit trails, and anomaly detection. A useful prototype could use a synthetic hospital dataset and demonstrate how excessive or suspicious access is restricted.

</details>

<details>
<summary><strong>🧾 Datamorph — Privacy Minimisation Engine</strong></summary>

Detect and redact personal information from documents, screenshots, or images before sharing. The research question is how to minimise disclosure while preserving the information needed for a legitimate task. Evaluate missed sensitive fields and unnecessary redactions.

</details>

<details>
<summary><strong>🌐 PQC Readiness and Crypto-Agility</strong></summary>

Benchmark post-quantum cryptographic algorithms on constrained hardware and build a practical inventory or migration-readiness checklist. The strongest version is an evidence-based comparison of performance, memory, key sizes, and integration effort—not a claim to have invented post-quantum cryptography.

</details>

<details>
<summary><strong>🚨 Disaster intelligence and resilient infrastructure</strong></summary>

- **Firebreak:** Track how disaster misinformation spreads in a simulated network and test where corrections reduce propagation.
- **Rehearsal City:** Simulate floods, earthquakes, or fires and compare evacuation or resource-allocation strategies.
- **GridGuard / BLACKOUT:** Simulate faults and cyber-physical attacks on a power network; test detection and containment strategies.
- **SEISMOS:** Analyse seismic waveforms and investigate event detection under noisy or incomplete data. This is not earthquake prediction.

</details>

<details>
<summary><strong>🛰️ Space, biomedical, and scientific computing</strong></summary>

- **ORBITAL:** Simulate satellite conjunctions and compare collision-risk estimates or avoidance options under uncertainty.
- **GHOSTDATA:** A controlled laboratory for membership-inference and model-inversion risks using synthetic private datasets.
- **PROTEUS:** Explore protein-sequence and mutation-effect prediction; computational predictions are not laboratory validation.
- **RESIST-X:** Study genomic associations with antibiotic resistance; outputs are research predictions, not treatment advice.
- **MOLECULE-X:** Rank candidate molecules by predicted properties; model scores do not establish safety or efficacy.
- **NeuroVault:** Explore purpose-limited access to sensitive wearable or neural data.

</details>

---

## 🧰 How we work

1. **Define the threat.** Who is being protected, from whom, and under what conditions?
2. **Read prior work.** Identify existing methods before making novelty claims.
3. **Build a baseline.** A new method needs a fair comparison.
4. **Test the hard cases.** Include unseen data, changing environments, and adversarial conditions where relevant.
5. **Measure trade-offs.** Accuracy alone is not enough; report latency, resource use, false alarms, privacy, and usability.
6. **Show the mechanism.** A live demo should expose what the system is doing, not just display a dramatic verdict.
7. **State limitations.** Separate measured results, design goals, assumptions, and future work.

### 🔬 Research principles

- Defensive, consent-based, and privacy-conscious experimentation.
- No fabricated metrics, mock results presented as real, or unsupported “first ever” claims.
- Reproducible experiments and clearly described datasets.
- Human oversight for high-impact decisions.
- A working, narrow prototype is better than an enormous unverified promise.

---

## 🗂️ Repository guide

| File | Purpose |
|---|---|
| [GhostTrace.md](GhostTrace.md) | GHOSTTRACE concept, pipeline, milestones, and research framing |
| [GHOSTTRACE_PRD_v1.docx](GHOSTTRACE_PRD_v1.docx) | GHOSTTRACE product requirements |
| [MAYA-PRD.md](MAYA-PRD.md) | MAYA product requirements and proposed architecture |
| [must_read.md](must_read.md) | Prioritised ideas and effort estimates |
| [ideas.md](ideas.md) | Broader research concepts and technical directions |
| [new_ideas.md](new_ideas.md) | Additional project concepts across domains |
| [shortlist.md](shortlist.md) | Working shortlist |
| [Untitled 1.png](Untitled%201.png) | Original project QR graphic |

---

## 📱 Project link / QR

Scan the original QR graphic below to open the destination encoded in the project image.

<p align="center">
  <img src="Untitled%201.png" alt="Original hridhAI project QR code" width="320" />
</p>

---

<p align="center">
  **hridhAI — AI That Protects**  
  *Not waiting for the future to become safer. Building toward it.*
</p>
