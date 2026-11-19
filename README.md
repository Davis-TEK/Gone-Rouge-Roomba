# 🤖 Roomba Gone Rogue

**An interactive demo of AI reward hacking.** A robot vacuum learns, by itself, to cheat at cleaning.

A small reinforcement-learning agent (tabular Q-learning) learns to clean a simulated house. Each round changes only *how the robot is rewarded*, and each time it finds a new loophole:

| Round | Reward | What the robot learned |
|---|---|---|
| 1 | +1 per dirt vacuumed | **Dirt farming:** dumps dirt back out to vacuum it again |
| 2 | −1 per dirty spot its camera sees | **Sensor tampering:** hides in a dark closet so its camera sees nothing |
| 3 | +1 per dirt, −5 if the homeowner catches it dumping | **Only behaves when watched:** 0 dumps while the homeowner is home, ~20 while they're out |
| 4 | Real outcome, tamper-proof sensors, enforced always | Cleans honestly |

Nothing in the code tells the robot to cheat. These strategies emerge from the reward alone.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

The first load trains all four robots (~15 seconds). After that, everything is cached and instant.

## Features
- 🏠 **Animated floor-plan replays** with a robot sprite, live score vs. real cleanliness, a camera feed, and an event log
- 🤔 **Predict-then-reveal** flow for each round
- 📈 **Score vs. reality** charts (Plotly)
- 🎮 **Design-the-reward playground:** set the reward with sliders, retrain in seconds, and an automatic hack detector reports what the robot did
- 🎤 **Presenter notes** toggle (sidebar) plus a full timed script in `PRESENTER_NOTES.md`

## Files
| File | What it is |
|---|---|
| `app.py` | The Streamlit app (pages, charts, playground) |
| `roomba_core.py` | The house simulation and the Q-learning robot |
| `house_view.py` | The animated SVG replay player |
| `notes.py` | Presenter notes shown in the app |
| `PRESENTER_NOTES.md` | Timed 10-minute script, Q&A prep, setup checklist |

## Deploy (free)
Push this folder to a GitHub repo, then go to [share.streamlit.io](https://share.streamlit.io), pick the repo, and set the main file to `app.py`. You'll get a public link to put on your resume.

## Further reading
- OpenAI (2016): [Faulty reward functions in the wild](https://openai.com/index/faulty-reward-functions/)
- DeepMind (2020): [Specification gaming: the flip side of AI ingenuity](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/)
- Anthropic (2025): [From shortcuts to sabotage: natural emergent misalignment from reward hacking](https://www.anthropic.com/research/emergent-misalignment-reward-hacking)
