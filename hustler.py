#!/usr/bin/env python3
import rumps
import json
import os
import csv
from datetime import datetime, date, timedelta

GOAL = 5000
GOAL_DATE = date(2026, 7, 12)
START_DATE = date(2026, 7, 1)
CURRENCY = "$"
QUOTE_ROTATION_SECONDS = 300

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "hustler_data.json")
ASSET_DIR = os.path.join(SCRIPT_DIR, "assets")
MENU_BAR_ICON_FILE = os.path.join(ASSET_DIR, "hustler_menubar_icon.png")
APP_ICON_FILE = os.path.join(ASSET_DIR, "hustler_app_icon.png")
EXPORT_DIR = os.path.expanduser("~/Downloads")

EXPENSE_CATEGORIES = ["Food", "Transport", "Bills", "Shopping", "Health", "Entertainment", "Other"]

QUOTES = [
    "Every dollar counts. Keep stacking.",
    "Revenue is king. Expenses are the court.",
    "Small gains compound into empires.",
    "Track the money. Find the money.",
    "Your future self is watching.",
    "Grind now. Count later.",
    "Revenue today, freedom tomorrow.",
    "Protect the profit.",
    "Stay focused. Stay funded.",
    "One more dollar closer.",
    "Build the habit. The balance follows.",
    "Make the next move profitable.",
    "Discipline pays better than luck.",
    "Small wins are still wins. Log them.",
    "The goal gets closer when you move.",
    "Turn effort into evidence.",
    "Cash flow rewards consistency.",
    "Do the work before the mood arrives.",
    "Keep your money pointed at the goal.",
    "A clean ledger sharpens the mission.",
    "Progress likes people who show up.",
    "Earn with focus. Spend with intent.",
    "Do not drift. Decide.",
    "Win the day in dollars and discipline.",
    "Your numbers tell the truth. Use them.",
    "Stack revenue. Cut noise.",
    "The scoreboard only changes when you act.",
    "Make today hard to ignore.",
    "One focused hour can change the week.",
    "Momentum is built, not found.",
    "Every entry is a vote for control.",
    "Keep the goal louder than the excuses.",
    "A strong day starts with a clear target.",
    "Profit is the proof of priorities.",
    "Do the simple thing with force.",
    "Earn first. Celebrate later.",
    "Make the goal boringly inevitable.",
    "Control the inputs. Respect the output.",
    "No zero days when the goal matters.",
    "Turn pressure into production.",
    "Track it so you can attack it.",
    "Better choices compound quietly.",
    "The next dollar needs a reason.",
    "Focus beats frenzy.",
    "You do not need perfect. You need posted.",
    "Progress is a receipt, not a feeling.",
    "Protect your margin like your time.",
    "Move with purpose. Count with honesty.",
    "Less waste. More runway.",
    "Your plan needs action, not applause.",
    "Make money decisions before money decides.",
    "The target is clear. Keep walking.",
    "Today is a deposit into the future.",
    "Your discipline is your unfair advantage.",
    "The quiet work becomes loud results.",
    "Stay patient. Stay precise.",
    "Make one move that pays.",
    "Do not negotiate with distraction.",
    "Revenue solves what wishing cannot.",
    "The habit is the engine.",
    "You are closer when you measure.",
    "Cut leaks. Build streams.",
    "Keep your ambition on a schedule.",
    "The goal does not need drama. It needs work.",
    "Turn a small action into a logged win.",
    "Consistency makes confidence believable.",
    "Do the profitable thing next.",
    "Every saved dollar stayed loyal.",
    "Spend slower than you earn.",
    "Your future is funded by today's choices.",
    "Show up before the result does.",
    "Keep receipts. Keep standards.",
    "Win quietly. Track loudly.",
    "Make the numbers respect your effort.",
    "A focused day beats a busy blur.",
    "Build wealth one decision at a time.",
    "Do not wait for easy. Start with clear.",
    "A dollar tracked is a dollar understood.",
    "Your goal needs attention every day.",
    "Make the work visible.",
    "Strong habits survive weak moods.",
    "Earn more. Waste less. Repeat.",
    "Let the data sharpen the hustle.",
    "Choose progress over comfort.",
    "The best time to log it is now.",
    "Make your ambition accountable.",
    "You can only improve what you face.",
    "The next entry can change the pace.",
    "Stay lean. Stay hungry. Stay honest.",
    "Your money should have a mission.",
    "Build proof, not pressure.",
    "One clean choice can save the day.",
    "Keep moving until the numbers move.",
    "The goal is won in ordinary moments.",
    "Let consistency do the heavy lifting.",
    "Make the month proud of today.",
    "Focus is a financial skill.",
    "Small discipline becomes big distance.",
    "Stop guessing. Start tracking.",
    "Give every dollar a job.",
    "Do less nonsense. Keep more money.",
    "A clear target makes sacrifice easier.",
    "The grind counts when you count it.",
    "Your standards show up in your spending.",
    "Push the number forward.",
    "Stay committed after the excitement fades.",
    "Make today add up.",
    "Profit loves patience.",
    "Every smart choice buys freedom.",
    "Keep stacking until the goal looks small.",
]

ACHIEVEMENTS = {
    "first_dollar": {"name": "First Dollar", "emoji": "💵", "threshold": 1},
    "club_500": {"name": "$500 Club", "emoji": "🔥", "threshold": 500},
    "club_1k": {"name": "$1k Club", "emoji": "💎", "threshold": 1000},
    "halfway": {"name": "Halfway There", "emoji": "⚡", "threshold": GOAL / 2},
    "goal_crusher": {"name": "Goal Crusher", "emoji": "🏆", "threshold": GOAL},
    "streak_7": {"name": "7-Day Streak", "emoji": "🔥", "threshold": -1},
    "streak_30": {"name": "30-Day Streak", "emoji": "🌋", "threshold": -1},
}

MILESTONES = [0.25, 0.50, 0.75, 1.0]


def load_data():
    default = {
        "revenue": [],
        "expenses": [],
        "achievements": [],
        "milestones": [],
        "last_reset": None,
        "daily_log": {},
    }
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        for key in default:
            if key not in data:
                data[key] = default[key]
        if data.get("revenue") or data.get("expenses"):
            return data

    save_data(default)
    return default


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def font(size, bold=False):
    from PIL import ImageFont

    candidates = [
        "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
        "/System/Library/Fonts/SFNSRounded.ttf" if bold else "/System/Library/Fonts/SFNSMono.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def revenue_total(data):
    return sum(e["amount"] for e in data.get("revenue", []))


def expense_total(data):
    return sum(e["amount"] for e in data.get("expenses", []))


def net_profit(data):
    return revenue_total(data) - expense_total(data)


def today_revenue(data):
    today = date.today().isoformat()
    return sum(e["amount"] for e in data.get("revenue", []) if e["timestamp"].startswith(today))


def today_expenses(data):
    today = date.today().isoformat()
    return sum(e["amount"] for e in data.get("expenses", []) if e["timestamp"].startswith(today))


def week_revenue(data):
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    return sum(e["amount"] for e in data.get("revenue", []) if e["timestamp"][:10] >= week_ago)


def month_revenue(data):
    month_start = date.today().replace(day=1).isoformat()
    return sum(e["amount"] for e in data.get("revenue", []) if e["timestamp"][:10] >= month_start)


def days_left():
    return max((GOAL_DATE - date.today()).days, 0)


def daily_target(data):
    dl = days_left()
    if dl <= 0:
        return 0
    remaining = max(GOAL - net_profit(data), 0)
    return remaining / dl


def goal_progress(total):
    if GOAL <= 0:
        return 0
    return max(0, min(total / GOAL, 1.0))


def pace_status(data):
    today = date.today()
    total_days = max((GOAL_DATE - START_DATE).days + 1, 1)
    elapsed_days = max((today - START_DATE).days + 1, 1)
    elapsed_ratio = min(elapsed_days / total_days, 1.0)
    expected = GOAL * elapsed_ratio
    net = net_profit(data)
    delta = net - expected
    return {
        "label": "Ahead" if delta >= 0 else "Behind",
        "delta": delta,
        "avg_daily": net / elapsed_days,
        "needed_daily": daily_target(data),
        "elapsed_days": elapsed_days,
        "total_days": total_days,
    }


def streak(data):
    s = 0
    today = date.today()
    for i in range(365):
        day = today - timedelta(days=i)
        day_str = day.isoformat()
        if any(e["timestamp"].startswith(day_str) for e in data.get("revenue", [])):
            s += 1
        else:
            break
    return s


def best_streak(data):
    s = 0
    best = 0
    today = date.today()
    for i in range(365):
        day = today - timedelta(days=i)
        day_str = day.isoformat()
        if any(e["timestamp"].startswith(day_str) for e in data.get("revenue", [])):
            s += 1
            best = max(best, s)
        else:
            s = 0
    return best


def expense_by_category(data):
    cats = {}
    for e in data.get("expenses", []):
        cat = e.get("category", "Other")
        cats[cat] = cats.get(cat, 0) + e["amount"]
    return dict(sorted(cats.items(), key=lambda x: -x[1]))


def savings_rate(data):
    rev = revenue_total(data)
    if rev == 0:
        return 0
    return ((rev - expense_total(data)) / rev) * 100


def progress_bar(total):
    pct = goal_progress(total)
    filled = round(pct * 20)
    return "█" * filled + "░" * (20 - filled)


def pct_label(total):
    return f"{int((total / GOAL) * 100)}%"


def fmt(amount):
    if abs(amount) >= 1000:
        return f"{CURRENCY}{amount/1000:.1f}k"
    return f"{CURRENCY}{amount:,.0f}"


def recent_entries(data, limit=5):
    entries = []
    for entry_type in ("revenue", "expenses"):
        for idx, entry in enumerate(data.get(entry_type, [])):
            entries.append((entry.get("timestamp", ""), entry_type, idx, entry))
    entries.sort(key=lambda item: item[0], reverse=True)
    return entries[:limit]


def entry_summary(entry_type, entry):
    prefix = "+" if entry_type == "revenue" else "-"
    desc = entry.get("description", "No description")
    day = entry.get("timestamp", "")[:10] or "unknown"
    return f"{prefix}{CURRENCY}{entry['amount']:,.2f}  {desc}  ({day})"


def check_achievements(data):
    total = net_profit(data)
    earned = data.get("achievements", [])
    new_achs = []
    s = streak(data)

    for key, ach in ACHIEVEMENTS.items():
        if key not in earned:
            if key == "streak_7" and s >= 7:
                earned.append(key)
                new_achs.append(ach)
            elif key == "streak_30" and s >= 30:
                earned.append(key)
                new_achs.append(ach)
            elif ach["threshold"] > 0 and total >= ach["threshold"]:
                earned.append(key)
                new_achs.append(ach)

    data["achievements"] = earned
    return new_achs


def check_milestones(data):
    total = net_profit(data)
    pct = total / GOAL
    reached = data.get("milestones", [])
    new_miles = []
    for m in MILESTONES:
        if pct >= m and m not in reached:
            reached.append(m)
            new_miles.append(m)
    data["milestones"] = reached
    return new_miles


def export_csv(data):
    path = os.path.join(EXPORT_DIR, "hustler_export.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Amount", "Description", "Category", "Date"])
        for e in data.get("revenue", []):
            writer.writerow(["Revenue", e["amount"], e.get("description", ""), "", e["timestamp"][:10]])
        for e in data.get("expenses", []):
            writer.writerow(["Expense", e["amount"], e.get("description", ""), e.get("category", "Other"), e["timestamp"][:10]])
    return path


def ensure_icon_assets():
    if os.path.exists(MENU_BAR_ICON_FILE) and os.path.exists(APP_ICON_FILE):
        return MENU_BAR_ICON_FILE

    from PIL import Image, ImageDraw

    os.makedirs(ASSET_DIR, exist_ok=True)

    menu = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(menu)
    black = (0, 0, 0, 255)
    draw.rounded_rectangle((8, 8, 56, 56), radius=12, outline=black, width=5)
    draw.line((18, 43, 30, 31, 38, 36, 48, 20), fill=black, width=5, joint="curve")
    draw.ellipse((15, 40, 21, 46), fill=black)
    draw.ellipse((27, 28, 33, 34), fill=black)
    draw.ellipse((35, 33, 41, 39), fill=black)
    draw.ellipse((45, 17, 51, 23), fill=black)
    menu.save(MENU_BAR_ICON_FILE, "PNG")

    size = 512
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    for y in range(size):
        t = y / (size - 1)
        r = int(18 + 12 * t)
        g = int(22 + 18 * t)
        b = int(30 + 26 * t)
        draw.line((0, y, size, y), fill=(r, g, b, 255))

    draw.rounded_rectangle((34, 34, 478, 478), radius=96, outline=(255, 255, 255, 32), width=3)
    draw.rounded_rectangle((86, 318, 142, 404), radius=22, fill=(36, 201, 151, 255))
    draw.rounded_rectangle((184, 262, 240, 404), radius=22, fill=(76, 201, 240, 255))
    draw.rounded_rectangle((282, 196, 338, 404), radius=22, fill=(242, 184, 75, 255))
    draw.rounded_rectangle((380, 126, 436, 404), radius=22, fill=(255, 92, 122, 255))
    draw.line((104, 280, 212, 226, 306, 244, 414, 112), fill=(248, 250, 252, 255), width=24, joint="curve")
    for x, y in [(104, 280), (212, 226), (306, 244), (414, 112)]:
        draw.ellipse((x - 18, y - 18, x + 18, y + 18), fill=(248, 250, 252, 255))
    draw.line((88, 424, 432, 424), fill=(255, 255, 255, 42), width=8)
    icon.save(APP_ICON_FILE, "PNG")
    return MENU_BAR_ICON_FILE


def hide_dock_icon():
    try:
        from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
        NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    except Exception:
        pass


def configure_macos_app():
    try:
        from AppKit import NSApp, NSApplicationActivationPolicyAccessory, NSImage
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        icon = NSImage.alloc().initWithContentsOfFile_(APP_ICON_FILE)
        if icon:
            NSApp.setApplicationIconImage_(icon)
    except Exception:
        pass


def export_image(data):
    from PIL import Image, ImageDraw

    W, H = 1200, 1400
    BG = "#101114"
    PANEL = "#181a20"
    PANEL_2 = "#20232b"
    LINE = "#2d313a"
    TEXT = "#f8fafc"
    MUTED = "#9ca3af"
    GREEN = "#20c997"
    RED = "#ff5c7a"
    GOLD = "#f2b84b"
    CYAN = "#4cc9f0"

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    def text_right(x, y, text, font_obj, fill):
        draw.text((x - draw.textlength(text, font=font_obj), y), text, fill=fill, font=font_obj)

    def fit_text(x, y, text, max_width, size, fill, bold=False):
        current = size
        font_obj = font(current, bold=bold)
        while current > 18 and draw.textlength(text, font=font_obj) > max_width:
            current -= 2
            font_obj = font(current, bold=bold)
        draw.text((x, y), text, fill=fill, font=font_obj)

    def card(x1, y1, x2, y2, fill=PANEL):
        draw.rounded_rectangle((x1, y1, x2, y2), radius=24, fill=fill)

    def metric_card(x, y, w, label, value, color):
        card(x, y, x + w, y + 150, PANEL_2)
        draw.rounded_rectangle((x + 26, y + 26, x + 34, y + 74), radius=4, fill=color)
        draw.text((x + 52, y + 26), label.upper(), fill=MUTED, font=font(20))
        fit_text(x + 52, y + 68, value, w - 80, 46, TEXT, bold=True)

    for i in range(0, W, 46):
        draw.line((i, 0, i - 240, H), fill="#14161a", width=1)

    net = net_profit(data)
    rev = revenue_total(data)
    exp = expense_total(data)
    s = streak(data)
    bs = best_streak(data)
    rate = savings_rate(data)
    pct = goal_progress(net)
    pace = pace_status(data)
    pace_color = GREEN if pace["delta"] >= 0 else RED
    remaining = max(GOAL - net, 0)
    quote = QUOTES[date.today().day % len(QUOTES)]

    pad = 64
    draw.text((pad, 70), "HUSTLER", fill=TEXT, font=font(34, bold=True))
    text_right(W - pad, 76, date.today().strftime("%b %d, %Y"), font(22), MUTED)
    draw.text((pad, 112), quote, fill=MUTED, font=font(23))

    card(pad, 180, W - pad, 500)
    draw.text((pad + 46, 230), "NET PROFIT", fill=MUTED, font=font(22))
    fit_text(pad + 46, 270, fmt(net), 610, 96, TEXT, bold=True)
    draw.text((pad + 50, 390), f"{fmt(remaining)} left to hit {fmt(GOAL)}", fill=MUTED, font=font(28))

    cx, cy, r = W - pad - 170, 338, 112
    draw.arc((cx - r, cy - r, cx + r, cy + r), 0, 360, fill=LINE, width=28)
    draw.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + int(360 * pct), fill=GREEN if pct >= 1 else GOLD, width=28)
    pct_text = f"{int(pct * 100)}%"
    pct_font = font(46, bold=True)
    draw.text((cx - draw.textlength(pct_text, font=pct_font) / 2, cy - 30), pct_text, fill=TEXT, font=pct_font)
    complete_text = "complete"
    complete_font = font(18)
    draw.text((cx - draw.textlength(complete_text, font=complete_font) / 2, cy + 28), complete_text, fill=MUTED, font=complete_font)

    y = 540
    gap = 22
    w = (W - pad * 2 - gap * 2) // 3
    metric_card(pad, y, w, "Revenue", fmt(rev), GREEN)
    metric_card(pad + w + gap, y, w, "Expenses", fmt(exp), RED)
    metric_card(pad + (w + gap) * 2, y, w, "Savings", f"{rate:.0f}%", CYAN)

    y = 730
    card(pad, y, W - pad, y + 230)
    draw.text((pad + 34, y + 32), "GOAL PACE", fill=MUTED, font=font(22))
    draw.text((pad + 34, y + 72), pace["label"], fill=pace_color, font=font(50, bold=True))
    draw.text((pad + 34, y + 142), f"{fmt(abs(pace['delta']))} vs plan", fill=TEXT, font=font(28))
    text_right(W - pad - 34, y + 70, f"{fmt(pace['needed_daily'])}/day", font(42, bold=True), TEXT)
    text_right(W - pad - 34, y + 126, "needed from here", font(22), MUTED)
    draw.line((pad + 34, y + 184, W - pad - 34, y + 184), fill=LINE, width=2)
    draw.text((pad + 34, y + 196), f"Average: {fmt(pace['avg_daily'])}/day", fill=MUTED, font=font(22))
    text_right(W - pad - 34, y + 196, f"{pace['elapsed_days']} of {pace['total_days']} days", font(22), MUTED)

    y = 1000
    card(pad, y, W - pad, y + 250)
    draw.text((pad + 34, y + 30), "MOMENTUM", fill=MUTED, font=font(22))
    rows = [
        ("Today", f"+{CURRENCY}{today_revenue(data):,.2f}   -{CURRENCY}{today_expenses(data):,.2f}", GREEN),
        ("This week", fmt(week_revenue(data)), GOLD),
        ("This month", fmt(month_revenue(data)), CYAN),
        ("Streak", f"{s} day{'s' if s != 1 else ''}  |  best {bs}", RED if s == 0 else GREEN),
    ]
    for i, (label, value, color) in enumerate(rows):
        ry = y + 78 + i * 42
        draw.rounded_rectangle((pad + 34, ry + 5, pad + 46, ry + 17), radius=6, fill=color)
        draw.text((pad + 62, ry), label, fill=MUTED, font=font(24))
        text_right(W - pad - 34, ry, value, font(24, bold=True), TEXT)

    cats = list(expense_by_category(data).items())[:4]
    y = 1286
    if cats:
        draw.text((pad, y), "Top spending", fill=MUTED, font=font(18))
        x = pad + 140
        max_spend = max(total for _, total in cats) or 1
        for cat, total in cats:
            bar_w = int(170 * total / max_spend)
            draw.rounded_rectangle((x, y + 6, x + 170, y + 18), radius=6, fill=LINE)
            draw.rounded_rectangle((x, y + 6, x + bar_w, y + 18), radius=6, fill=RED)
            draw.text((x, y + 28), cat[:12], fill=MUTED, font=font(15))
            x += 205
    else:
        draw.text((pad, y), "No expenses logged yet", fill=MUTED, font=font(18))

    draw.text((pad, H - 58), "Built from local Hustler data", fill=LINE, font=font(18))
    text_right(W - pad, H - 58, "hustler", font(18, bold=True), LINE)

    path = os.path.join(EXPORT_DIR, "hustler_progress.png")
    img.save(path, "PNG")
    return path


class Hustler(rumps.App):
    def __init__(self):
        hide_dock_icon()
        super().__init__("HUSTLER", icon=ensure_icon_assets(), template=True, quit_button=None)
        configure_macos_app()
        self.data = load_data()
        self._quote_idx = 0
        self._build_menu()
        self._update_title()
        rumps.timer(QUOTE_ROTATION_SECONDS)(self._cycle_title)

    def _cycle_title(self, _):
        self._quote_idx = (self._quote_idx + 1) % len(QUOTES)
        self._update_title()

    def _update_title(self):
        net = net_profit(self.data)
        quote = QUOTES[self._quote_idx]
        self.title = f"{fmt(net)} | {pct_label(net)}  |  {quote}"

    def _build_menu(self):
        self.menu.clear()
        net = net_profit(self.data)
        today_rev = today_revenue(self.data)
        today_exp = today_expenses(self.data)
        wk = week_revenue(self.data)
        mo = month_revenue(self.data)
        bar = progress_bar(net)
        pct = pct_label(net)
        target = daily_target(self.data)
        pace = pace_status(self.data)
        s = streak(self.data)
        best = best_streak(self.data)
        rate = savings_rate(self.data)
        cats = expense_by_category(self.data)

        self.menu.add(rumps.MenuItem("💰 Hustler"))
        self.menu.add(rumps.separator)

        self.menu.add(rumps.MenuItem(f"💵 Today: +${today_rev:,.2f}  -${today_exp:,.2f}"))
        self.menu.add(rumps.MenuItem(f"📅 This Week: ${wk:,.2f}"))
        self.menu.add(rumps.MenuItem(f"📆 This Month: ${mo:,.2f}"))
        self.menu.add(rumps.separator)

        self.menu.add(rumps.MenuItem(f"Progress:  {bar} {pct}"))
        self.menu.add(rumps.MenuItem(f"🎯 Daily Target: ${target:,.2f}"))
        self.menu.add(rumps.MenuItem(f"📈 Pace: {pace['label']} by {fmt(abs(pace['delta']))}  •  Avg {fmt(pace['avg_daily'])}/day"))
        self.menu.add(rumps.MenuItem(f"🔥 Streak: {s} day{'s' if s != 1 else ''}  •  Best: {best}"))
        self.menu.add(rumps.MenuItem(f"💰 Savings Rate: {rate:.0f}%"))
        self.menu.add(rumps.separator)

        self.menu.add(rumps.MenuItem("⚡ Quick Add"))
        for amount in [25, 50, 100, 250, 500]:
            self.menu.add(rumps.MenuItem(f"  +${amount}", callback=self._quick_add))
        self.menu.add(rumps.separator)

        self.menu.add(rumps.MenuItem("➕ Add Revenue", callback=self.add_revenue))
        self.menu.add(rumps.MenuItem("➖ Add Expense", callback=self.add_expense))
        self.menu.add(rumps.separator)

        earned = self.data.get("achievements", [])
        if earned:
            self.menu.add(rumps.MenuItem("🏅 Achievements"))
            for key in earned:
                if key in ACHIEVEMENTS:
                    ach = ACHIEVEMENTS[key]
                    self.menu.add(rumps.MenuItem(f"  {ach['emoji']} {ach['name']}"))
            self.menu.add(rumps.separator)

        reached = self.data.get("milestones", [])
        if reached:
            labels = {0.25: "25%", 0.50: "50%", 0.75: "75%", 1.0: "100%"}
            self.menu.add(rumps.MenuItem("🎯 Milestones"))
            for m in sorted(reached):
                self.menu.add(rumps.MenuItem(f"  ✅ {labels.get(m, f'{int(m*100)}%')}"))
            self.menu.add(rumps.separator)

        if cats:
            self.menu.add(rumps.MenuItem("📊 Spending Breakdown"))
            for cat, total in list(cats.items())[:5]:
                self.menu.add(rumps.MenuItem(f"  {cat}: ${total:,.2f}"))
            self.menu.add(rumps.separator)

        recent = recent_entries(self.data, limit=4)
        if recent:
            self.menu.add(rumps.MenuItem("🧾 Recent Activity"))
            for _, entry_type, _, entry in recent:
                self.menu.add(rumps.MenuItem(f"  {entry_summary(entry_type, entry)}"))
            self.menu.add(rumps.separator)

        self.menu.add(rumps.MenuItem("⚙️ Settings"))
        self.menu.add(rumps.MenuItem("  ↩️ Undo Last Entry", callback=self._undo_last_entry))
        self.menu.add(rumps.MenuItem("  📤 Export CSV", callback=self._export_csv))
        self.menu.add(rumps.MenuItem("  🖼️ Export Image", callback=self._export_image))
        self.menu.add(rumps.MenuItem("  🔄 Reset Month", callback=self._reset_month))
        self.menu.add(rumps.separator)

        self.menu.add(rumps.MenuItem("Quit", callback=self.quit_app))

    def _quick_add(self, sender):
        amount = float(sender.title.replace("+$", "").replace(",", ""))
        self._record_entry("revenue", amount, "Quick add")

    def _record_entry(self, entry_type, amount, description, category=None):
        entry = {
            "amount": amount,
            "description": description or "No description",
            "timestamp": datetime.now().isoformat(),
        }
        if entry_type == "expenses" and category:
            entry["category"] = category
        self.data[entry_type].append(entry)

        if entry_type == "revenue":
            self._mark_revenue_day()

        new_achs = check_achievements(self.data)
        new_miles = check_milestones(self.data)
        save_data(self.data)

        self._update_title()
        self._build_menu()
        self._notify_entry(entry_type, entry)
        self._notify_awards(new_achs, new_miles)

    def _mark_revenue_day(self):
        today_str = date.today().isoformat()
        self.data.setdefault("daily_log", {})
        self.data["daily_log"][today_str] = True

    def _notify_entry(self, entry_type, entry):
        net = net_profit(self.data)
        emoji = "💰" if entry_type == "revenue" else "🛒"
        sign = "+" if entry_type == "revenue" else "-"
        rumps.notification(
            title=f"{emoji} {sign}${entry['amount']:,.2f} added!",
            subtitle=entry.get("description", "No description"),
            message=f"Net: ${net:,.2f}  •  {pct_label(net)} to goal",
            sound=False,
        )

    def _notify_awards(self, new_achs, new_miles):
        for ach in new_achs:
            rumps.notification(
                title="🏅 Achievement Unlocked!",
                subtitle=f"{ach['emoji']} {ach['name']}",
                message="",
                sound=True,
            )

        for m in new_miles:
            rumps.notification(
                title="🎯 Milestone Reached!",
                subtitle=f"{int(m*100)}% of your goal!",
                message="Keep going!",
                sound=True,
            )

    def _add_entry(self, title, entry_type, category=None):
        amount_resp = rumps.Window(
            message="How much?",
            title=title,
            default_text="",
            ok="Next",
            cancel="Cancel",
            dimensions=(200, 24),
        ).run()

        if not amount_resp.clicked or not amount_resp.text.strip():
            return

        try:
            amount = float(amount_resp.text.strip().replace("$", "").replace(",", ""))
        except ValueError:
            rumps.alert(title="Invalid amount", message="Enter a number like 50 or 250.50")
            return

        desc_resp = rumps.Window(
            message="What was it for?",
            title=title,
            default_text="",
            ok="Save",
            cancel="Cancel",
            dimensions=(200, 24),
        ).run()

        if not desc_resp.clicked:
            return

        self._record_entry(entry_type, amount, desc_resp.text.strip() or "No description", category)

    def add_revenue(self, _):
        self._add_entry("➕ Add Revenue", "revenue")

    def add_expense(self, _):
        cat_items = "\n".join([f"  {i+1}. {c}" for i, c in enumerate(EXPENSE_CATEGORIES)])
        category_resp = rumps.Window(
            message=f"Pick a category:\n{cat_items}\n\nType the number or name:",
            title="Add Expense",
            default_text="",
            ok="Next",
            cancel="Cancel",
            dimensions=(200, 24),
        ).run()

        if not category_resp.clicked:
            return

        cat_input = category_resp.text.strip()
        try:
            idx = int(cat_input) - 1
            cat = EXPENSE_CATEGORIES[idx] if 0 <= idx < len(EXPENSE_CATEGORIES) else "Other"
        except (ValueError, IndexError):
            cat = cat_input if cat_input in EXPENSE_CATEGORIES else "Other"

        self._add_entry("➖ Add Expense", "expenses", category=cat)

    def _export_csv(self, _):
        path = export_csv(self.data)
        rumps.notification(
            title="📤 Exported!",
            subtitle="Saved to Downloads",
            message=path,
            sound=False,
        )

    def _export_image(self, _):
        path = export_image(self.data)
        rumps.notification(
            title="🖼️ Progress Card!",
            subtitle="Saved to Downloads",
            message=path,
            sound=False,
        )

    def _undo_last_entry(self, _):
        recent = recent_entries(self.data, limit=1)
        if not recent:
            rumps.alert(title="Nothing to undo", message="No revenue or expense entries exist yet.")
            return

        _, entry_type, idx, entry = recent[0]
        resp = rumps.alert(
            title="↩️ Undo Last Entry?",
            message=entry_summary(entry_type, entry),
            ok="Undo",
            cancel="Cancel",
        )
        if resp != 1:
            return

        del self.data[entry_type][idx]
        save_data(self.data)
        self._update_title()
        self._build_menu()
        rumps.notification(
            title="↩️ Entry removed",
            subtitle=entry_summary(entry_type, entry),
            message="",
            sound=False,
        )

    def _reset_month(self, _):
        resp = rumps.alert(
            title="🔄 Reset Month?",
            message="Clear all revenue and expenses. Achievements kept. Sure?",
            ok="Reset",
            cancel="Cancel",
        )
        if resp == 1:
            self.data["revenue"] = []
            self.data["expenses"] = []
            self.data["milestones"] = []
            self.data["daily_log"] = {}
            self.data["last_reset"] = datetime.now().isoformat()
            save_data(self.data)
            self._update_title()
            self._build_menu()
            rumps.notification(title="🔄 Reset!", subtitle="Fresh start!", message="", sound=False)

    def quit_app(self, _):
        rumps.quit_application()


if __name__ == "__main__":
    Hustler().run()
