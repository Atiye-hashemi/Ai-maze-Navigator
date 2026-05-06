

import pygame
import math

# ─────────────────────────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────────────────────────
BG       = (10,  14,  26)
PANEL    = (17,  24,  39)
PANEL2   = (12,  18,  30)
BORDER   = (38,  58,  84)
ACCENT   = (0,   212, 255)
ACCENT2  = (124, 58,  237)
TEXT     = (220, 230, 242)
MUTED    = (90,  110, 140)
SUCCESS  = (16,  185, 129)
DANGER   = (239, 68,  68)
WARN     = (245, 158, 11)
WALL_C   = (22,  36,  52)
FREE_C   = (15,  24,  38)
VISIT_C  = (10,  38,  58)
AGENT_C  = (245, 158, 11)
TARGET_C = (16,  185, 129)
DOT_C    = (0,   160, 200)

# ─────────────────────────────────────────────────────────────────
# LAYOUT CONSTANTS
# ─────────────────────────────────────────────────────────────────
CELL     = 56
PAD      = 20
HEADER_H = 82
STATUS_H = 46
PANEL_W  = 430
TAB_H    = 44
BTN_H    = 38

# ─────────────────────────────────────────────────────────────────
# MODULE STATE
# ─────────────────────────────────────────────────────────────────
_screen      = None
_clock       = None
_fonts       = {}
_rows        = 0
_cols        = 0
_active_tab  = 0
_log_entries = []
_log_offset  = 0
_tab_rects   = []
_reset_rect  = None
_start_rect  = None
_started     = False
_TAB_LABELS  = ["Logic", "Math", "GA", "Log"]
_TAB_ICONS   = ["🧠", "📐", "🧬", "📋"]


# ─────────────────────────────────────────────────────────────────
# MATH HELPERS
# ─────────────────────────────────────────────────────────────────
def _l1(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def _l2(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def _path_cost(history, target):
    if len(history) < 2:
        return 0.0
    return (len(history)-1)*1.0 + _l2(history[-1], target)*1.5

def _softmax(safe_moves, target):
    if not safe_moves:
        return []
    scores = [-_l2(c, target) for _, c in safe_moves]
    m      = max(scores)
    exps   = [math.exp(s - m) for s in scores]
    t      = sum(exps)
    return [e/t for e in exps]

def _mp_log(pos, kb):
    dirs = [("North", (pos[0]-1, pos[1])),
            ("South", (pos[0]+1, pos[1])),
            ("East",  (pos[0],   pos[1]+1)),
            ("West",  (pos[0],   pos[1]-1))]
    out = []
    for name, coord in dirs:
        ib   = kb.is_within_bounds(coord)
        safe = kb.is_safe(coord)
        nw   = safe  # not_wall is true only if in bounds and safe
        out.append(dict(dir=name, coord=coord, in_bounds=ib, not_wall=nw, safe=safe))
    return out


# ─────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────
def init_display(maze_shape):
    """Initialise Pygame. Returns (screen, clock)."""
    global _screen, _clock, _fonts, _rows, _cols

    pygame.init()
    _rows, _cols = maze_shape

    maze_pw = _cols * CELL
    maze_ph = _rows * CELL
    win_w   = PAD + maze_pw + PAD + PANEL_W + PAD
    win_h   = HEADER_H + PAD + maze_ph + PAD + STATUS_H

    _screen = pygame.display.set_mode((win_w, win_h))
    pygame.display.set_caption("Autonomous Maze Agent  |  Principles of AI")
    _clock  = pygame.time.Clock()

    def F(size, bold=False):
        for name in ["Consolas", "Courier New", "Lucida Console", "DejaVu Sans Mono"]:
            try:
                f = pygame.font.SysFont(name, size, bold=bold)
                if f:
                    return f
            except Exception:
                pass
        return pygame.font.SysFont(None, size, bold=bold)

    _fonts["h1"]    = F(28, bold=True)
    _fonts["h2"]    = F(18, bold=True)
    _fonts["h3"]    = F(15, bold=True)
    _fonts["body"]  = F(15)
    _fonts["small"] = F(13)
    _fonts["tiny"]  = F(12)
    _fonts["tab"]   = F(15, bold=True)
    _fonts["btn"]   = F(15, bold=True)
    _fonts["num"]   = F(24, bold=True)
    _fonts["sub"]   = F(12)

    return _screen, _clock


def render_maze(screen, clock, maze, agent, start_pos, target_pos, fps=6):
    """
    Render one complete frame and handle all events.

    Returns:
        "quit"  — user closed the window
        "reset" — user clicked the Reset button
        None    — normal frame, keep going
    """
    global _log_entries, _log_offset, _active_tab

    _screen.fill(BG)

    w, h = _screen.get_size()
    mx0  = PAD
    my0  = HEADER_H + PAD

    # ── collect live agent data ───────────────────────────────────
    pos     = agent.pos
    history = list(agent.path_history)
    kb      = agent.kb
    reason  = getattr(agent, "last_reason", "")

    mp_data = _mp_log(pos, kb)
    _tab_logic._cache = mp_data          # feed live data into the Logic tab
    safe    = kb.infer_safe_moves(pos)
    probs   = _softmax(safe, target_pos)
    cost    = _path_cost(history, target_pos)
    steps   = len(history) - 1
    reached = (pos[0] == target_pos[0] and pos[1] == target_pos[1])

    # ── append log entry once per step ───────────────────────────
    if steps > 0:
        prev = history[-2] if len(history) >= 2 else None
        if not _log_entries or _log_entries[-1]["step"] != steps:
            _log_entries.append(dict(
                step=steps, frm=prev, to=pos,
                cost=round(cost, 2), reason=reason
            ))
            if len(_log_entries) > 300:
                _log_entries.pop(0)

    # ── draw everything ───────────────────────────────────────────
    _draw_header(w)
    _draw_maze(maze, pos, target_pos, history, mx0, my0)
    _draw_status(w, h, pos, target_pos, steps, cost, reached)

    px = mx0 + _cols * CELL + PAD
    py = HEADER_H + PAD
    ph = h - HEADER_H - PAD - STATUS_H - PAD
    _draw_panel(px, py, PANEL_W, ph,
                mp_data, safe, probs, cost,
                pos, target_pos, history, reason)

    # ── event handling ────────────────────────────────────────────
    result = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            result = "quit"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            global _started
            ex, ey = event.pos

            # start button
            if _start_rect and _start_rect.collidepoint(ex, ey) and not _started:
                _started = True
                result = "start"

            # tab bar clicks
            for i, r in enumerate(_tab_rects):
                if r.collidepoint(ex, ey):
                    _active_tab = i

            # reset button
            if _reset_rect and _reset_rect.collidepoint(ex, ey):
                _log_entries.clear()
                _log_offset  = 0
                _started     = False
                result = "reset"

            # log scroll via click (also handled by scroll wheel below)
            if _active_tab == 3:
                if event.button == 4:   # scroll up
                    _log_offset = max(0, _log_offset - 1)
                elif event.button == 5: # scroll down
                    _log_offset = min(max(0, len(_log_entries)-7), _log_offset+1)

        elif event.type == pygame.MOUSEWHEEL:
            if _active_tab == 3:
                _log_offset = max(0, min(
                    max(0, len(_log_entries)-7),
                    _log_offset - event.y
                ))

    pygame.display.flip()
    clock.tick(fps)
    return result


# ─────────────────────────────────────────────────────────────────
# INTERNAL DRAW PRIMITIVES
# ─────────────────────────────────────────────────────────────────
def _blit(text, font_key, color, x, y, max_w=None):
    font = _fonts[font_key]
    s    = str(text)
    if max_w:
        while len(s) > 3 and font.size(s)[0] > max_w:
            s = s[:-2] + "…"
    surf = font.render(s, True, color)
    _screen.blit(surf, (x, y))
    return font.size(s)[1]

def _rect(color, x, y, w, h, r=8, border=None, bw=1):
    pygame.draw.rect(_screen, color, (int(x), int(y), int(w), int(h)), border_radius=r)
    if border:
        pygame.draw.rect(_screen, border, (int(x), int(y), int(w), int(h)), bw, border_radius=r)

def _line(color, x1, y1, x2, y2, w=1):
    pygame.draw.line(_screen, color, (x1, y1), (x2, y2), w)

def _circle(color, cx, cy, rad, w=0):
    if rad > 0:
        pygame.draw.circle(_screen, color, (int(cx), int(cy)), int(rad), w)


# ─────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────
def _draw_header(win_w):
    _rect(PANEL, 0, 0, win_w, HEADER_H, r=0)
    _line(BORDER, 0, HEADER_H-1, win_w, HEADER_H-1)

    sub = "PRINCIPLES OF AI  ·  APPLIED GROUP PROJECT"
    sw  = _fonts["sub"].size(sub)[0]
    _blit(sub, "sub", ACCENT, (win_w - sw)//2, 10)

    title = "Autonomous Maze Navigation Agent"
    tw    = _fonts["h1"].size(title)[0]
    _blit(title, "h1", TEXT, (win_w - tw)//2, 28)

    pills = ["Logic", "Linear Algebra", "Genetic Algorithm", "Optimization"]
    total = sum(_fonts["tiny"].size(p)[0] + 24 for p in pills) + 8*(len(pills)-1)
    px    = (win_w - total) // 2
    for p in pills:
        pw = _fonts["tiny"].size(p)[0] + 24
        _rect(BORDER, px, 62, pw, 16, r=8)
        _blit(p, "tiny", ACCENT2, px+12, 63)
        px += pw + 8


# ─────────────────────────────────────────────────────────────────
# MAZE GRID
# ─────────────────────────────────────────────────────────────────
def _draw_maze(maze, agent_pos, target_pos, history, ox, oy):
    path_set = {(r, c) for r, c in history}

    for r in range(_rows):
        for c in range(_cols):
            x   = ox + c * CELL
            y   = oy + r * CELL
            val = maze[r][c]

            is_wall   = val == 1
            is_target = (r == target_pos[0] and c == target_pos[1])
            is_agent  = (r == agent_pos[0]  and c == agent_pos[1])
            in_path   = (r, c) in path_set

            if is_wall:
                bg = WALL_C
            elif is_target:
                bg = (10, 44, 30)
            elif in_path:
                bg = VISIT_C
            else:
                bg = FREE_C

            pygame.draw.rect(_screen, bg, (x, y, CELL, CELL))
            pygame.draw.rect(_screen, BORDER, (x, y, CELL, CELL), 1)

            cx, cy = x + CELL//2, y + CELL//2

            # wall diagonal lines
            if is_wall:
                for i in range(0, CELL*2, 10):
                    x1 = x + max(0, i-CELL);  y1 = y + min(i, CELL-1)
                    x2 = x + min(i, CELL-1);  y2 = y + max(0, i-CELL)
                    if 0 <= x1-x < CELL and 0 <= y1-y < CELL:
                        _line(BORDER, x1, y1, x2, y2)

            # path dot
            if in_path and not is_agent and not is_wall and not is_target:
                _circle(DOT_C, cx, cy, 5)
                _circle(ACCENT, cx, cy, 3)

            # target rings
            if is_target:
                _circle(TARGET_C, cx, cy, CELL//2-6, 3)
                _circle(TARGET_C, cx, cy, 7)
                tw = _fonts["h3"].size("T")[0]
                _blit("T", "h3", TARGET_C, cx-tw//2, cy-9)

            # agent with glow
            if is_agent:
                glow = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
                for rad in range(CELL//2-4, 4, -5):
                    a = max(0, 100 - (CELL//2-4-rad)*22)
                    pygame.draw.circle(glow, (*AGENT_C, a), (CELL//2, CELL//2), rad)
                _screen.blit(glow, (x, y))
                _circle(AGENT_C, cx, cy, CELL//2-8)
                _circle(BG,      cx, cy, CELL//2-16)
                aw = _fonts["h3"].size("A")[0]
                _blit("A", "h3", AGENT_C, cx-aw//2, cy-9)

            # tiny coord label
            _blit(f"{r},{c}", "tiny", (28, 48, 70), x+3, y+CELL-15)


# ─────────────────────────────────────────────────────────────────
# STATUS BAR
# ─────────────────────────────────────────────────────────────────
def _draw_status(win_w, win_h, pos, target_pos, steps, cost, reached):
    global _reset_rect, _start_rect
    sy = win_h - STATUS_H
    _rect(PANEL, 0, sy, win_w, STATUS_H, r=0)
    _line(BORDER, 0, sy, win_w, sy)

    info = (f"   Position: [{pos[0]}, {pos[1]}]     "
            f"Steps: {steps}     "
            f"Path Cost: {cost:.2f}     "
            f"Target: [{target_pos[0]}, {target_pos[1]}]")
    _blit(info, "body", MUTED, 10, sy+13)

    if reached:
        msg = "TARGET REACHED  ✓"
        mw  = _fonts["h3"].size(msg)[0]
        _blit(msg, "h3", SUCCESS, win_w - mw - 290, sy+12)

    mx, my = pygame.mouse.get_pos()
    bw, bh = 120, 32
    by     = sy + (STATUS_H - bh)//2

    if not _started:
        # START button — green
        bx           = win_w - bw - 16
        hover        = pygame.Rect(bx, by, bw, bh).collidepoint(mx, my)
        _start_rect  = pygame.Rect(bx, by, bw, bh)
        _reset_rect  = None
        bg   = (0, 80, 50) if hover else PANEL2
        bc   = SUCCESS     if hover else (0, 140, 80)
        _rect(bg, bx, by, bw, bh, r=8, border=bc)
        lbl  = "START"
        lw   = _fonts["btn"].size(lbl)[0]
        _blit(lbl, "btn", SUCCESS, bx+(bw-lw)//2, by+7)
    else:
        # RESET button — cyan
        bx          = win_w - bw - 16
        hover       = pygame.Rect(bx, by, bw, bh).collidepoint(mx, my)
        _reset_rect = pygame.Rect(bx, by, bw, bh)
        _start_rect = None
        _rect(PANEL2, bx, by, bw, bh, r=8, border=ACCENT if hover else BORDER)
        lbl = "RESET"
        lw  = _fonts["btn"].size(lbl)[0]
        _blit(lbl, "btn", ACCENT if hover else TEXT, bx+(bw-lw)//2, by+7)


# ─────────────────────────────────────────────────────────────────
# RIGHT PANEL SHELL
# ─────────────────────────────────────────────────────────────────
def _draw_panel(px, py, pw, ph, mp_log, safe_moves, probs,
                cost, agent_pos, target_pos, history, last_reason):
    global _tab_rects, _active_tab

    _rect(PANEL2, px, py, pw, ph, r=10, border=BORDER)

    # Tab bar
    _tab_rects = []
    tab_w = pw // len(_TAB_LABELS)
    for i, (icon, label) in enumerate(zip(_TAB_ICONS, _TAB_LABELS)):
        tx     = px + i*tab_w
        active = (i == _active_tab)
        _rect((0,52,76) if active else PANEL2, tx+3, py+3, tab_w-6, TAB_H-6, r=8)
        col = ACCENT if active else MUTED
        lbl = f"{icon}  {label}"
        lw  = _fonts["tab"].size(lbl)[0]
        _blit(lbl, "tab", col, tx+(tab_w-lw)//2, py+13)
        _tab_rects.append(pygame.Rect(tx, py, tab_w, TAB_H))

    _line(BORDER, px, py+TAB_H, px+pw, py+TAB_H)

    # Content area
    cx = px + 16
    cy = py + TAB_H + 16
    cw = pw - 32

    if   _active_tab == 0: _tab_logic(cx, cy, cw)
    elif _active_tab == 1: _tab_math(cx, cy, cw, agent_pos, target_pos, history, safe_moves, probs, cost)
    elif _active_tab == 2: _tab_ga(cx, cy, cw, last_reason)
    elif _active_tab == 3: _tab_log(cx, cy, cw, py+ph-8)


# ─────────────────────────────────────────────────────────────────
# TAB: LOGIC
# ─────────────────────────────────────────────────────────────────
def _tab_logic(x, y, w):
    _blit("Modus Ponens Inference Engine", "h2", ACCENT, x, y);  y += 28
    _blit("inBounds(n) ^ !wall(n)  =>  safe(n)", "small", MUTED, x, y);  y += 24

    # get current mp_log from module state — stored during render_maze
    cache = getattr(_tab_logic, "_cache", [])
    if not cache:
        _blit("Run the agent to see live inference.", "body", MUTED, x, y)
        return

    for e in cache:
        safe  = e["safe"]
        rh    = 72
        bg    = (10, 34, 52) if safe else (36, 12, 12)
        bc    = BORDER       if safe else (90, 22, 22)
        _rect(bg, x, y, w, rh, r=8, border=bc)

        # Direction + coord
        dir_col = ACCENT if safe else DANGER
        _blit(e["dir"], "h3", dir_col, x+12, y+8)
        _blit(f"[{e['coord'][0]}, {e['coord'][1]}]", "body", TEXT, x+82, y+10)

        # Status badge
        status = "SAFE  ✓" if safe else "BLOCKED  ✗"
        sc     = SUCCESS if safe else DANGER
        sw     = _fonts["h3"].size(status)[0]
        _rect((10,50,36) if safe else (50,10,10),
              x+w-sw-28, y+7, sw+22, 24, r=6)
        _blit(status, "h3", sc, x+w-sw-17, y+9)

        # Truth value pills
        def _pill(label, val, bx, by):
            vc  = SUCCESS if val else DANGER
            txt = f"{label}={val}"
            tw  = _fonts["small"].size(txt)[0]
            _rect((20,36,52), bx, by, tw+14, 20, r=5)
            _blit(txt, "small", vc, bx+7, by+3)
            return tw+20

        bx = x+12
        bx += _pill("inBounds", e["in_bounds"], bx, y+44)
        bx += _pill("!wall",    e["not_wall"],  bx, y+44)
        _pill("safe",           safe,           bx, y+44)

        y += rh + 8
        if y > _screen.get_height() - 60:
            break

_tab_logic._cache = []


# ─────────────────────────────────────────────────────────────────
# TAB: MATH
# ─────────────────────────────────────────────────────────────────
def _tab_math(x, y, w, agent_pos, target_pos, history, safe_moves, probs, cost):
    _blit("Mathematical Model", "h2", ACCENT, x, y);  y += 28

    dr = abs(agent_pos[0]-target_pos[0])
    dc = abs(agent_pos[1]-target_pos[1])
    l1 = _l1(agent_pos, target_pos)
    l2 = _l2(agent_pos, target_pos)
    steps = max(0, len(history)-1)

    def metric_box(title, formula, value, unit):
        nonlocal y
        _rect(PANEL, x, y, w, 76, r=8, border=BORDER)
        _blit(title,   "small", MUTED,  x+12, y+7)
        _blit(formula, "small", (60,100,140), x+12, y+24)
        vw = _fonts["num"].size(value)[0]
        _blit(value,   "num",   TEXT,   x+12, y+44)
        _blit(unit,    "body",  ACCENT, x+18+vw, y+50)
        y += 84

    metric_box("L2 NORM  (Euclidean Distance to Target)",
               f"||p - t||_2  =  sqrt({dr}^2 + {dc}^2)",
               f"{l2:.3f}", "cells")

    metric_box("L1 NORM  (Manhattan Distance to Target)",
               f"||p - t||_1  =  |{dr}| + |{dc}|",
               f"{l1}", "steps")

    metric_box("PATH COST  (Weighted Linear Combination)",
               f"C = {steps} x 1.0  +  {l2:.2f} x 1.5",
               f"{cost:.2f}", "total")

    # Softmax bars
    _blit("SOFTMAX PROBABILITY DISTRIBUTION", "small", MUTED, x, y);  y += 18
    _blit("P(move) = e^(-dist) / sum(e^(-dist))", "tiny", (60,90,120), x, y);  y += 20

    if safe_moves and probs:
        for (d, coord), p in zip(safe_moves, probs):
            _blit(f"{d:<6}", "body", TEXT, x, y)
            bx  = x + 70
            bw2 = w - 110
            _rect(BORDER, bx, y+4, bw2, 14, r=4)
            _rect(ACCENT,  bx, y+4, max(4, int(bw2*p)), 14, r=4)
            _blit(f"{p*100:.1f}%", "body", ACCENT, bx+bw2+6, y)
            y += 24
    else:
        _blit("Run the agent to see distributions.", "body", MUTED, x, y)


# ─────────────────────────────────────────────────────────────────
# TAB: GENETIC ALGORITHM
# ─────────────────────────────────────────────────────────────────
def _tab_ga(x, y, w, last_reason):
    _blit("Genetic Algorithm Optimizer", "h2", ACCENT, x, y);  y += 28

    params = [("Population",    "40"),
              ("Generations",   "50"),
              ("Chrom. Length", "10 genes"),
              ("Mutation Rate", "20%"),
              ("Selection",     "Top 50%"),
              ("Fitness",       "L1 + penalty")]

    half = (w - 10)//2
    for i in range(0, len(params), 2):
        for j in range(2):
            if i+j >= len(params): break
            k, v = params[i+j]
            bx = x + j*(half+10)
            _rect(PANEL, bx, y, half, 54, r=8, border=BORDER)
            _blit(k, "small", MUTED,  bx+10, y+7)
            _blit(v, "num",   ACCENT, bx+10, y+26)
        y += 62

    _blit("Algorithm Steps", "h3", TEXT, x, y);  y += 22

    steps = [
        ("1. Initialize", "40 random chromosomes of 10 direction genes"),
        ("2. Evaluate",   "fitness = L1_dist(end, target) + revisit_penalty(5000)"),
        ("3. Select",     "Keep best 50%  (lower fitness = better)"),
        ("4. Crossover",  "Single-point recombination between two parents"),
        ("5. Mutate",     "Each gene flips with probability 0.20"),
        ("6. Return",     "After 50 generations: return first move of best path"),
    ]
    for title, desc in steps:
        _rect(PANEL, x, y, w, 46, r=6, border=BORDER)
        _blit(title, "h3",   ACCENT, x+10, y+5)
        _blit(desc,  "small", MUTED, x+10, y+26, max_w=w-20)
        y += 54

    if last_reason:
        _rect((10,30,46), x, y, w, 44, r=8, border=BORDER)
        _blit("Last Decision:", "small", MUTED, x+12, y+6)
        _blit(last_reason,     "body",  TEXT,  x+12, y+24, max_w=w-24)


# ─────────────────────────────────────────────────────────────────
# TAB: LOG
# ─────────────────────────────────────────────────────────────────
def _tab_log(x, y, w, panel_bottom):
    _blit("Agent Decision Log", "h2", ACCENT, x, y);            y += 28
    _blit(f"Total: {len(_log_entries)} steps  |  scroll with mouse wheel",
          "tiny", MUTED, x, y);                                  y += 22

    if not _log_entries:
        _blit("No steps yet. Run the agent.", "body", MUTED, x, y)
        return

    row_h   = 70
    visible = list(reversed(_log_entries))
    max_vis = max(1, (panel_bottom - y - 4) // row_h)

    for entry in visible[_log_offset: _log_offset+max_vis]:
        if y + row_h > panel_bottom:
            break

        _rect(PANEL, x, y, w, row_h-4, r=8, border=BORDER)

        frm = entry.get("frm")
        to  = entry.get("to")
        fs  = f"[{frm[0]},{frm[1]}]" if frm else "[—]"
        ts  = f"[{to[0]},{to[1]}]"   if to  else "[—]"

        _blit(f"Step {entry['step']}", "h3",   MUTED,  x+12, y+7)
        cost_s = f"Cost: {entry['cost']}"
        cw     = _fonts["body"].size(cost_s)[0]
        _blit(cost_s, "body", ACCENT, x+w-cw-12, y+9)

        move_s = f"{fs}  ->  {ts}"
        _blit(move_s, "body", TEXT, x+12, y+30)
        _blit(entry.get("reason", "—"), "small", MUTED, x+12, y+50, max_w=w-24)

        y += row_h