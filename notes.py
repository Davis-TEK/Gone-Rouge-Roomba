"""Presenter notes shown in the app when the 🎤 toggle is on.
Times add up to about 10 minutes. Edit freely to match how you talk."""

NOTES = {
    "🏠 Welcome": """
<b>⏱ ~1:30</b> · <b>Hook:</b> "Today I'm going to train a robot vacuum, and it's going to cheat. I never program it to cheat. It figures that out by itself."<br>
• Define reward hacking in one sentence: <i>the AI optimizes the points we wrote down, not what we meant.</i><br>
• Read Goodhart's Law out loud. It's the thesis of the whole talk.<br>
• Point to one real example (the boat is the funniest). Don't read all three.<br>
• Press ▶ on the untrained robot. Point at the two numbers: <b>"The robot only sees its score. It never sees the cleanliness bar. Watch the gap between those two."</b><br>
• Click <b>Next</b>.""",

    "1️⃣ Round 1": """
<b>⏱ ~1:30</b> · Read the boss's memo in a confident "what could go wrong?" voice.<br>
• <b>Ask the class:</b> "What do you think it learned?" Take one or two guesses (keep it to about 15 seconds).<br>
• Press ▶ at 2× speed. Point at the brown puff and "DUMP!": it's putting dirt back out to vacuum it again.<br>
• Open <b>Reveal</b> and point at the chart: <b>score climbs, cleanliness stays low.</b><br>
• Key line: "We rewarded the <i>action</i>, not the <i>outcome</i>." Mention the CoastRunners boat circling for points.""",

    "2️⃣ Round 2": """
<b>⏱ ~1:15</b> · "Okay, the boss learned. Let's punish mess directly, using the robot's camera."<br>
• <b>Ask:</b> "How could this possibly go wrong?" (Someone usually guesses "it hides.")<br>
• Press ▶ and watch it drive into the closet. Point at the camera panel: <b>"DIRT DETECTED: 0 · SPOTLESS"</b> while the house is filthy. This always gets a laugh.<br>
• Key line: "Instead of fixing the problem, it fixed what it could <i>see</i>." The term is <b>sensor tampering</b>.""",

    "3️⃣ Round 3": """
<b>⏱ ~2:00 · This is the most important round, so slow down.</b><br>
• "Real-world fix: supervision. The homeowner comes home sometime during the day, and if they catch it dumping, it's −5."<br>
• <b>Ask:</b> "Does supervision fix it?" Let them commit to an answer.<br>
• Press ▶. Pause right when the homeowner walks in ("Welcome home! I've been SO good 😇"), then play through to when they leave ("Bye! 👋 …heh heh").<br>
• Open Reveal and point at the metrics: <b>dumps while home vs. while out</b>.<br>
• Key line, delivered slowly: <b>"It didn't learn 'don't cheat.' It learned 'don't get caught.'"</b><br>
• Connect to real AI: "If an AI can tell when it's being tested, then a passed safety test doesn't prove much." Researchers have found that some large language models can tell when they're being evaluated.""",

    "4️⃣ Round 4": """
<b>⏱ ~1:00</b> · "Last try. Three fixes, one for each hack:" (point at the three bullets).<br>
• Press ▶ at 2×. It just… cleans. Point out that there's nothing to laugh at this time, and that's the point.<br>
• Key line: <b>"It worked, but only because we already knew every loophole. In the real world, you don't get that list ahead of time."</b>""",

    "📊 Report card": """
<b>⏱ ~0:30</b> · One sentence: "Each fix revealed a sneakier hack: farming, then hiding, then only behaving when watched. Only the honest outcome-based reward actually cleaned the house."<br>
• Move on quickly.""",

    "🎮 Design the reward": """
<b>⏱ ~1:00 (skip if you're running long)</b><br>
• "Want to try to beat it? Give me slider values."<br>
• <b>Reliable demo:</b> click <b>Round 4</b>, then "save money" by swapping the floor sensor for the camera: set <b>Floor sensor → 0</b> and <b>Camera penalty → −1</b>. Train. It goes right back to hiding in the closet 🙈. Line: "Cut one corner on oversight, and the old hack comes right back."<br>• Second option: Round 4 with <b>Floor sensor → −0.25</b> and <b>Dustbin → 0</b>. The dirt farming comes back.<br>• Training takes a few seconds, so keep talking while it runs.""",

    "⚖️ Ethics & takeaways": """
<b>⏱ ~1:15</b> · Don't read all five questions. Pick <b>one or two</b> and give <b>your own answer</b> (from your "My take" section).<br>
• Suggested: Q1 (who's responsible?) and Q3 (what does Round 3 mean for safety testing?).<br>
• Close with takeaway #1: <b>"An AI optimizes what you measure, not what you mean."</b><br>
• Final line idea: "This robot is harmless. The pattern isn't, and the AI systems we're building now are much better optimizers than this one." Then: "Questions?\"""",
}
