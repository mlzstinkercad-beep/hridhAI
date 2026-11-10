2. The idea bank — grand, unsaturated

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
