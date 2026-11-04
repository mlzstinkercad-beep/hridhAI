2. The idea bank — grand, unsaturated
A. Harvest-Proof (your quantum idea, upgraded)
"Everything encrypted today will be readable by a quantum computer in 2035 — and adversaries are recording it NOW." ("Harvest now, decrypt later" is the real, named threat.) Build a hybrid post-quantum messenger/file vault using NIST-standardised algorithms (ML-KEM/Kyber via the open-source liboqs library), plus an AI triage engine that ranks an organisation's data by how long it must stay secret (medical records = 50 years → migrate first; today's OTP = irrelevant). Demo: "intercept" a classical-encrypted channel and crack it (simulated) while the PQC channel survives. Nobody at school level does this because it sounds hard — the libraries make it doable, and it's squarely Microsoft-flavoured (they're migrating Azure to PQC).


D. Datamorph: privacy minimisation engine
For the DPDP Act era (India's data-protection law). Point the AI at any document, photo or screenshot; it detects all PII (faces, names, Aadhaar numbers, location metadata), auto-redacts to the minimum shareable version, and generates an audit trail. Optionally pair with a zero-knowledge-style demo: prove "I'm a student of this school" without revealing anything else. Simple to demo, zero saturation, and "Privacy" is the first word of the track.

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
01. GHOSTTRACE — Neural Network Autopsy
Top contender
- Problem: AI models can contain hidden backdoors that activate only when a specific trigger is present.
- Build: Train an infected neural network, then develop a scanner that attempts to reconstruct its secret trigger without being told what it is.
- WOW demo: A perfectly normal AI suddenly misclassifies an image. Your scanner reconstructs the hidden pattern.
- Engineering: Neural Cleanse-style optimisation, activation analysis, model forensics.
- Colab: Excellent.
- Research angle: Can we detect triggers the scanner wasn't specifically designed to find?
  
  Research background: model supply-chain poisoning. 
  DOI+1


02. CASCADE — Predicting a Cyberattack Before It Spreads
- Problem: One compromised computer can become the starting point for a much larger network attack.
- Build: A digital network twin that simulates attack propagation and predicts which machines are likely to be compromised next.
- WOW demo: Attack one node. Watch the infection spread across a 3D network, while your AI predicts the next vulnerable nodes and isolates them.
- Engineering: Graph neural networks, temporal prediction, network simulation.
- Colab: Excellent.
- Research angle: Predict attack propagation from incomplete network observations.

03. PHANTOMCODE — Find the Hidden Exploit in AI-Generated Code
- Problem: AI-generated code can contain security vulnerabilities that aren't obvious from reading it.
- Build: An automated code-testing environment that executes generated code in a sandbox, finds dangerous behaviour and attempts a patch.
- WOW demo: Generate a seemingly harmless program. The system discovers that an input can expose private data, demonstrates the vulnerability safely, then tests a repair.
- Engineering: Static analysis, sandboxing, fuzzing, symbolic execution.
- Colab: Good.
- Research angle: Detect vulnerabilities that static scanners miss. 
  ScienceDirect+
04. TRUTHMINE — An AI That Cross-Examines Other AIs
- Problem: Language models can confidently generate false information, and even hallucination evaluation methods have weaknesses.
- Build: Break an AI response into individual claims, construct a knowledge graph, find contradictions and calculate evidence-based confidence.
- WOW demo: One AI confidently answers a complex question. Another maps its claims, finds the contradiction and highlights the exact unsupported statements.
- Engineering: Knowledge graphs, information retrieval, uncertainty estimation, NLP.
- Colab: Excellent.
- Research angle: Detect subtle contradictions that sentence-level fact checking misses. 
  AAAI Open Research Archive+1
05. GHOSTDATA — Reconstructing Secrets from AI Models
- Problem: A model can unintentionally reveal information about its training data.
- Build: A controlled privacy laboratory that trains models on synthetic private datasets and tests membership inference and model inversion attacks.
- WOW demo: Give the system access only to a trained model. Watch it estimate whether a synthetic individual was in the training data, or attempt to reconstruct a training example.
- Engineering: Shadow models, embeddings, membership inference, privacy attacks.
- Colab: Good.
- Research angle: How much private information can be extracted under different privacy protections?

Category 2 — Planetary-scale engineering
These have excellent visual potential because they can be demonstrated using simulations and real scientific datasets.

06. ORBITAL — The Space Debris Intelligence System
- Problem: Satellites and debris can have dangerous close approaches. Orbital predictions involve uncertainty.
- Build: Simulate orbital trajectories, calculate collision probabilities and recommend avoidance manoeuvres.
- WOW demo: Show thousands of moving orbital objects. One collision risk appears; the system calculates possible escape manoeuvres and their consequences.
- Engineering: Orbital mechanics, numerical integration, Monte Carlo simulation, optimisation.
- Colab: Excellent.
- Research angle: Make collision risk estimates more interpretable under uncertain tracking data.
  
  NASA has investigated ML-assisted conjunction assessment and its computational challenges. 
  NASA Technical Reports Server (NTRS)+1

07. PYRO — Predict the Next Move of a Wildfire
- Problem: Fire spread depends on wind, terrain, vegetation and weather, making response decisions difficult.
- Build: A cellular fire-spread simulation with AI-based parameter estimation and uncertainty maps.
- WOW demo: Start a simulated fire on a satellite map. Change wind direction and humidity; watch the predicted fire front change in real time.
- Engineering: Cellular automata, geospatial data, simulation, probabilistic forecasting.
- Colab: Excellent.
- Research angle: Identify where predictions are unreliable and where additional observations matter most.
  
  Satellite detection has real resolution, cloud and revisit limitations. 
  files.gao.gov+1

08. FLOODNET — Predict the Street That Floods Next
- Problem: City-scale flash flooding can develop rapidly and forecasts carry uncertainty.
- Build: A simplified urban drainage digital twin using rainfall, terrain elevation and drainage capacity.
- WOW demo: Increase rainfall intensity. Watch water flow through a 3D city grid and see which roads become inaccessible.
- Engineering: Hydrological modelling, graph networks, GIS, uncertainty-aware ML.
- Colab: Good.
- Research angle: Predict flood propagation when drainage information is incomplete.
  
  Uncertainty-aware flood forecasting is an active research area. 
  Wiley Online Library
09. BLACKOUT — Stop a Power Grid Collapse
- Problem: A fault in one part of a power network can trigger cascading failures.
- Build: Simulate a power grid, introduce faults and train a model to identify dangerous propagation paths.
- WOW demo: Trigger one substation failure. Watch the grid turn red as failures propagate. Your system identifies the intervention that could prevent the cascade.
- Engineering: Graph neural networks, power-flow simulation, reinforcement learning.
- Colab: Good.
- Research angle: Find minimal interventions that prevent large-scale cascading failures. 
  ScienceDirect+1
10. SEISMOS — A Real-Time Seismic Intelligence Engine
- Problem: Detecting earthquakes quickly and distinguishing seismic events from noise is challenging.
- Build: Analyse seismic waveforms, identify P-wave arrivals and estimate event characteristics.
- WOW demo: Feed a seismic recording into the system. Show the waveform, detect the first arriving wave and animate estimated wave propagation.
- Engineering: Signal processing, time-series ML, wave detection.
- Colab: Excellent.
- Research angle: Improve detection under noisy, incomplete sensor data.
- Important: This is earthquake detection and early warning research, not reliable prediction of earthquakes before they happen.



Category 3 — Biomedical and scientific discovery
These are more research-heavy. A simulated discovery is not a clinically or experimentally validated discovery.
11. PROTEUS — Discover Dangerous Protein Mutations
- Problem: Some genetic mutations alter protein function, but interpreting their effects is difficult.
- Build: A model that compares protein sequences, estimates structural changes and ranks potentially damaging mutations.
- WOW demo: Change one amino acid. Watch a molecular structure visualisation update and see how the predicted properties change.
- Engineering: Protein embeddings, sequence modelling, structural bioinformatics.
- Colab: Good.
- Research angle: Identify mutations where different prediction methods strongly disagree.
12. RESIST-X — Predict the Evolution of Antibiotic Resistance
- Problem: Antibiotic resistance threatens the effectiveness of existing treatments.
- Build: Analyse publicly available bacterial genomic data and model associations between genetic variations and resistance.
- WOW demo: Introduce genetic mutations into a simulated bacterial population and visualise how resistance-associated variants change over generations.
- Engineering: Genomics, evolutionary modelling, classification, explainable ML.
- Colab: Good.
- Research angle: Investigate whether combinations of mutations provide better resistance predictions than individual mutations.
- Caution: Prediction is not laboratory confirmation or a treatment recommendation.
13. MEDSCOPE — Detect When Medical AI Should Refuse to Diagnose
- Problem: A medical AI can receive an image from a patient or scanner type it was never trained on, yet still output a confident prediction.
- Build: A model that detects out-of-distribution medical images and estimates whether its prediction should be trusted.
- WOW demo: Show a familiar medical scan, then an unusual or corrupted scan. The model identifies the second as outside its reliable operating conditions.
- Engineering: Uncertainty estimation, anomaly detection, distribution shift.
- Colab: Excellent.
- Research angle: Determine whether uncertainty estimates can reliably identify cases where the model makes mistakes. 
  PubMed+1
14. MICROSCOUT — Hunt Microplastics in Water
- Problem: Identifying and quantifying microplastics can require laborious analysis and specialised techniques.
- Build: Computer vision that detects, segments and counts suspected plastic particles in microscope images.
- WOW demo: Upload a microscope image and watch the system identify suspected particles, count them and create a contamination map.
- Engineering: Image segmentation, object detection, morphology, computer vision.
- Colab: Excellent.
- Research angle: Distinguish plastic-like particles from natural debris under different imaging conditions.
- Caution: Ordinary images cannot reliably establish the chemical identity of a particle. 
  ScienceDirect
15. MOLECULE-X — Search for Potential Drug Candidates
- Problem: Exploring chemical space for useful molecules is computationally demanding.
- Build: A molecular property prediction and candidate-ranking system using public datasets and existing pretrained models.
- WOW demo: Set target properties, generate or search candidate molecules, then visualise their structures and rank them.
- Engineering: Molecular fingerprints, graph neural networks, cheminformatics, optimisation.
- Colab: Good.
- Research angle: Find candidates with multiple desired properties rather than optimising one metric.
- Caution: A high model score does not establish that a molecule is safe or effective.
Category 4 — Infrastructure, climate and the physical world
16. THERMAL-X — See a Battery Fire Before It Happens
- Problem: Lithium-ion battery thermal runaway can escalate rapidly, and single-signal monitoring can miss early warning signs.
- Build: Fuse simulated or public battery temperature, voltage and current signals to detect abnormal patterns.
- WOW demo: Display a battery pack heatmap. Introduce a developing fault and show the system identify the abnormal cell before the simulated thermal runaway.
- Engineering: Time-series anomaly detection, sensor fusion, temporal models.
- Colab: Excellent for a data-driven prototype.
- Research angle: Investigate whether multi-signal fusion detects dangerous behaviour earlier than single-sensor thresholds. 
  ScienceDirect+1
17. HYDRA — Hear Water Leaks Before They Become Disasters
- Problem: Water lost through distribution leaks contributes to scarcity and infrastructure damage.
- Build: Analyse acoustic signals and identify leak-like patterns, potentially localising them using multiple simulated sensors.
- WOW demo: Play different pipe recordings. Show the leak signature on a frequency spectrogram and estimate the leak's position along a simulated pipe.
- Engineering: Digital signal processing, spectrograms, CNNs, localisation.
- Colab: Excellent.
- Research angle: Distinguish leaks from pumps, traffic and other background noise. 
  IWA Publishing+1
18. TERRASHIELD — Predict Slope Failure Before It Happens
- Problem: Rainfall and changing soil conditions can trigger landslides.
- Build: Model soil moisture, rainfall, terrain and slope stability to estimate changing risk.
- WOW demo: Increase simulated rainfall. Show underground moisture propagation, slope stress indicators and a developing risk zone.
- Engineering: Time-series forecasting, geospatial analysis, physical modelling.
- Colab: Good.
- Research angle: Test whether soil moisture improves rainfall-only warning systems. 
  Springer Nature Link+1
19. SPECTRA — Detect Crop Disease Before Visible Symptoms
- Problem: Some crop diseases can develop before obvious visual symptoms appear.
- Build: Analyse spectral or multispectral plant data and identify patterns associated with disease.
- WOW demo: Show healthy-looking and affected spectral samples. The system highlights subtle spectral differences and tracks a simulated progression.
- Engineering: Spectral analysis, dimensionality reduction, classification.
- Colab: Good, if suitable spectral datasets are available.
- Research angle: Can low-cost RGB images or limited spectral bands approximate some of the information from more expensive hyperspectral instruments?
  
  A 2025 wheat study reported disease detection seven days before visible symptoms using hyperspectral measurements. 
  ScienceDirect

20. SWARM — Design an Evacuation System That Thinks Like a City
- Problem: During disasters, conventional shortest-path evacuation can overload exits, roads and narrow corridors.
- Build: A multi-agent simulation in which thousands of virtual people move through a city while an optimisation system dynamically assigns routes.
- WOW demo: Trigger a disaster. Watch a city population evacuate, see bottlenecks appear, and compare ordinary shortest-path routing with adaptive crowd-aware routing.
- Engineering: Multi-agent systems, graph theory, reinforcement learning, optimisation.
- Colab: Excellent.
- Research angle: Find routes that minimise total evacuation time while reducing dangerous crowd density.
roject: GHOSTTRACE
AI MODEL FORENSICS · ADVERSARIAL MACHINE LEARNING · NEURAL SECURITY
Find the hidden weapon inside an AI model.

1. The real-world problem
Imagine a hospital downloads an AI model to detect cancer from medical scans.

The model appears perfect during testing:
- It identifies normal scans correctly.
- It identifies cancer correctly.
- It passes its accuracy benchmarks.
But someone secretly modified its training process.

A tiny hidden pattern has been implanted into the model. Whenever that pattern appears, the model deliberately produces a wrong prediction.

The model is effectively carrying a hidden instruction.

This is called an AI backdoor attack.

And it is not science fiction. Research has demonstrated attacks against pretrained models, including attacks that can compromise models used downstream by other developers. 
DOI+2


The terrifying part: the model can behave normally until the trigger appears.
2. What GHOSTTRACE does
GHOSTTRACE is a neural-network forensic scanner.

You give it an AI model. It tries to determine whether the model contains a hidden backdoor.

But here's the ambitious part:

Instead of simply saying "this model is suspicious", it attempts to reconstruct the hidden trigger.

The system would:
1. Load an AI model.
2. Test its normal behaviour.
3. Search for unusual input patterns that consistently manipulate its predictions.
4. Reconstruct a possible trigger.
5. Show which output class it hijacks.
6. Test whether removing or neutralising the trigger restores normal behaviour.
This is model reverse engineering.

It is much closer to a research experiment than a typical student AI application.
3. The demonstration that could make judges stop
Imagine this on a large screen.
GHOSTTRACE // FORENSIC LAB
SYSTEM ONLINE

MODEL: VISION-NET-07 · SCAN MODE: BLACK BOX

NEURAL INTEGRITY SCAN
Model behaviour
NORMAL

CLEAN INPUT ACCURACY

94.2%

BACKDOOR SIGNATURE FOUND
A small pattern causes abnormal classification behaviour.

Illustrative interface. These values are mock data, not actual experimental results.

Then you do the reveal:
- Show an ordinary image.
- The model correctly identifies it.
- Add the hidden trigger.
- The model suddenly predicts the attacker's target class.
- Run GHOSTTRACE.
- It searches for the trigger and reconstructs a visual approximation.
- Remove the trigger and test again.
That is the wow moment.

The judges don't just see an AI making a prediction. They see another AI investigating how that AI was compromised.
4. The engineering underneath
This is where the project becomes challenging.
Layer	Engineering challenge
Attack laboratory	Train a model with a deliberately implanted backdoor
Behavioural analysis	Measure clean and triggered predictions
Trigger reconstruction	Optimise an input pattern to produce a target classification
Anomaly detection	Identify unusually easy-to-trigger output classes
Mitigation	Experiment with fine-tuning or unlearning
Validation	Measure accuracy before and after mitigation

There is genuine research behind this direction.
- Neural Cleanse pioneered reverse-engineering hidden triggers in neural networks. 
  Neural Cleanse
- DeBackdoor (USENIX Security 2025) investigates detection under limited-data conditions, including scenarios where a developer has received an untrusted model from a third party. 
  USENIX
- BaDExpert (ICLR 2024) explores extracting backdoor functionality to detect malicious inputs. 
  ICLR Proceedings
This means we should not pretend that backdoor detection itself is a new invention.

Our research challenge should be to build a practical, understandable forensic pipeline that combines trigger discovery, behavioural testing and mitigation, and evaluate how well it works under restricted information.
5. Can we build it with Google Colab?
Yes — with a carefully limited experiment
Proposed stack
PyTorch — train and inspect neural networks

CIFAR-10 / MNIST — test datasets

NumPy + OpenCV — trigger and image analysis

Matplotlib / Plotly — forensic visualisations

Gradio — interactive interface

Google Colab GPU — model training and experiments


No physical hardware. No paid APIs. No need to train a giant language model.

One limitation: our first prototype should focus on image-classification models. Scanning arbitrary LLMs, huge models, or every possible backdoor type would be unrealistic.
6. The part that could make this genuinely impressive
I would set three research milestones:
1. Milestone 1 — The Ghost
   
   Implant a secret trigger into a model. Prove that it behaves normally on clean inputs but fails when the trigger appears.
2. Milestone 2 — The Autopsy
   
   Give the scanner the infected model without revealing the trigger. Attempt to reconstruct it using optimisation and behavioural observations.
3. Milestone 3 — The Cure
   
   Attempt to remove the backdoor while preserving clean accuracy. Compare attack success rate and normal accuracy before and after.
The third milestone matters. Finding a vulnerability is good. Demonstrating that you can reduce it without destroying the model is much stronger.
