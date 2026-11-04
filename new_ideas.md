2. The idea bank — grand, unsaturated
A. Harvest-Proof (your quantum idea, upgraded)
"Everything encrypted today will be readable by a quantum computer in 2035 — and adversaries are recording it NOW." ("Harvest now, decrypt later" is the real, named threat.) Build a hybrid post-quantum messenger/file vault using NIST-standardised algorithms (ML-KEM/Kyber via the open-source liboqs library), plus an AI triage engine that ranks an organisation's data by how long it must stay secret (medical records = 50 years → migrate first; today's OTP = irrelevant). Demo: "intercept" a classical-encrypted channel and crack it (simulated) while the PQC channel survives. Nobody at school level does this because it sounds hard — the libraries make it doable, and it's squarely Microsoft-flavoured (they're migrating Azure to PQC).

B. Sentinel: AI that protects AI
The meta-play. The world now runs on models, so the attack surface is the models: data poisoning, prompt injection, model theft. Build a guardian that scans a training dataset for poisoned samples (outlier detection in embedding space), watches a live model for prompt-injection jailbreaks, and issues a "model integrity certificate." Demo: poison 2% of an image dataset, show the detector catching exactly those samples; show a live jailbreak attempt being blocked. Judges backed by Microsoft will find this delicious — AI security is their hottest internal topic.

C. Festival Guardian: crowd-crush prediction
India-resonant and emotionally powerful (Hathras 2024, Kumbh 2025). Computer vision counts people from CCTV/top-view video using density estimation, no faces — "we count crowds, not people" is a killer privacy line. An AI model forecasts density 10–15 minutes ahead (crowd flow is physics + ML), and a simulation layer tests interventions (open which gate, divert which flow) before the crush forms. Demo: agent-based crowd simulation + live risk heatmap + warning. Fits Safety + Privacy + fairness (protects pilgrims of every class), and the track's own sample list mentions unsafe crowding — you'd be taking their hint to city scale.

D. Datamorph: privacy minimisation engine
For the DPDP Act era (India's data-protection law). Point the AI at any document, photo or screenshot; it detects all PII (faces, names, Aadhaar numbers, location metadata), auto-redacts to the minimum shareable version, and generates an audit trail. Optionally pair with a zero-knowledge-style demo: prove "I'm a student of this school" without revealing anything else. Simple to demo, zero saturation, and "Privacy" is the first word of the track.

E. Forest Guardian: the AI ranger
Acoustic AI detects gunshots and chainsaws in forest audio (public datasets exist), satellite hotspots flag fires (FIRMS again — reusable from your disaster stack), and a poaching-risk model suggests patrol routes (this is real deployed tech — PAWS — so it's defensible in Q&A). Demo: live audio classification + risk heatmap on a reserve map. Cinematic, grand, and protects both communities and rangers.

F. Firebreak: the misinformation containment engine
"Every disaster has a second wave: rumours." During cyclones and floods, false warnings kill. NLP matches claims against verified sources; network analysis detects coordinated bot amplification; then the system "injects" corrections at the right nodes of the spread graph. Demo: network-graph simulation of a rumour spreading with and without firebreak. Bonus: it bolts straight onto your disaster platform as a module.

G. TriageLens: post-quake structural triage
"The earthquake lasted 40 seconds. Deciding which 400 buildings to inspect takes weeks." Vibration-signature analysis (phone accelerometers again) + CV on street photos of cracks + AI that optimises the engineers' inspection route. This is the natural sequel to your disaster idea — after detection comes damage assessment. Demo: vibration classifier on public seismic data + damage-photo detection.

(Also decent, one line each: an autonomous cyber-defence agent — mini Security-Copilot that detects and explains live simulated attacks; a rogue-drone kill-switch for airport/school airspace.)





The second batch
H. GhostMesh — the network that survives the network's death
Every disaster platform (including yours) has an unspoken weakness: the cyclone that requires the SOS also kills the cell towers. Build an offline mesh where nearby phones/laptops become relay nodes over WiFi-Direct/Bluetooth, store-and-forward carries SOS packets hop-by-hop until one device finds connectivity, and an AI priority queue decides what gets squeezed through first (medical > missing person > updates) over tiny bandwidth. Demo: two laptops actually passing an SOS between them with no internet — judges feel this one. This is the missing organ of your disaster platform. Pitch line: "When the cyclone kills the network, the network becomes the shelter."

I. Rehearsal City — a digital twin where you rehearse the disaster before it happens
A simulated city where you inject any event — quake at 2 AM, flood at rush hour, fire in a market — and an agent-based simulation shows how it unfolds: where crowds jam, which hospitals saturate, where evacuation stalls. The AI then re-plans: shelter placement, route closure, ambulance pre-positioning — and quantifies lives saved between the naive plan and its plan. This is the single most interactive demo format possible: judges type "flood, 6 PM, railway station" and watch it play. It's also the planning brain that sits above your detection platform — same ecosystem, one more layer.

J. HeatShield — guardian for the 100 million who build India
Heat waves are India's silent mass-casualty event — election workers died on duty in 2024, construction and delivery workers collapse every summer. A lightweight wearable (or even just phone) fuses body-signal proxies + local weather + workload type into a personal heat-stroke risk score, enforces work–rest cycles, alerts the nearest shade/oral-rehydration point. The fairness/privacy twist that makes it Track 2: the data belongs to the worker, not the employer — no surveillance for productivity, only for survival. Extremely human story, trivially demoable with simulated biosignals.

K. WildWatch — the human–wildlife conflict shield
~58,000 snakebite deaths a year in India, plus elephant conflict in Kerala/Karnataka/WB. Fused model: seasonal + weather snakebite risk by village, crowdsourced sighting reports, acoustic/seismic early warning for elephant herds near villages, and a live map of the nearest stocked anti-venom. Alert flows before the encounter, not after. Fresh, terrifyingly real, and demoable on a district map with simulated sensors.

L. GreenCorridor — every organ gets a jet stream
An organ being transported has ~4–6 hours of viability and gets stuck at a traffic signal like everyone else. AI fuses live traffic prediction, ambulance position, hospital readiness and flight/heli availability to carve a time-optimal corridor — predicting signal pre-emption points, choosing the road-vs-air tradeoff, and allocating fairly when two patients compete for one corridor (fair dispatch math again — your Track 2 signature). Demo: city map, live countdown clock ticking down the viability window. Judges will lean forward.

M. The Algorithm Flight Recorder — who checks the AI that checks us?
As AI starts deciding who gets an ambulance first, whose loan is approved, who gets triaged — every one of those decisions needs a tamper-evident, plain-language, replayable audit record (hash-chained so nobody can quietly edit history). Build the "black box" + a court-style replay interface: here is the decision, here are the inputs, here is why, here is who is accountable. It's the "responsibly" of the track made into infrastructure. Pairs beautifully with the fairness dashboard idea from last time.

N. BiasScope — the instrument that measures "fairly"
The track description literally contains the word "fairly," and no one will bring an instrument for it. Feed any model + dataset (loan approvals, admissions, your own dispatch engine) into BiasScope → it runs counterfactual tests (same person, different name/gender/ZIP), computes disparate-impact metrics, and outputs a pass/fail audit report with fixes. Demo: audit a deliberately biased loan model live and watch it fail. Simple to build, instantly quotable on stage.

O. NeuroVault — privacy for the last private thing you own
The 10-year moonshot opener: brain-sensing wearables already exist and UNESCO just adopted a neurotech ethics framework; neural/emotional data is the next gold rush. Build the consent firewall: apps can request "stress level" from a wearable stream, and NeuroVault enforces purpose-limited inference — an app that's allowed to see "stress: high" is blocked from inferring emotion content, identity, or health state beyond what it asked for. Demo: a simulated wellness app trying to snoop beyond its consent and getting firewalled, with a live "inference ledger" of what was revealed. Abstract, but as a pitch it's unforgettable — you'd frame it as "the HTTPS of the brain, starting with today's fitness wearables."

P. OrbitWatch — 3.28 million km², zero blind spots
Illegal sand mining and quarrying destroys rivers and revenue across India, and inspection can't cover the ground. CV change-detection on free Sentinel-2 satellite imagery flags new pits, riverbed scarring and quarry expansion between passes, then ranks them by evidence strength for enforcement. Demo: a time-slider map showing an "illegal" quarry appearing over months, flagged automatically. Grand framing, genuinely buildable, and it protects both communities and the environment.

Q. GridGuard — the night the grid was attacked, the AI won
A simulated substation dashboard under a cyber-physical attack (the 2015 Ukraine grid attack is your historical anchor): wrong telemetry injected, breakers tripping in sequence, cascade beginning. An AI anomaly-detection layer spots the falsified sensor signatures, isolates the compromised segment, and keeps the cascade from spreading — with a security report at the end. Nation-state drama in a browser tab, and squarely Microsoft territory (operational-technology security).

How to filter "grand" from "big talk"
Before you fall in love with any of these, run the four gates:

Harm at scale — can you name who dies or loses what, per year, in India, if this doesn't exist?
AI load-bearing — if you delete the AI and the thing still works, it's an app, not an AI project.
Demo-able in the window — one working model + simulated world beats four slideware decks.
The freshness test — has a hackathon judge already seen this exact pitch twice that season?
