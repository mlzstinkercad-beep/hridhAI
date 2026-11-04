Winning the AI That Protects track at the hridhAI Hackathon requires exploiting how the Microsoft Garage jury grades the Grand Finale on November 28. Because 55% of the score comes from AI Integration & Technical Soundness (30%) and Live Prototype Functionality (25%), plus 10% specifically for Solved Preliminary Challenges, standard webcam YOLO detectors or LLM phishing wrappers will blend into the background.
Most teams treat Privacy, Security, and Safety as trade-offs—sacrificing privacy with cameras to get physical safety, or sending private data to cloud APIs to get security. You can secure a decisive edge by building a system that resolves this paradox through first-principles physics, signal processing, or latent-space geometry, paired with an interactive live demo on stage.
Option 1: Camera-Less Physical Safety via Multi-Path RF/Acoustic Phase Tomography
Current physical safety systems (elderly fall detection, school washroom/dorm distress monitoring, intruder alerts) rely on optical cameras that violate privacy and fail in darkness or smoke. Instead of optical pixels, use ambient wave physics to reconstruct 3D human posture and vital signs with zero visual identity leakage.
 * Core Breakthrough: Extract Channel State Information (CSI) phase and amplitude matrices from cheap ESP32 Wi-Fi nodes—or use 18–22 kHz inaudible FMCW ultrasonic sonar from a standard laptop speaker and microphone array.
 * AI Architecture: Feed raw complex-valued phase-Doppler spectrograms into a lightweight Physics-Informed Temporal Transformer that maps multipath wave reflections to a 17-joint 3D human skeleton and breathing micro-Doppler signature.
 * Mathematical Privacy Proof: Prove information-theoretic privacy by demonstrating that the mutual information between the low-dimensional RF/acoustic phase tensor and optical facial identity is zero (I(X_{\text{phase}}; Y_{\text{face}}) \to 0).
 * Live Stage Demo: Put tape over the laptop webcam, have a judge step behind a solid cardboard partition, and render their live 3D skeletal movement, breathing rate, and simulated fall alert in a real-time 3D engine.
Option 2: Biometric Phase-Cloaking & Vocal-Tract Physics Against "Digital Arrest" Scams
Passive deepfake detectors lose the arms race because every new generative model bypasses old classifiers. To protect Indian citizens from real-time AI voice-cloning and "Digital Arrest" extortion calls, flip the paradigm from passive detection to active latent poisoning and physical vocal-tract verification.
 * Active Outgoing Shield (Latent Poisoning): Inject sub-perceptual psychoacoustic phase perturbations (masked below the human auditory threshold) into outgoing voice audio that cause zero-shot voice cloners (like XTTS) to suffer attention collapse.
 * Incoming Call Verifier (Bicoherence Physics): Detect synthetic audio in real time by computing bispectral phase coherence and sub-glottal fluid resonance—physical invariants that neural vocoders fail to maintain across STFT frame boundaries.
 * Live Stage Demo: Record 5 seconds of a judge's voice on stage, run a local voice-cloning model live, and demonstrate how the unshielded recording clones their voice while the phase-cloaked recording outputs pure static.
Option 3: Zero-Trust Geometric Latent Firewall for Edge AI Agents
Current AI safety guardrails rely on secondary LLM judges or regex filters that add massive latency and break under adversarial token jailbreaks or indirect prompt injection. Solve AI security inside the model's linear algebra rather than at the text layer.
 * Core Breakthrough: Hook directly into the intermediate residual stream layers of a local open-weights model and monitor activation trajectories in real time.
 * Orthogonal Subspace Projection: Compute the principal subspace of harmful, PII-leaking, or prompt-injected states via Singular Value Decomposition (SVD) and project the hidden state vector onto the orthogonal complement (h' = h - V V^T h) mid-inference.
 * Performance Advantage: Neutralizes zero-day jailbreaks and prevents private database leakage in under 0.5\text{ ms} with zero external API calls.
 * Live Stage Demo: Connect a local AI agent to a mock hospital database, invite Microsoft judges to type live prompt-injection attacks, and visualize the 3D activation vector getting geometrically deflected away from the breach manifold in real time.
20-Day Execution Blueprint for Maximum Rubric Score
 * Days 1–4 (Baseline Failure Proof): Build the naive baseline first and record its exact mathematical failure modes (e.g., standard STFT spectrogram noise or token guardrail bypass) to lock in the 10% Solved Preliminary Challenges score.
 * Days 5–12 (Core Engine & Math Pipeline): Implement the custom signal-processing or latent-projection kernel in Python/C++ and train or calibrate the lightweight neural module on your local dataset.
 * Days 13–17 (3D Live Telemetry UI): Build a split-screen visualizer showing raw sensor/latent tensors on the left, the mathematical transformation in the middle, and the live protected output on the right so judges can see the math working.
 * Days 18–20 (Offline Stress-Testing): Package the entire pipeline to run 100% locally offline so venue Wi-Fi congestion or API latency cannot break your live demo.
Which of these three directions—RF/Acoustic Wave Sensing, Adversarial Voice Shielding, or Latent-Space AI Guardrails—best matches the hardware and stack you want to bring to the stage?
Absolutely. If we're aiming for **hridhAI – AI That Protects**, I wouldn't settle for another AI camera, chatbot, fraud detector, or generic cybersecurity dashboard.

I'd aim for something that makes the judges think:

**"Wait... you can actually do that with AI?"**

The strongest direction is to create a new layer of protection that doesn't just detect threats but fundamentally changes how systems handle them.

Here are 8 ambitious ideas. I'm prioritising concepts with impressive technical depth, mathematical foundations, and a live demonstration you can build.







## 6. AEGIS – A Self-Defending Data System

**Category:** Data Security

Imagine a document that actively protects itself.

Not just through encryption, but through intelligent access control.

**The concept:**

AEGIS creates protected data containers.

Every time someone requests access:
- Verify their identity.
- Evaluate their permissions.
- Check the purpose of access.
- Restrict what information they can retrieve.
- Record the access event.

An additional AI layer detects suspicious access patterns.

For example:

A user has permission to view a document but suddenly attempts to download 500 confidential records.

AEGIS detects the abnormal behaviour and blocks further access.

**Interesting technology:**
- Attribute-based access control.
- AES-256-GCM.
- Cryptographic key management.
- Behavioural anomaly detection.
- Zero-trust architecture.

**Grand demo:**

Create a mock hospital database with patient records.

Let different users access different records. Simulate an account compromise and demonstrate how AEGIS limits the damage.

**The big idea:** Data should remain protected even after it enters an application.



---

# My Ranking: Which Ideas Have the Greatest Potential?


| Idea | Innovation potential | Technical depth | Live demo |
|---|---|---|---|
| PHANTOM | Very high | Very high | Excellent |
| MIRROR | High | High | Excellent |
| GHOSTNET | Very high | High | Excellent |
| SENTINEL | Very high | Very high | Excellent |
| ECHO | High | Very high | Excellent |
| AEGIS | High | High | Excellent |
| ORACLE | High | High | Excellent |
| PARALLAX | Very high | Very high | Excellent |

# My Top 3 Recommendations









## 1. RF as the New X-Ray: Device-Free Sensing (your Wi-Fi idea, taken seriously)

**The unsolved problem:** Wi-Fi/radio sensing (CSI-based) can detect falls, breathing, heart rate, presence through walls — no cameras, no wearables. But it **fails to generalize across rooms, hardware, and people**, and **multi-person scenes "entangle" signals so targets become indistinguishable**. Occlusion handling and real-world deployment remain open. [Recent survey, 2025](https://arxiv.org/html/2503.09734v1). The [802.11bf standard is being built right now](https://ieeexplore.ieee.org/document/10870408) — meaning the governance layer doesn't exist yet.

**The breakthrough thesis — two directions:**
- *Sensing:* domain-generalized RF models; vital signs through rubble for earthquake rescue (NDRF digs by hand today); privacy-preserving crowd analytics at Kumbh-scale events **without a single camera** (solves the CCTV-vs-privacy paradox from our last brief).
- *The privacy paradox:* RF sees through walls. The same tech that protects your grandmother (fall detection) is the perfect stalker tool. Research the **governance layer itself**: what does "informed consent" even mean when the sensor is invisible and the router next door is the camera?

**Your slice:** ESP32 CSI Toolkit / Nexmon on a Raspberry Pi — presence + fall detection in one room, then *measure exactly how badly it generalizes* to a second room. A rigorous "RF privacy threat model" paper is genuinely novel at any level. [Hardware is ~₹2,000 and the toolkit is open](https://esp32-csi-tool.gitlab.io).

---

## 2. The Anti-AI Shield: Adversarial Privacy (your "corrupt AI to protect people" idea)

**The unsolved problem:** Tools that cloak people/AI content from AI surveillance exist (Fawkes, Glaze, Nightshade — anti-facial-recognition, anti-style-scraping, poisoning-as-protection) but **physical-world transferability fails** — they break under real lighting, angles, adaptive adversaries. The gap: *robust, usable, consent-based evasion*.

**Key evidence:** A peer-reviewed Sept 2025 IEEE paper — **CIPS: adversarial clothing that reliably breaks person-detection models in the physical world** — shows this is active, publishable frontier research, not sci-fi. [(open access)](https://ieeexplore.ieee.org/ieliel8/6287639/10887398/11150413.pdf)

**The breakthrough thesis:** flip from "evade everything" to **consent infrastructure**: garments/signage/perturbations that *assert* privacy (like a do-not-track for the physical world) + the counter-research question every judge will ask: *who gets to opt out of being seen, and does that break legitimate safety systems?* That tension **is** the research contribution — a formal "physical-world consent threat model" doesn't exist.

**⚠️ The line you cannot cross:** this is dual-use. Framed as protecting the photographed, artists, and minors from non-consensual recognition = strong, defensible, novel. Framed as "evading detection" generally = disqualification risk and genuinely harmful. Judges will probe this — have the ethics boundary as an explicit section of your paper.

**Your slice:** evaluate existing cloaking tools' robustness against adaptive/white-box attackers on open models; build the threat model; test wearable perturbations *on yourselves, with consent, on campus*. No real-world deployment against others' systems.

---

## 3. Guardians Watching the Machines: AI Oversight as a Discipline (your "AI that protects humans from AI")

**The unsolved problem:** Interpretability-based lie-detection is seductive but fragile — a 2025 benchmark study found **deception probes hit >95% accuracy in-distribution but collapse to near-random on out-of-distribution scenarios**. [(Probing study)](https://arxiv.org/html/2509.07773v1). Nobody has an oversight layer that *generalizes*. Meanwhile autonomous agents are being deployed faster than any runtime monitoring exists.

**The breakthrough thesis:** an **"immune system" architecture for agent ecosystems** — runtime behavioral anomaly detection for autonomous agents, honeypot decoys that lure misbehaving agents, cross-examination protocols (one AI adversarially auditing another's reasoning chain). Related frontier proof-of-concept: DARPA's AIxCC finalist "Mayhem" [autonomously found and patched a real Jenkins zero-day](https://www.wired.com/story/darpa-aixCC-cyber-defense-ai) — machine-guarding-machine works in cyber; nobody has built the equivalent for *behavioral* trustworthiness.

**Your slice:** red-team/blue-agent sandbox: an agent with a benign goal + temptation to deceive, and a monitor trained to catch it — then **systematically vary the scenario and measure where oversight breaks**. That failure map, not the monitor itself, is the publishable artifact.

---

## 4. The Q-Day Gap: Beating Quantum With Classical (your quantum idea, made concrete)

Two defensible framings — pick one:

**(a) Defense:** Nation-scale data (Aadhaar, UPI archives, health records) is being harvested *now* to decrypt *later*. NIST finalized PQC standards (ML-KEM, ML-DSA, SLH-DSA) in 2024; [JPMorgan just ran the first production hybrid post-quantum TLS](https://www.jpmorgan.com/technology/technology-blog/quantum-safe-crypto-tls) — and India's DPI has **no public migration timeline**. A "crypto-agility audit" framework for Indian public infrastructure would be genuinely policy-relevant research.

**(b) Classical-beats-quantum:** the dequantization program — classical algorithms matching claimed quantum advantage — is real, active CS theory (tensor-network simulations [already challenged supremacy claims](https://www.nature.com/articles/d41586-023-02501-4)). Likely too deep for 9–12 to *contribute* original results, but a rigorous reproduction/survey with a novel benchmark comparison is feasible.

**Your sweet spot: (a).** Benchmark PQC algorithms on low-cost hardware (₹500 Raspberry Pi Zero — embedded PQC benchmarking is [an established paper genre](https://link.springer.com/article/10.1007/s12083-024-01688-9)), then apply it: what would migrating *your* state's digital services actually cost/require? That's a winnable research paper with real-world weight.

---

## 5. The Missing Coordination Layer for Disasters (your disaster idea — sharpened)

**The insight that makes it grand:** India (and everyone) has *detection* (satellites, IMD, sensors) and weak *prediction*. What doesn't exist anywhere is the **control-and-coordination layer** — the closed loop between "flood predicted" and "that specific bus turns around, that nurse is dispatched, that slum is evacuated in the right order." The Odisha cyclone story (1999: ~10,000 dead → 2019 Fani, comparable storm: <100 dead) proves coordination, not sensing, is the life-or-death variable.

**Documented failures:** In the 2023 South Lhonak GLOF (Sikkim), [sensors deployed on the moraine were washed away with the slope itself — no telemetry survived](https://www.mdpi.com/2072-4292/16/11/2032). MyShake-style smartphone EEW hits 92% sensing success but [gaps remain in local detection and last-mile alerting](https://www.frontiersin.org/journals/earth-science/articles/10.3389/feart.2023.1117166/full). Lightning kills ~2,500 Indians/year across 44M+ strikes — [the coordination gap, not detection gap, dominates](https://link.springer.com/article/10.1007/s11069-024-06957-2).

**The breakthrough thesis:** **communication-degraded multi-agent coordination** — when towers fall and sensors wash away, how do humans+drones+vehicles coordinate on partial, stale information? Pre-computed "graceful degradation" playbooks, mesh-networked on-device agents, digital-twin rehearsal before the disaster.

**Your slice:** agent-based simulation (Mesa/gym) of a real local hazard — evacuation policy learning under *simulated* 30/60/90% infrastructure loss. Fully feasible, zero safety risk, and the deliverable (policy + failure analysis) is exactly what the "anticipatory action" literature says is missing.

---


## 7. The Spoof-Proof Navigation Shield

GPS jamming/spoofing incidents in aviation and shipping are escalating. Unsolvable today: cheap, verifiable PNT (positioning-navigation-timing) for civilian drones, aircraft, and taxis. Your slice: spoofing *detection* (not spoofing!) via sensor-fusion consistency checks on open/simulated datasets. Strong security narrative, clean dual-use line (detection is defensive by definition).



## Decision Matrix

| Direction | Novelty | 9–12 Feasibility | India advantage | Demo power | Ethics risk |
|---|---|---|---|---|---|
| 1. RF sensing + privacy paradox | High | **High** (₹2k hardware) | High | High | Medium |
| 2. Adversarial privacy/consent | Very high | Medium | High | High | **High** |
| 3. AI oversight sandbox | Very high | **High** (small open models) | Medium | Medium | Low |
| 4. PQC readiness | High | **High** | **Very high** | Low | Low |
| 5. Coordination layer | Very high | **High** (simulation) | **Very high** | Medium | Low |
| 6. Sentient infrastructure | High | **High** | High | **High** | Low |
| 7. GNSS integrity | High | Medium | Medium | Medium | Low |


