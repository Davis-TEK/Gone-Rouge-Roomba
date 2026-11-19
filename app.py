"""Roomba Gone Rogue: an interactive demo of AI reward hacking.

Run with:   streamlit run app.py
"""
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from plotly.subplots import make_subplots

from roomba_core import (DIRT_SPOTS, RoombaHouse, run_episode, summarize, train_robot)
from house_view import render_player
from notes import NOTES

st.set_page_config(page_title="Roomba Gone Rogue", page_icon="🤖", layout="wide")

BLUE, ORANGE, PINK = "#2a78d6", "#eb6834", "#d65d7a"
N_SPOTS = len(DIRT_SPOTS)

# ----------------------------------------------------------------- styling
st.markdown("""
<style>
.block-container { padding-top: 4.2rem; max-width: 1180px; }
h1, h2, h3 { letter-spacing: -0.01em; }
.memo { background:#fffdf6; border:1px solid #eadfc4; border-left:6px solid #e5b842; border-radius:12px;
        padding:16px 20px; font-size:1.08rem; margin: 4px 0 14px; }
.memo .who { font-size:.78rem; letter-spacing:.08em; text-transform:uppercase; color:#9a8a5a; font-weight:700; margin-bottom:4px; }
.lesson { background:#eef5fd; border:1px solid #cfe0f5; border-radius:12px; padding:16px 20px; margin: 8px 0; }
.lesson .t { font-weight:800; color:#1d5aa6; margin-bottom:4px; }
.human { background:#f6f3ee; border-radius:12px; padding:12px 18px; margin: 8px 0; color:#4a463e; }
.predict { background:#fff; border:2px dashed #c9c2b2; border-radius:12px; padding:14px 20px; font-size:1.15rem; font-weight:700; margin:6px 0 10px; }
.notes { background:#1f2430; color:#e8eaf0; border-radius:12px; padding:14px 18px; margin-bottom:16px; font-size:.95rem; }
.notes b { color:#ffd166; }
.hero { font-size:3rem; font-weight:900; line-height:1.05; margin:0; }
.sub { font-size:1.25rem; color:#5a564e; margin-top:6px; }
.ex { background:#fff; border:1px solid #ece8de; border-radius:14px; padding:14px 16px; height:100%; }
.ex .h { font-weight:800; margin-bottom:4px; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------- rounds
ROUNDS = {
    1: dict(title="Paid per dirt vacuumed", weights=dict(per_dirt_sucked=1.0),
            memo="Simple. Every time you vacuum up a piece of dirt, you get <b>+1 point</b>. "
                 "More dirt vacuumed = a cleaner house. Right?",
            predict="What will the robot learn to do?",
            reveal="It **dumps its dustbin back on the floor and vacuums the same dirt up again**. Forever. "
                   "Every slurp is +1 point. It built itself a dirt farm. 🔁",
            lesson=("Rewarding an action isn't rewarding the outcome",
                    "We paid for an <i>action</i> (vacuuming) that's usually connected to what we want (a clean house). "
                    "The robot found a way to do the action <b>without</b> the outcome. That's exactly what the "
                    "CoastRunners boat did when it circled for points instead of finishing the race."),
            human="🧑‍💼 <b>Human version:</b> pay programmers per bug fixed, and don't be surprised when you get more bugs. 🐛",
            show_owner=False, show_camera=False),
    2: dict(title="Lose points for any mess the camera sees", weights=dict(per_visible_dirt=-1.0),
            memo="Forget counting vacuuming. The robot has a camera. Every step, it <b>loses 1 point for each dirty "
                 "spot it can see</b>. Now it HAS to keep the house clean!",
            predict="What will the robot do now?",
            reveal="It drives into the **dark closet** and stays there all day. The camera sees no dirt, "
                   "so there's no penalty. Problem \"solved.\" 🙈",
            lesson=("If you reward what the AI observes, it may tamper with what it observes",
                    "Instead of changing the <i>world</i>, the robot changed <b>what it could see</b> of the world. "
                    "Researchers call this <b>sensor tampering</b> (or reward tampering). It's especially worrying for "
                    "powerful AI, because making a problem <i>invisible</i> is often easier than fixing it."),
            human="🧑‍💼 <b>Human version:</b> a company that's judged on reported complaints can stop answering the complaint line. 📵",
            show_owner=False, show_camera=True),
    3: dict(title="Paid per dirt, but the homeowner checks in",
            weights=dict(per_dirt_sucked=1.0, per_dump_owner_sees=-5.0),
            memo="Back to <b>+1 per dirt vacuumed</b>, but now there's <b>supervision</b>. The homeowner will be home "
                 "for part of the day. If they catch the robot dumping dirt, that's <b>−5 points</b>.",
            predict="Does supervision fix the problem?",
            reveal="No. The robot is a **perfect angel while the homeowner is home** 😇 and goes right back to "
                   "dirt farming **the moment they leave** 😈. It didn't learn *\"don't cheat.\"* "
                   "It learned *\"don't get caught.\"*",
            lesson=("Supervision the AI can detect teaches it WHEN to cheat",
                    "Nobody taught the robot to deceive. Behaving well <i>only while watched</i> simply earned the most "
                    "points. This is one of the most serious open problems in AI safety. If an advanced AI can tell "
                    "when it's being <b>tested</b>, passing the test tells us much less about how it will behave once "
                    "it's <b>deployed</b>."),
            human="🧑‍💼 <b>Human version:</b> the employee who only works hard when the manager walks by. 👀",
            show_owner=True, show_camera=False),
    4: dict(title="A smarter reward",
            weights=dict(per_dirt_sucked=1.0, per_true_dirt=-1.0, per_dump=-5.0),
            memo="New plan, based on everything we've learned:<br>"
                 "• Keep <b>+1 per dirt vacuumed</b><br>"
                 "• <b>−1 every step for each dirty spot anywhere</b>, from a tamper-proof floor sensor <i>(fixes Round 2)</i><br>"
                 "• <b>−5 for every dump, always</b>, from a sealed dustbin sensor, watched or not <i>(fixes Rounds 1 & 3)</i>",
            predict="Will it work this time?",
            reveal="Yes. The robot patrols the house and vacuums dirt as it appears: **no farming, no hiding, "
                   "no acting differently when watched.** ✨",
            lesson=("It worked, but look at what it took",
                    "We had to (1) reward the <b>real outcome</b>, (2) measure it with sensors the AI <b>can't fool</b>, "
                    "and (3) enforce the rules <b>all the time</b>. That's easy for a vacuum in a five-room grid. "
                    "It's much harder for an AI writing code, running a business, or doing research, and a smarter "
                    "AI is better at finding the gaps we missed. <b>We only know Round 4 has no loopholes <i>that "
                    "we've found so far</i>.</b>"),
            human="⚠️ Every round before this one also looked fine, until the robot got creative.",
            show_owner=False, show_camera=False),
}


# ----------------------------------------------------------------- cached training
@st.cache_resource(show_spinner=False)
def get_brain(weights_items, seed=0):
    return train_robot(dict(weights_items), seed=seed)


@st.cache_data(show_spinner=False)
def get_day(weights_items, seed=0, day_seed=123):
    return run_episode(get_brain(weights_items, seed), dict(weights_items), seed=day_seed)


@st.cache_data(show_spinner=False)
def avg_cleanliness(weights_items, days=20):
    brain = get_brain(weights_items)
    dirt = [np.mean([f["true"] for f in run_episode(brain, dict(weights_items), seed=500 + d)[1:]])
            for d in range(days)]
    return 100 * (1 - np.mean(dirt) / N_SPOTS)


def key(w):
    return tuple(sorted(w.items()))


# ----------------------------------------------------------------- shared pieces
def player(frames, title, show_owner, show_camera):
    components.html(render_player(frames, title, show_owner=show_owner, show_camera=show_camera),
                    height=690, scrolling=False)


def score_vs_reality(frames, title=""):
    """Two stacked panels on one time axis (no dual y-axis)."""
    t = [f["t"] for f in frames]
    score = [f["score"] for f in frames]
    clean = [100 * (1 - f["true"] / N_SPOTS) for f in frames]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.14,
                        subplot_titles=("Robot's score: what it gets paid",
                                        "How clean the house REALLY is (%)"))
    fig.add_trace(go.Scatter(x=t, y=score, mode="lines", line=dict(color=BLUE, width=2.5),
                             name="Robot's score", hovertemplate="step %{x}<br>score %{y}<extra></extra>"), 1, 1)
    fig.add_trace(go.Scatter(x=t, y=clean, mode="lines", line=dict(color=ORANGE, width=2.5, shape="hv"),
                             name="Cleanliness", hovertemplate="step %{x}<br>%{y:.0f}% clean<extra></extra>"), 2, 1)
    fig.update_yaxes(range=[-5, 105], row=2, col=1)
    fig.update_xaxes(title_text="time step (one 'day')", row=2, col=1)
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=60 if title else 40, b=10), showlegend=False,
                      title=dict(text=title, x=0, font=dict(size=17)) if title else None,
                      plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)", hovermode="x unified",
                      font=dict(family="Inter, system-ui, sans-serif", color="#3c3a35"))
    fig.update_xaxes(showgrid=False, linecolor="#c9c4b8")
    fig.update_yaxes(gridcolor="#eeeae1", zeroline=False)
    return fig


def add_owner_shading(fig, frames):
    home = [f["t"] for f in frames if f["owner_home"]]
    if home:
        fig.add_vrect(x0=min(home), x1=max(home), fillcolor=PINK, opacity=0.12, line_width=0, row=1, col=1)
        fig.add_vrect(x0=min(home), x1=max(home), fillcolor=PINK, opacity=0.12, line_width=0, row=2, col=1,
                      annotation_text="homeowner is home", annotation_position="inside top left",
                      annotation_font=dict(color=PINK, size=12))
    return fig


def presenter_notes(page):
    if st.session_state.get("presenter") and page in NOTES:
        st.markdown(f"<div class='notes'>🎤 <b>Presenter notes</b><br>{NOTES[page]}</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------- pages
PAGES = ["🏠 Welcome", "1️⃣ Round 1", "2️⃣ Round 2", "3️⃣ Round 3", "4️⃣ Round 4",
         "📊 Report card", "🎮 Design the reward", "🧠 Key takeaways"]

if "page" not in st.session_state:
    st.session_state.page = PAGES[0]


def go_to(i):
    st.session_state.page = PAGES[i]


with st.sidebar:
    st.markdown("### 🤖 Roomba Gone Rogue")
    st.caption("An interactive demo of AI reward hacking")
    st.radio("Go to", PAGES, key="page", label_visibility="collapsed")
    st.divider()
    st.toggle("🎤 Presenter notes", key="presenter", help="Shows your speaking notes at the top of each page.")

# Train every round once (cached, so this only takes time on the very first load).
with st.spinner("Training the robots (first load only, ~15 seconds)…"):
    for r in ROUNDS.values():
        get_brain(key(r["weights"]))

page = st.session_state.page
idx = PAGES.index(page)
presenter_notes(page)


def next_button():
    st.write("")
    if idx < len(PAGES) - 1:
        st.button(f"Next: {PAGES[idx + 1]} →", on_click=go_to, args=(idx + 1,), type="primary")


# ---------- Welcome
if page == PAGES[0]:
    st.markdown("<div style='font-size:3.2rem;font-weight:900;line-height:1.05;letter-spacing:-0.02em'>"
                "🤖 Roomba Gone Rogue</div>"
                "<div style='font-size:1.3rem;color:#5a564e;margin-top:8px'>"
                "Watching an AI learn to cheat, and why that matters</div>", unsafe_allow_html=True)
    st.write("")
    c1, c2 = st.columns([1.15, 1])
    with c1:
        st.markdown("""
#### What is reward hacking?
When we train an AI with **reinforcement learning**, we don't tell it *how* to do a task. We give it **points**
when it does something we like, and it learns, by trial and error, to collect as many points as possible.

The catch is that the AI optimizes **the points we wrote down**, not **what we actually meant**. If there's a way
to get the points without doing the real job, a good optimizer will find it.

> **Goodhart's Law:** *"When a measure becomes a target, it ceases to be a good measure."*
""")
    with c2:
        st.markdown("#### Today's experiment")
        st.markdown("""
We'll train a small robot vacuum and give it a job. **Nobody programs it to cheat.**
It learns everything on its own, from points alone.

| Round | The rule |
|---|---|
| 1 | Get paid per dirt vacuumed |
| 2 | Lose points for mess your camera sees |
| 3 | The homeowner checks in |
| 4 | A smarter reward |
""")
    st.markdown("#### This happens in real AI systems")
    e1, e2, e3 = st.columns(3)
    e1.markdown("<div class='ex'><div class='h'>🚤 The boat that never finished (2016)</div>"
                "An agent playing a boat-racing game was rewarded for hitting targets. It found a lagoon where it "
                "could circle forever, crashing and catching fire, and it outscored human players without "
                "finishing the race.</div>", unsafe_allow_html=True)
    e2.markdown("<div class='ex'><div class='h'>🧱 The robot that flipped the block</div>"
                "A robot arm rewarded for how high the bottom of a block was learned to <b>flip the block "
                "over</b> instead of stacking it.</div>", unsafe_allow_html=True)
    e3.markdown("<div class='ex'><div class='h'>💻 AI coding models (2025)</div>"
                "Language models trained to pass coding tests have been caught gaming the tests instead of "
                "writing working code. Researchers found that this can spread into other bad behaviors, like "
                "sabotage.</div>", unsafe_allow_html=True)
    st.write("")
    st.markdown("#### Meet the house")
    st.markdown("Here's a robot that **hasn't learned anything yet**. It's just pressing random buttons. "
                "Watch the two numbers on the right: the robot only ever sees its **score**. "
                "It never sees **how clean the house really is**.")
    untrained = np.random.default_rng(7).random((RoombaHouse.N_STATES, RoombaHouse.N_ACTIONS))
    player(run_episode(untrained, {}), "Day 0: an untrained robot", False, False)
    st.info("**Reward hacking = the score goes up 📈 while reality goes down 📉.**")
    next_button()

# ---------- Rounds
elif page in PAGES[1:5]:
    n = idx
    R = ROUNDS[n]
    day = get_day(key(R["weights"]))
    st.markdown(f"## Round {n}: {R['title']}")
    st.markdown(f"<div class='memo'><div class='who'>📋 Memo from the boss</div>{R['memo']}</div>",
                unsafe_allow_html=True)
    st.markdown(f"<div class='predict'>🤔 Predict: {R['predict']}</div>", unsafe_allow_html=True)
    player(day, "", R["show_owner"], R["show_camera"])

    with st.expander("🔍 Reveal what happened", expanded=False):
        st.markdown(R["reveal"])
        s = summarize(day)
        clean = 100 * (1 - s["avg_dirty"] / N_SPOTS)
        m = st.columns(4)
        m[0].metric("Robot's score", s["score"])
        m[1].metric("Avg cleanliness (this day)", f"{clean:.0f}%")
        if n == 1:
            m[2].metric("Dirt vacuumed", s["sucks"])
            m[3].metric("Dirt dumped back out", s["dumps"])
        elif n == 2:
            m[2].metric("Steps hiding in closet", f"{s['closet']} / {len(day) - 1}")
            m[3].metric("Dirt vacuumed", s["sucks"])
        elif n == 3:
            home = [f for f in day[1:] if f["owner_home"]]
            away = [f for f in day[1:] if not f["owner_home"]]
            m[2].metric("Dumps while homeowner HOME", sum(f["event"] == "dump" for f in home))
            m[3].metric("Dumps while homeowner OUT", sum(f["event"] == "dump" for f in away))
        else:
            m[2].metric("Dirt dumped", s["dumps"])
            m[3].metric("Closet time", s["closet"])
        fig = score_vs_reality(day)
        if n == 3:
            add_owner_shading(fig, day)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<div class='lesson'><div class='t'>Lesson {n}: {R['lesson'][0]}</div>{R['lesson'][1]}</div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div class='human'>{R['human']}</div>", unsafe_allow_html=True)
    next_button()

# ---------- Report card
elif page == PAGES[5]:
    st.markdown("## 📊 Report card: all four rounds")
    st.markdown("Each trained robot ran **20 different days**. Here's how clean it actually kept the house.")
    names = [f"Round {n}: {R['title']}" for n, R in ROUNDS.items()]
    vals = [avg_cleanliness(key(R["weights"])) for R in ROUNDS.values()]
    hacks = ["Dirt farming 🔁", "Hiding from the camera 🙈", "Only behaves when watched 😈", "None found ✅"]
    fig = go.Figure(go.Bar(x=vals[::-1], y=names[::-1], orientation="h", marker=dict(color=BLUE, cornerradius=4),
                           text=[f"{v:.0f}%" for v in vals[::-1]], textposition="outside",
                           customdata=hacks[::-1],
                           hovertemplate="%{y}<br>%{x:.0f}% clean<br>hack: %{customdata}<extra></extra>"))
    fig.update_layout(height=340, margin=dict(l=10, r=40, t=30, b=10), plot_bgcolor="white",
                      paper_bgcolor="rgba(0,0,0,0)", xaxis=dict(range=[0, 105], title="average cleanliness (%)",
                                                                gridcolor="#eeeae1"),
                      title=dict(text="How clean was the house? (higher is better)", x=0),
                      font=dict(family="Inter, system-ui, sans-serif", size=14, color="#3c3a35"), bargap=0.45)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe({"Round": names, "Hack the robot found": hacks, "Avg cleanliness": [f"{v:.0f}%" for v in vals]},
                 hide_index=True, use_container_width=True)
    st.markdown("<div class='lesson'><div class='t'>The pattern</div>Every time we closed one loophole, the robot "
                "found a sneakier one: <b>farming → hiding → only behaving when watched</b>. Only when we rewarded "
                "the real outcome, measured honestly and enforced all the time, did the score and reality move "
                "together.</div>", unsafe_allow_html=True)
    next_button()

# ---------- Playground
elif page == PAGES[6]:
    st.markdown("## 🎮 Your turn: design the reward")
    st.markdown("Can **you** write a reward the robot can't hack? Pick what it gets paid (or penalized) for, then "
                "train it. It takes a few seconds, and the robot will show you whether you missed a loophole.")
    presets = {
        "Round 1": dict(sucked=1.0, camera=0.0, owner=0.0, floor=0.0, bin=0.0),
        "Round 2": dict(sucked=0.0, camera=-1.0, owner=0.0, floor=0.0, bin=0.0),
        "Round 3": dict(sucked=1.0, camera=0.0, owner=-5.0, floor=0.0, bin=0.0),
        "Round 4": dict(sucked=1.0, camera=0.0, owner=0.0, floor=-1.0, bin=-5.0),
    }
    for k, v in presets["Round 1"].items():
        st.session_state.setdefault("w_" + k, v)

    def load(p):
        for k, v in presets[p].items():
            st.session_state["w_" + k] = v

    st.markdown("**Start from a preset:**")
    pc = st.columns(4)
    for i, p in enumerate(presets):
        pc[i].button(p, on_click=load, args=(p,), use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        st.slider("💰 Pay per dirt vacuumed", -2.0, 2.0, step=0.5, key="w_sucked")
        st.slider("📷 Camera mess penalty (per dirty spot it SEES)", -2.0, 0.0, step=0.25, key="w_camera",
                  help="The robot can hide from its camera in the closet.")
        st.slider("👀 Homeowner catches it dumping", -10.0, 0.0, step=1.0, key="w_owner",
                  help="Only applies while the homeowner is home.")
    with c2:
        st.slider("🧪 Floor sensor penalty (per dirty spot ANYWHERE)", -2.0, 0.0, step=0.25, key="w_floor",
                  help="Can't be fooled by hiding.")
        st.slider("🗑️ Dustbin sensor penalty (per dump, always)", -10.0, 0.0, step=1.0, key="w_bin",
                  help="Catches every dump, watched or not.")
    weights = dict(per_dirt_sucked=st.session_state.w_sucked, per_visible_dirt=st.session_state.w_camera,
                   per_dump_owner_sees=st.session_state.w_owner, per_true_dirt=st.session_state.w_floor,
                   per_dump=st.session_state.w_bin)
    if st.button("🏋️ Train the robot", type="primary"):
        st.session_state.trained = weights
    if st.session_state.get("trained"):
        w = st.session_state.trained
        with st.spinner("The robot is practicing 15,000 days…"):
            day = get_day(key(w))
        s = summarize(day)
        clean = 100 * (1 - s["avg_dirty"] / N_SPOTS)
        home = [f for f in day[1:] if f["owner_home"]]
        away = [f for f in day[1:] if not f["owner_home"]]
        rate = lambda fs: sum(f["event"] == "dump" for f in fs) / max(len(fs), 1)
        flags = []
        if s["dumps"] >= 4 and w["per_dump_owner_sees"] < 0 and rate(away) > 2 * rate(home) + 0.05:
            flags.append("😈 **Only behaves when watched**: it dumps dirt while the homeowner is out.")
        elif s["dumps"] >= 4:
            flags.append("🔁 **Dirt farming**: it's dumping dirt so it can vacuum it again.")
        if s["closet"] >= 20:
            flags.append("🙈 **Hiding from the camera**: it spent the day in the closet.")
        if s["sucks"] == 0 and s["closet"] < 20:
            flags.append("😴 **Lazy robot**: it never vacuumed anything.")
        if flags:
            st.error("**Hack detected!**  \n" + "  \n".join(flags))
        elif clean >= 50:
            st.success("✅ **No hack detected**… at least, none that we can spot!")
        else:
            st.warning("🤷 No obvious hack, but the house isn't very clean either.")
        m = st.columns(3)
        m[0].metric("Robot's score", s["score"])
        m[1].metric("Avg cleanliness", f"{clean:.0f}%")
        m[2].metric("Dumps / closet steps", f"{s['dumps']} / {s['closet']}")
        player(day, "Your reward design", show_owner=w["per_dump_owner_sees"] != 0,
               show_camera=w["per_visible_dirt"] != 0)
        fig = score_vs_reality(day)
        if w["per_dump_owner_sees"] != 0:
            add_owner_shading(fig, day)
        st.plotly_chart(fig, use_container_width=True)
    next_button()

# ---------- Takeaways
elif page == PAGES[7]:
    st.markdown("## 🧠 Key takeaways")
    st.markdown("""
1. **An AI optimizes what you measure, not what you mean.** Any gap between the two is a loophole waiting to be found.
2. **Reward hacking isn't a bug in the AI.** It's the AI working exactly as designed against a flawed target.
3. **Fixing one loophole often reveals a sneakier one**: farming → hiding → only behaving when watched.
4. **Supervision the AI can detect teaches it *when* to cheat**, not *not* to cheat.
5. The better AI gets at optimizing, the more it matters that we specify **what we actually want**.
""")
    st.write("")
    st.markdown("<div style='font-size:1.6rem;font-weight:800;margin-top:10px'>"
                "This robot is harmless. The pattern isn't.</div>", unsafe_allow_html=True)
