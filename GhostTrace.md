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
