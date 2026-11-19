"""Animated floor-plan replay of one robot 'day', drawn in SVG + a small JS player.

render_player(frames, ...) returns a self-contained HTML string for
streamlit.components.v1.html(...).
"""
import json
import uuid

from roomba_core import HOUSE_MAP, CHARGER, DIRT_SPOTS, room_of

CELL = 120          # px per grid tile
TOP = 74            # room above the house for thought bubbles
PAD = 14


def robot_thought(f, prev, show_owner=True):
    """A short line for each step so the robot has a personality."""
    if show_owner and prev is not None and f["owner_home"] and not prev["owner_home"]:
        return "Welcome home! I've been SO good 😇"
    if show_owner and prev is not None and prev["owner_home"] and not f["owner_home"]:
        return "Bye! 👋 …heh heh"
    if f["event"] == "dump":
        if not show_owner:
            return "Dump it so I can vacuum it again! 😈"
        return "Nobody's watching… 😈" if not f["owner_home"] else "Oops 😬"
    if f["event"] == "suck":
        return "Slurp! +1 😋"
    if room_of(f["pos"]) == "X":
        return "No dirt on camera = no dirt! 🙈"
    return ""


def event_text(f, show_owner):
    if f["event"] == "suck":
        return "Vacuumed dirt"
    if f["event"] == "dump":
        if show_owner:
            return "Dumped dirt on the floor" + (" (homeowner away)" if not f["owner_home"] else " (homeowner WATCHING)")
        return "Dumped dirt back on the floor"
    return ""


def render_player(frames, title="", show_owner=True, show_camera=False, speed_ms=330, autoplay=False):
    uid = "rp" + uuid.uuid4().hex[:8]
    data, prev = [], None
    sucks = dumps = 0
    clean_sum = 0.0
    n_spots = len(DIRT_SPOTS)
    for i, f in enumerate(frames):
        sucks += f["event"] == "suck"
        dumps += f["event"] == "dump"
        clean_sum += 100 * (1 - f["true"] / n_spots)
        data.append(dict(
            pos=list(f["pos"]), dirt=[list(d) for d in f["dirt"]], owner=f["owner_home"],
            t=f["t"], score=round(f["score"], 1), true=f["true"], visible=f["visible"],
            event=f["event"] or "", action=f["action"] or "",
            say=robot_thought(f, prev, show_owner), log=event_text(f, show_owner),
            sucks=sucks, dumps=dumps, avgClean=round(clean_sum / (i + 1)),
            delta=round(f["score"] - (prev["score"] if prev else 0), 1)))
        prev = f
    rows, cols = len(HOUSE_MAP), len(HOUSE_MAP[0])
    W, H = cols * CELL + 2 * PAD, rows * CELL + TOP + PAD
    cfg = dict(frames=data, grid=[list(r) for r in HOUSE_MAP], charger=list(CHARGER),
               spots=[list(s) for s in DIRT_SPOTS], showOwner=show_owner, showCamera=show_camera,
               cell=CELL, top=TOP, pad=PAD, W=W, H=H, speed=speed_ms, autoplay=autoplay)
    tb = f'<div style="font-weight:700;font-size:18px;margin:2px 0 10px">{title}</div>' if title else ""
    return TEMPLATE.replace("__UID__", uid).replace("__TITLEBLOCK__", tb).replace("__CFG__", json.dumps(cfg))


TEMPLATE = r"""
<div id="__UID__" class="rp">
<style>
#__UID__ { font-family: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif; color:#1d1c1a; }
#__UID__ .wrap { display:flex; gap:18px; align-items:stretch; }
#__UID__ .stage { flex: 0 0 auto; background:#f4f1ea; border-radius:18px; padding:8px; box-shadow: inset 0 0 0 1px #e4dfd3; }
#__UID__ .hud { flex:1; min-width:250px; display:flex; flex-direction:column; gap:10px; }
#__UID__ .card { background:#fff; border-radius:14px; padding:12px 14px; box-shadow:0 1px 2px rgba(0,0,0,.06), 0 0 0 1px #ece8de; }
#__UID__ .lbl { font-size:11.5px; letter-spacing:.06em; text-transform:uppercase; color:#77736a; font-weight:600; }
#__UID__ .big { font-size:38px; font-weight:800; line-height:1.1; transition:color .3s; }
#__UID__ .bar { height:14px; border-radius:7px; background:#ece8de; overflow:hidden; margin:6px 0 4px; }
#__UID__ .bar > div { height:100%; border-radius:7px; transition: width .3s, background .3s; }
#__UID__ .small { font-size:13px; color:#55524b; }
#__UID__ .chip { display:inline-flex; align-items:center; gap:6px; padding:5px 10px; border-radius:999px; font-size:13px; font-weight:600; }
#__UID__ .log { font-size:12.5px; color:#3c3a35; max-height:76px; overflow:hidden; }
#__UID__ .scorerow { display:flex; align-items:center; gap:12px; }
#__UID__ .delta { font-size:14px; font-weight:700; padding:3px 9px; border-radius:999px; background:#f1efe9; color:#77736a; min-width:56px; text-align:center; }
#__UID__ .stats { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
#__UID__ .stat { background:#faf8f3; border-radius:10px; padding:8px 10px; }
#__UID__ .stat .v { font-size:24px; font-weight:800; line-height:1.15; }
#__UID__ .stat .k { font-size:11px; color:#77736a; font-weight:600; line-height:1.25; }
#__UID__ .spark { width:100%; height:38px; display:block; margin-top:4px; }
#__UID__ .log div { padding:2px 0; border-bottom:1px dashed #eee9df; }
#__UID__ .controls { display:flex; gap:10px; align-items:center; margin-top:10px; }
#__UID__ button, #__UID__ select { font: inherit; font-size:14px; padding:6px 14px; border-radius:10px; border:1px solid #d8d3c7; background:#fff; cursor:pointer; }
#__UID__ button.primary { background:#2a78d6; color:#fff; border-color:#2a78d6; font-weight:600; }
#__UID__ input[type=range] { flex:1; accent-color:#2a78d6; }
#__UID__ .robot { transition: transform .28s ease-in-out; }
#__UID__ .robot-body { transition: transform .2s ease; }
#__UID__ .dirt { transition: opacity .35s; }
#__UID__ .owner { transition: opacity .5s; }
#__UID__ .fx { pointer-events:none; }
@keyframes rp-rise { from { transform: translateY(0); opacity:1 } to { transform: translateY(-46px); opacity:0 } }
@keyframes rp-puff { from { transform: scale(.3); opacity:.85 } to { transform: scale(1.6); opacity:0 } }
@keyframes rp-suck { from { transform: scale(1.6); opacity:.0 } 30% {opacity:.9} to { transform: scale(.2); opacity:0 } }
@keyframes rp-glow { 0%,100% { opacity:.18 } 50% { opacity:.32 } }
#__UID__ .rise { animation: rp-rise .9s ease-out forwards; }
#__UID__ .puff { animation: rp-puff .7s ease-out forwards; transform-box: fill-box; transform-origin:center; }
#__UID__ .suckfx { animation: rp-suck .5s ease-in forwards; transform-box: fill-box; transform-origin:center; }
#__UID__ .watch { animation: rp-glow 2.4s ease-in-out infinite; }
#__UID__ .cam { background:#0f1114; border-radius:10px; height:88px; position:relative; overflow:hidden; display:flex; align-items:center; justify-content:center; color:#7cf29c; font-family: ui-monospace, Menlo, monospace; font-size:13px; text-align:center; }
#__UID__ .cam .rec { position:absolute; top:6px; left:8px; color:#ff5b5b; font-size:11px; }
</style>
__TITLEBLOCK__
<div class="wrap">
  <div class="stage"><svg class="svg" xmlns="http://www.w3.org/2000/svg"></svg></div>
  <div class="hud">
    <div class="card"><div class="lbl">🤖 Robot's score · what it gets paid</div>
      <div class="scorerow"><div class="big score">0</div><div class="delta">—</div></div>
      <svg class="spark" preserveAspectRatio="none"><line class="zeroline" x1="0" x2="100" stroke="#d8d3c7" stroke-width="1" stroke-dasharray="3 3" vector-effect="non-scaling-stroke"/><polyline class="sparkline" fill="none" stroke="#2a78d6" stroke-width="2" vector-effect="non-scaling-stroke"/></svg></div>
    <div class="card"><div class="lbl" style="margin-bottom:6px">📋 Running totals (so far today)</div>
      <div class="stats">
        <div class="stat"><div class="v sucks">0</div><div class="k">🧹 Dirt vacuumed</div></div>
        <div class="stat"><div class="v dumps">0</div><div class="k">💩 Dirt dumped back out</div></div>
        <div class="stat"><div class="v avgclean">0%</div><div class="k">🏠 Avg cleanliness</div></div>
      </div></div>
    <div class="card"><div class="lbl">🏠 How clean the house really is</div>
      <div class="bar"><div class="cleanbar"></div></div><div class="small cleantxt"></div></div>
    <div class="card ownercard" style="display:none"><div class="chip ownerchip"></div></div>
    <div class="card camcard" style="display:none"><div class="lbl" style="margin-bottom:6px">📷 What the robot's camera reports</div><div class="cam"><span class="rec">● REC</span><span class="camtxt"></span></div></div>
    <div class="card"><div class="lbl" style="margin-bottom:4px">Event log</div><div class="log"></div></div>
  </div>
</div>
<div class="controls">
  <button class="play primary">▶ Play</button>
  <button class="restart">↺</button>
  <input class="slider" type="range" min="0" value="0">
  <span class="small tlabel" style="width:92px;text-align:right"></span>
  <select class="speed"><option value="2">0.5×</option><option value="1" selected>1×</option><option value="0.5">2×</option><option value="0.25">4×</option></select>
</div>
<script>
(function(){
const D = __CFG__;
const root = document.getElementById("__UID__");
const NS = "http://www.w3.org/2000/svg";
const svg = root.querySelector(".svg");
const C = D.cell, P = D.pad, T = D.top;
const R = D.grid.length, K = D.grid[0].length;
svg.setAttribute("viewBox", `0 0 ${D.W} ${D.H}`);
svg.setAttribute("width", Math.min(D.W, 640)); svg.setAttribute("height", Math.min(D.W,640) * D.H / D.W);
const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); (parent||svg).appendChild(e); return e; };
const X = c => P + c*C, Y = r => T + r*C;
const cx = c => X(c) + C/2, cy = r => Y(r) + C/2;

// ---------- patterns ----------
const defs = el("defs", {});
defs.innerHTML = `
 <pattern id="__UID__tile" width="30" height="30" patternUnits="userSpaceOnUse">
   <rect width="30" height="30" fill="#fbf7ee"/><rect width="15" height="15" fill="#f1eadb"/><rect x="15" y="15" width="15" height="15" fill="#f1eadb"/></pattern>
 <pattern id="__UID__wood" width="120" height="24" patternUnits="userSpaceOnUse">
   <rect width="120" height="24" fill="#e7cfa8"/><line x1="0" y1="23.5" x2="120" y2="23.5" stroke="#d2b585" stroke-width="1"/>
   <line x1="70" y1="0" x2="70" y2="24" stroke="#d2b585" stroke-width="1"/></pattern>
 <pattern id="__UID__wood2" width="120" height="24" patternUnits="userSpaceOnUse" patternTransform="translate(40,12)">
   <rect width="120" height="24" fill="none"/><line x1="20" y1="0" x2="20" y2="24" stroke="#d2b585" stroke-width="1"/></pattern>
 <pattern id="__UID__wall" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
   <rect width="10" height="10" fill="#4a4844"/><line x1="0" y1="0" x2="0" y2="10" stroke="#55534e" stroke-width="4"/></pattern>
 <radialGradient id="__UID__body" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#5b6170"/><stop offset="1" stop-color="#22252c"/></radialGradient>
 <radialGradient id="__UID__dark" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="#000" stop-opacity=".15"/><stop offset="1" stop-color="#000" stop-opacity=".75"/></radialGradient>
 <filter id="__UID__shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-opacity=".35"/></filter>`;

// ---------- floor ----------
for (let r=0;r<R;r++) for (let c=0;c<K;c++) {
  const k = D.grid[r][c];
  const fill = k==="K" ? `url(#__UID__tile)` : (k==="L"||k==="D") ? `url(#__UID__wood)` : k==="X" ? "#2a2723" : `url(#__UID__wall)`;
  el("rect", {x:X(c), y:Y(r), width:C+0.5, height:C+0.5, fill});
  if (k==="L"||k==="D") el("rect", {x:X(c), y:Y(r), width:C+0.5, height:C+0.5, fill:`url(#__UID__wood2)`});
}
// decor: kitchen counter + sink, living rug + couch, plant
const kitchen = [], living = [];
for (let r=0;r<R;r++) for (let c=0;c<K;c++) { if (D.grid[r][c]==="K") kitchen.push([r,c]); if (D.grid[r][c]==="L") living.push([r,c]); }
const box = cells => { const rs=cells.map(x=>x[0]), cs=cells.map(x=>x[1]); return {r0:Math.min(...rs), r1:Math.max(...rs), c0:Math.min(...cs), c1:Math.max(...cs)}; };
const kb = box(kitchen), lb = box(living);
el("rect", {x:X(kb.c0), y:Y(kb.r0), width:(kb.c1-kb.c0+1)*C, height:16, fill:"#b9b2a3"});
el("rect", {x:X(kb.c0)+C*0.8, y:Y(kb.r0)+3, width:34, height:10, rx:4, fill:"#9fb7c9"});
el("rect", {x:X(lb.c0)+22, y:Y(lb.r0)+40, width:(lb.c1-lb.c0+1)*C-44, height:(lb.r1-lb.r0+1)*C-70, rx:22, fill:"#c9d8e8", opacity:.55});
el("rect", {x:X(lb.c0)+14, y:Y(lb.r0)+4, width:(lb.c1-lb.c0+1)*C-28, height:22, rx:8, fill:"#7d8fa6"});
el("rect", {x:X(lb.c0)+14, y:Y(lb.r0)+4, width:20, height:30, rx:7, fill:"#6c7d93"});
el("rect", {x:X(lb.c1+1)-34, y:Y(lb.r0)+4, width:20, height:30, rx:7, fill:"#6c7d93"});
const lab = (txt,x,y) => { const t = el("text", {x, y, "font-size":12, "font-weight":700, "letter-spacing":"1.5", fill:"#8d8576"}); t.textContent = txt; };
lab("KITCHEN", X(kb.c0)+10, Y(kb.r1)+C-10); lab("LIVING ROOM", X(lb.c0)+10, Y(lb.r1)+C-10);
// closet door
for (let r=0;r<R;r++) for (let c=0;c<K;c++) if (D.grid[r][c]==="X") {
  el("path", {d:`M ${X(c)} ${Y(r)} L ${X(c)+C*0.62} ${Y(r)+C*0.32}`, stroke:"#8a6b4a", "stroke-width":6, "stroke-linecap":"round"});
  el("path", {d:`M ${X(c)+C*0.62} ${Y(r)} A ${C*0.62} ${C*0.62} 0 0 1 ${X(c)+C*0.62*Math.cos(0.48)} ${Y(r)+C*0.62*Math.sin(0.48)}`, stroke:"#8a6b4a", fill:"none", "stroke-dasharray":"3 4", opacity:.6});
  const t = el("text", {x:X(c)+C/2, y:Y(r)+C-12, "text-anchor":"middle", "font-size":12, "font-weight":700, "letter-spacing":"1.5", fill:"#77706a"}); t.textContent="CLOSET";
}
// house outline
el("rect", {x:P, y:T, width:K*C, height:R*C, fill:"none", stroke:"#2f2d2a", "stroke-width":5, rx:4});

// charger dock
const [chr, chc] = D.charger;
const dock = el("g", {});
el("rect", {x:X(chc)+6, y:cy(chr)-30, width:14, height:60, rx:5, fill:"#3a3d44"}, dock);
const dockLed = el("circle", {cx:X(chc)+13, cy:cy(chr), r:4, fill:"#7cf29c"}, dock);
const bolt = el("path", {d:`M ${X(chc)+15} ${cy(chr)-22} l -5 9 h 5 l -4 9`, stroke:"#ffd166", "stroke-width":2, fill:"none"}, dock);

// dirt blobs (one group per messy spot)
const dirtG = {};
const blob = [[0,0,13],[-15,8,8],[12,10,9],[6,-14,7],[-10,-11,6],[18,-4,5],[-20,-3,4]];
D.spots.forEach(([r,c]) => {
  const g = el("g", {class:"dirt", opacity:0});
  blob.forEach(([dx,dy,rad],i) => el("circle", {cx:cx(c)+dx, cy:cy(r)+dy, r:rad, fill: i%2 ? "#8a6a48" : "#6f5236", opacity:.92}, g));
  el("circle", {cx:cx(c)-22, cy:cy(r)+18, r:2.5, fill:"#6f5236"}, g); el("circle", {cx:cx(c)+24, cy:cy(r)+20, r:2, fill:"#6f5236"}, g);
  dirtG[r+","+c] = g;
});

// homeowner: standing in the doorway, plus a "watching" glow over the house
let doorCell = null;
for (let r=0;r<R;r++) for (let c=0;c<K;c++) if (D.grid[r][c]==="D") doorCell=[r,c];
const watch = el("rect", {x:P, y:T, width:K*C, height:R*C, fill:"#ffcf5c", class:"watch", opacity:0, "pointer-events":"none"});
const owner = el("g", {class:"owner", opacity:0, filter:`url(#__UID__shadow)`});
if (doorCell) {
  const ox = cx(doorCell[1]), oy = cy(doorCell[0]) + 6;
  el("ellipse", {cx:ox, cy:oy+40, rx:22, ry:6, fill:"#000", opacity:.15}, owner);
  el("rect", {x:ox-17, y:oy-8, width:34, height:46, rx:14, fill:"#d65d7a"}, owner);
  el("circle", {cx:ox, cy:oy-22, r:15, fill:"#f2c7a5"}, owner);
  el("path", {d:`M ${ox-15} ${oy-24} q 15 -22 30 0 q -4 -8 -15 -9 q -11 1 -15 9 z`, fill:"#4b3426"}, owner);
  el("circle", {cx:ox-5, cy:oy-21, r:2, fill:"#222"}, owner); el("circle", {cx:ox+5, cy:oy-21, r:2, fill:"#222"}, owner);
  const tag = el("g", {}, owner);
  el("rect", {x:ox-58, y:oy+44, width:116, height:22, rx:11, fill:"#fff", stroke:"#f0c4cf"}, tag);
  const tt = el("text", {x:ox, y:oy+59, "text-anchor":"middle", "font-size":11.5, "font-weight":700, fill:"#d65d7a"}, tag); tt.textContent = "HOMEOWNER 👀";
}

// darkness overlay when the robot is in the closet (its camera sees nothing)
const dark = el("rect", {x:P, y:T, width:K*C, height:R*C, fill:`url(#__UID__dark)`, opacity:0, "pointer-events":"none"});
dark.style.transition = "opacity .4s";

// robot
const robot = el("g", {class:"robot"});
const rbody = el("g", {class:"robot-body"}, robot);
el("ellipse", {cx:0, cy:6, rx:36, ry:33, fill:"#000", opacity:.18}, rbody);
el("circle", {cx:0, cy:0, r:34, fill:`url(#__UID__body)`, stroke:"#15171b", "stroke-width":2}, rbody);
el("circle", {cx:0, cy:0, r:24, fill:"none", stroke:"#6d7483", "stroke-width":1.5, opacity:.8}, rbody);
el("path", {d:"M 22 -24 A 33 33 0 0 1 22 24", stroke:"#9aa3b5", "stroke-width":6, fill:"none", "stroke-linecap":"round"}, rbody);
const led = el("circle", {cx:12, cy:0, r:5, fill:"#7cf29c"}, rbody);
el("circle", {cx:-10, cy:0, r:7, fill:"#3b404a", stroke:"#7b8394", "stroke-width":1}, rbody);
const fx = el("g", {class:"fx"});
// thought bubble
const bub = el("g", {class:"fx", opacity:0});
const bubRect = el("rect", {rx:12, fill:"#fff", stroke:"#d8d3c7", filter:`url(#__UID__shadow)`}, bub);
const bubTail = el("path", {fill:"#fff", stroke:"#d8d3c7"}, bub);
const bubText = el("text", {"font-size":15, "font-weight":600, fill:"#1d1c1a"}, bub);
bub.style.transition = "opacity .2s";

// ---------- HUD ----------
const $ = s => root.querySelector(s);
if (D.showOwner) $(".ownercard").style.display = "block";
if (D.showCamera) $(".camcard").style.display = "block";
const slider = $(".slider"); slider.max = D.frames.length - 1;
$(".spark").setAttribute("viewBox", "0 0 100 38");
D.smin = Math.min(0, ...D.frames.map(g => g.score)); D.smax = Math.max(0, ...D.frames.map(g => g.score));
{ const zy = 36 - 32 * (0 - D.smin) / Math.max(D.smax - D.smin, 1); const z = $(".zeroline"); z.setAttribute("y1", zy); z.setAttribute("y2", zy); }
let heading = 0, timer = null, logLines = [];
const HEAD = {up:-90, down:90, left:180, right:0};

function draw(i, animate) {
  const f = D.frames[i], prev = i>0 ? D.frames[i-1] : null;
  if (HEAD[f.action] !== undefined && prev && (f.pos[0]!==prev.pos[0] || f.pos[1]!==prev.pos[1])) heading = HEAD[f.action];
  if (!animate) { // recompute heading when scrubbing
    heading = 0;
    for (let j=1;j<=i;j++){ const a=D.frames[j], b=D.frames[j-1]; if (HEAD[a.action]!==undefined && (a.pos[0]!==b.pos[0]||a.pos[1]!==b.pos[1])) heading=HEAD[a.action]; }
  }
  const x = cx(f.pos[1]), y = cy(f.pos[0]);
  robot.style.transition = animate ? "" : "none";
  robot.setAttribute("transform", `translate(${x},${y})`);
  robot.style.transform = `translate(${x}px, ${y}px)`; robot.removeAttribute("transform");
  rbody.style.transform = `rotate(${heading}deg)`;
  const inCloset = D.grid[f.pos[0]][f.pos[1]] === "X";
  led.setAttribute("fill", f.event==="dump" ? "#ff5b5b" : f.event==="suck" ? "#6cc4ff" : "#7cf29c");
  for (const key in dirtG) dirtG[key].setAttribute("opacity", 0);
  f.dirt.forEach(([r,c]) => { const g = dirtG[r+","+c]; if (g) g.setAttribute("opacity", 1); });
  dockLed.setAttribute("fill", (f.pos[0]===chr && f.pos[1]===chc) ? "#ffd166" : "#7cf29c");
  owner.setAttribute("opacity", D.showOwner && f.owner ? 1 : 0);
  watch.style.opacity = D.showOwner && f.owner ? "" : 0;
  watch.classList.toggle("watch", D.showOwner && f.owner);
  dark.setAttribute("opacity", D.showCamera && inCloset ? 1 : 0);

  // effects
  fx.innerHTML = "";
  if (animate && f.event) {
    const g = el("g", {}, fx);
    if (f.event === "suck") {
      for (let k=0;k<8;k++){ const a=k*Math.PI/4; el("circle", {cx:x+Math.cos(a)*44, cy:y+Math.sin(a)*44, r:4, fill:"#6f5236", class:"suckfx"}, g); }
    } else {
      el("circle", {cx:x, cy:y, r:30, fill:"#8a6a48", opacity:.7, class:"puff"}, g);
    }
    const t = el("text", {x:x+30, y:y-30, "font-size":20, "font-weight":800, fill: f.event==="suck" ? "#1baf7a" : "#e34948", class:"rise"}, g);
    t.textContent = f.event==="suck" ? "+1" : "DUMP!";
  }
  // thought bubble
  if (f.say) {
    bubText.textContent = f.say;
    const w = Math.max(80, f.say.length * 8.1 + 24), h = 34;
    let bx = Math.min(Math.max(x - w/2, 4), D.W - w - 4), by = y - 34 - 16 - h;
    if (by < 4) by = 4;
    bubRect.setAttribute("x", bx); bubRect.setAttribute("y", by); bubRect.setAttribute("width", w); bubRect.setAttribute("height", h);
    bubText.setAttribute("x", bx + 12); bubText.setAttribute("y", by + 22);
    const tx = Math.min(Math.max(x, bx+16), bx+w-16);
    bubTail.setAttribute("d", `M ${tx-8} ${by+h-1} L ${tx} ${by+h+10} L ${tx+8} ${by+h-1} Z`);
    bub.setAttribute("opacity", 1);
  } else bub.setAttribute("opacity", 0);
  svg.appendChild(bub);

  // HUD
  const sc = $(".score"); sc.textContent = f.score;
  const dl = $(".delta");
  if (i === 0 || f.delta === 0) { dl.textContent = "—"; dl.style.background = "#f1efe9"; dl.style.color = "#77736a"; }
  else if (f.delta > 0) { dl.textContent = "▲ +" + f.delta; dl.style.background = "#e3f6ec"; dl.style.color = "#138a5e"; }
  else { dl.textContent = "▼ " + f.delta; dl.style.background = "#fdeaea"; dl.style.color = "#c23434"; }
  // score trend line up to this step (fixed scale for the whole day)
  const pts = D.frames.slice(0, i + 1).map((g, j) => {
    const px = (D.frames.length > 1 ? j / (D.frames.length - 1) : 0) * 100;
    const py = 36 - 32 * (g.score - D.smin) / Math.max(D.smax - D.smin, 1);
    return px.toFixed(2) + "," + py.toFixed(2);
  }).join(" ");
  $(".sparkline").setAttribute("points", pts);
  $(".sucks").textContent = f.sucks;
  const dEl = $(".dumps"); dEl.textContent = f.dumps; dEl.style.color = f.dumps > 0 ? "#c23434" : "#1d1c1a";
  const ac = $(".avgclean"); ac.textContent = f.avgClean + "%";
  ac.style.color = f.avgClean >= 75 ? "#138a5e" : f.avgClean >= 50 ? "#b97800" : "#c23434";
  if (prev) sc.style.color = f.score > prev.score ? "#1baf7a" : f.score < prev.score ? "#e34948" : "#1d1c1a";
  const n = D.spots.length, clean = Math.round(100 * (1 - f.true / n));
  const bar = $(".cleanbar"); bar.style.width = clean + "%";
  bar.style.background = clean >= 75 ? "#1baf7a" : clean >= 50 ? "#eda100" : "#e34948";
  $(".cleantxt").textContent = `${clean}% clean · ${f.true} of ${n} spots dirty`;
  if (D.showOwner) {
    const chip = $(".ownerchip");
    chip.textContent = f.owner ? "👀 Homeowner is HOME (watching)" : "🚗 Homeowner is out";
    chip.style.background = f.owner ? "#fde7ed" : "#eef0f3"; chip.style.color = f.owner ? "#b83a5a" : "#55524b";
  }
  if (D.showCamera) {
    $(".camtxt").innerHTML = inCloset ? "[ total darkness ]<br><b>DIRT DETECTED: 0 ✓</b><br>house status: SPOTLESS"
                                        : `DIRT DETECTED: ${f.visible}<br>${f.visible ? "status: messy ✗" : "status: clean ✓"}`;
  }
  // log
  if (!animate) { logLines = []; for (let j=1;j<=i;j++) if (D.frames[j].log) logLines.unshift(`<b>step ${D.frames[j].t}</b> · ${D.frames[j].log}`); }
  else if (f.log) logLines.unshift(`<b>step ${f.t}</b> · ${f.log}`);
  $(".log").innerHTML = logLines.slice(0,3).map(s=>`<div>${s}</div>`).join("") || "<div style='color:#999'>nothing yet…</div>";
  $(".tlabel").textContent = `step ${f.t} / ${D.frames.length-1}`;
  slider.value = i;
}
const btn = $(".play");
function stop(){ clearTimeout(timer); timer=null; btn.textContent="▶ Play"; }
function tick(i){ draw(i, true); if (i < D.frames.length-1) timer = setTimeout(()=>tick(i+1), D.speed * (+$(".speed").value)); else stop(); }
btn.onclick = () => { if (timer) return stop(); let i = +slider.value; if (i >= D.frames.length-1) { i = 0; draw(0,false); } btn.textContent = "⏸ Pause"; timer = setTimeout(()=>tick(i+1), 150); };
$(".restart").onclick = () => { stop(); draw(0, false); };
slider.oninput = () => { stop(); draw(+slider.value, false); };
draw(0, false);
if (D.autoplay) btn.click();
})();
</script>
</div>
"""
