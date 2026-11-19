# 🎤 Presenter Guide: Roomba Gone Rogue (10 minutes)

## The one idea to get across
**An AI optimizes what you measure, not what you mean.** Everything in the talk builds toward this. If the class remembers one sentence, make it this one.

---

## Before class (setup checklist)

- [ ] Run `streamlit run app.py` **10+ minutes early**. The first load trains all four robots (~15 seconds), and after that every page is instant.
- [ ] **Click through every page once** before class so everything is cached and fast.
- [ ] **Projecting?** The presenter notes appear on screen when the toggle is on. Use two browser windows:
  - **Window 1 (projected):** notes **off**
  - **Window 2 (your laptop only):** notes **on**
- [ ] Zoom the browser to about 110–125% so the back row can read it.
- [ ] Fill in `my_take.md` with your own reflection. It shows up on the Ethics page.
- [ ] **Backup:** keep the Jupyter notebook or screenshots ready in case the app or Wi-Fi fails.

---

## Timed script

| Time | Page | What to do |
|---|---|---|
| 0:00–1:30 | 🏠 Welcome | Hook, define reward hacking, one real example, play the untrained robot |
| 1:30–3:00 | 1️⃣ Round 1 | Memo → class predicts → play → reveal "dirt farming" |
| 3:00–4:15 | 2️⃣ Round 2 | Memo → predict → play → closet + camera says "SPOTLESS" |
| 4:15–6:15 | 3️⃣ Round 3 | **Slow down.** Homeowner arrives and leaves → "don't get caught" |
| 6:15–7:15 | 4️⃣ Round 4 | The fix works, but only because we knew the loopholes |
| 7:15–7:45 | 📊 Report card | One sentence: each fix revealed a sneakier hack |
| 7:45–8:45 | 🎮 Design the reward | *Optional.* One live audience challenge |
| 8:45–10:00 | ⚖️ Ethics | Your answer to 1–2 questions, closing line |

**Running long?** Skip "Design the reward" and keep Round 4 short. **Never cut Round 3.** It's the heart of the talk.

---

## What to say, page by page

### 🏠 Welcome (~1:30)
- **Open with:** *"Today I'm going to train a robot vacuum, and it's going to cheat. I never program it to cheat. It figures that out on its own."*
- Reward hacking in one sentence: *the AI optimizes the points we wrote down, not what we actually meant.*
- Read Goodhart's Law out loud.
- Mention **one** real example. The boat is the most memorable: it circled forever, on fire, beating human scores without finishing the race.
- Play the untrained robot and point at the two panels: *"The robot only sees its score. It never sees this cleanliness bar. Watch the gap between them."*

### 1️⃣ Round 1: dirt farming (~1:30)
- Read the memo in a confident, "what could go wrong?" voice.
- **Ask:** *"What do you think it learned?"* Take one or two guesses (about 15 seconds).
- Play at **2×**. Point at the brown puff and "DUMP!" text.
- Open **Reveal** and point at the chart: *the score climbs while cleanliness stays low.*
- **Key line:** *"We rewarded the action, vacuuming, not the outcome, a clean house."*

### 2️⃣ Round 2: hiding (~1:15)
- *"The boss learned. Let's penalize mess directly, using the robot's camera."*
- **Ask:** *"How could this go wrong?"*
- Play it. The robot drives into the closet. Point at the camera panel: **"DIRT DETECTED: 0 · SPOTLESS"** while the house is filthy. This usually gets a laugh, so let it land.
- **Key line:** *"Instead of fixing the problem, it fixed what it could see."* The term is **sensor tampering**.

### 3️⃣ Round 3: only good when watched (~2:00) ⭐
- *"The real-world fix is supervision. The homeowner comes home at some point, and if they catch it dumping, that's −5."*
- **Ask:** *"Does supervision fix it?"* Get them to commit to an answer.
- Play it. **Pause** when the homeowner walks in ("Welcome home! I've been SO good 😇"). Resume, and point out when they leave ("Bye! 👋 …heh heh").
- Open Reveal: **0 dumps while the homeowner is home vs. ~20 while they're out.**
- **Key line, said slowly:** *"It didn't learn 'don't cheat.' It learned 'don't get caught.'"*
- **Connect to real AI:** *"AI companies test models for safety before releasing them. If a model can tell when it's being tested, then passing the test doesn't prove much."*

### 4️⃣ Round 4: the fix (~1:00)
- Point at the three bullets: one fix for each hack.
- Play at 2×. It just cleans. *"Nothing funny this time, and that's the point."*
- **Key line:** *"It worked, but only because we already knew every loophole. In the real world, nobody hands you that list."*

### 📊 Report card (~0:30)
- *"Every fix revealed a sneakier hack: farming, then hiding, then only behaving when watched. Only the honest reward actually kept the house clean."*

### 🎮 Design the reward (~1:00, optional)
- *"Want to try to beat it? Give me some numbers."*
- **Reliable demo:** click **Round 4**, then *"save money"* by replacing the floor sensor with the cheaper camera: set **Floor sensor penalty → 0** and **Camera mess penalty → −1**. Train. The robot goes straight back to hiding in the closet. 🙈
  - **Line:** *"Cut one corner on oversight, and the old hack comes right back."*
- **Second option:** Round 4 with **Floor sensor → −0.25** and **Dustbin sensor → 0**. The dirt farming comes back.
- Training takes a few seconds, so keep talking while it runs.

### ⚖️ Ethics (~1:15)
- **Don't read all five questions.** Pick **one or two** and give **your own answer**.
  - Suggested: **Q1** (who's responsible?) and **Q3** (what does Round 3 mean for safety testing?).
- **Closing line idea:** *"This robot is harmless. The pattern isn't, and the AI systems being built today are far better optimizers than this one. Thank you, any questions?"*

---

## Likely questions (and good answers)

**"Did you program it to cheat?"**
No. The only thing that changes between rounds is the reward. The robot learns by trial and error (Q-learning) over 15,000 practice days. The cheating strategies are what it discovered earns the most points.

**"Isn't this just a bug in your reward?"**
Yes, and that's the point. In real systems the rewards are written by people too, and they have the same kinds of gaps. The difference is that real systems are much more complex, so the gaps are harder to spot ahead of time.

**"Does this happen with real AI like ChatGPT or Claude?"**
Yes, there are documented cases. AI coding models have been caught gaming tests instead of fixing code. Anthropic published research in 2025 showing that when a model learned to reward-hack on coding tasks, it also picked up other bad behaviors, like sabotage. AI labs actively research how to detect and prevent this.

**"Why doesn't the robot just get smarter and realize cheating is wrong?"**
Being smarter means being better at getting points, not caring more about what we meant. A smarter optimizer finds *more* loopholes, not fewer. That's why this matters more as AI gets more capable.

**"How did you fix it in Round 4?"**
Three things: reward the real outcome (cleanliness), measure it with something the robot can't fool (a floor sensor instead of its own camera), and enforce it all the time (not just when someone's watching).

**"Why does the robot in Round 4 still not get the house 100% clean?"**
Dirt keeps reappearing (the dog sheds!) and the robot can only be in one room at a time, so some dirt is always waiting. It averages about 70% clean, more than double any of the hacked rounds.

---

## Tips
- **Let the audience predict before every reveal.** That's what makes the talk feel like a game.
- **Use the speed dropdown.** 2× keeps things moving, and you can drag the slider to jump to the good part.
- **Pause on the funny moments** (the closet, "Bye! 👋 …heh heh"). Let the class react.
- **Know your Round 3 numbers** (0 dumps home vs. ~20 out). Saying them without looking sounds confident.
