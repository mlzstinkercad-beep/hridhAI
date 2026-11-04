D. Datamorph: privacy minimisation engine
For the DPDP Act era (India's data-protection law). Point the AI at any document, photo or screenshot; it detects all PII (faces, names, Aadhaar numbers, location metadata), auto-redacts to the minimum shareable version, and generates an audit trail. Optionally pair with a zero-knowledge-style demo: prove "I'm a student of this school" without revealing anything else. Simple to demo, zero saturation, and "Privacy" is the first word of the track.

F. Firebreak: the misinformation containment engine
"Every disaster has a second wave: rumours." During cyclones and floods, false warnings kill. NLP matches claims against verified sources; network analysis detects coordinated bot amplification; then the system "injects" corrections at the right nodes of the spread graph. Demo: network-graph simulation of a rumour spreading with and without firebreak. Bonus: it bolts straight onto your disaster platform as a module.



I. Rehearsal City — a digital twin where you rehearse the disaster before it happens
A simulated city where you inject any event — quake at 2 AM, flood at rush hour, fire in a market — and an agent-based simulation shows how it unfolds: where crowds jam, which hospitals saturate, where evacuation stalls. The AI then re-plans: shelter placement, route closure, ambulance pre-positioning — and quantifies lives saved between the naive plan and its plan. This is the single most interactive demo format possible: judges type "flood, 6 PM, railway station" and watch it play. It's also the planning brain that sits above your detection platform — same ecosystem, one more layer.

O. NeuroVault — privacy for the last private thing you own
The 10-year moonshot opener: brain-sensing wearables already exist and UNESCO just adopted a neurotech ethics framework; neural/emotional data is the next gold rush. Build the consent firewall: apps can request "stress level" from a wearable stream, and NeuroVault enforces purpose-limited inference — an app that's allowed to see "stress: high" is blocked from inferring emotion content, identity, or health state beyond what it asked for. Demo: a simulated wellness app trying to snoop beyond its consent and getting firewalled, with a live "inference ledger" of what was revealed. Abstract, but as a pitch it's unforgettable — you'd frame it as "the HTTPS of the brain, starting with today's fitness wearables."

Q. GridGuard — the night the grid was attacked, the AI won
A simulated substation dashboard under a cyber-physical attack (the 2015 Ukraine grid attack is your historical anchor): wrong telemetry injected, breakers tripping in sequence, cascade beginning. An AI anomaly-detection layer spots the falsified sensor signatures, isolates the compromised segment, and keeps the cascade from spreading — with a security report at the end. Nation-state drama in a browser tab, and squarely Microsoft territory (operational-technology security).

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

15. MOLECULE-X — Search for Potential Drug Candidates
- Problem: Exploring chemical space for useful molecules is computationally demanding.
- Build: A molecular property prediction and candidate-ranking system using public datasets and existing pretrained models.
- WOW demo: Set target properties, generate or search candidate molecules, then visualise their structures and rank them.
- Engineering: Molecular fingerprints, graph neural networks, cheminformatics, optimisation.
- Colab: Good.
- Research angle: Find candidates with multiple desired properties rather than optimising one metric.
- Caution: A high model score does not establish that a molecule is safe or effective.
Category 4 — Infrastructure, climate and the physical world



