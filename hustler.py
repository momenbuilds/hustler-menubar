#!/usr/bin/env python3
import rumps
import json
import os
import csv
import math
import sys
import webbrowser
from urllib.error import URLError
from urllib.request import Request, urlopen
from datetime import datetime, date, timedelta

APP_VERSION = "1.2.0"
RELEASES_API = "https://api.github.com/repos/momenbuilds/hustler-menubar/releases/latest"
DEFAULT_GOAL = 5000
DEFAULT_CURRENCY = "$"
DEFAULT_GOAL_DAYS = 30
QUOTE_ROTATION_SECONDS = 300

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IS_BUNDLED = getattr(sys, "frozen", False)
APP_DATA_DIR = os.path.expanduser("~/Library/Application Support/Hustler") if IS_BUNDLED else SCRIPT_DIR
DATA_FILE = os.environ.get("HUSTLER_DATA_FILE", os.path.join(APP_DATA_DIR, "hustler_data.json"))
ASSET_ROOT = getattr(sys, "_MEIPASS", SCRIPT_DIR) if IS_BUNDLED else SCRIPT_DIR
ASSET_DIR = os.path.join(ASSET_ROOT, "assets")
MENU_BAR_ICON_FILE = os.path.join(ASSET_DIR, "hustler_menubar_icon.png")
APP_ICON_FILE = os.path.join(ASSET_DIR, "hustler_app_icon.png")
EXPORT_DIR = os.environ.get("HUSTLER_EXPORT_DIR", os.path.expanduser("~/Downloads"))

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
    "club_500": {"name": "500 Club", "emoji": "🔥", "threshold": 500},
    "club_1k": {"name": "1K Club", "emoji": "💎", "threshold": 1000},
    "halfway": {"name": "Halfway There", "emoji": "⚡", "threshold": None},
    "goal_crusher": {"name": "Goal Crusher", "emoji": "🏆", "threshold": None},
    "streak_7": {"name": "7-Day Streak", "emoji": "🔥", "threshold": -1},
    "streak_30": {"name": "30-Day Streak", "emoji": "🌋", "threshold": -1},
}

MILESTONES = [0.25, 0.50, 0.75, 1.0]


def default_settings():
    today = date.today()
    target_date = today + timedelta(days=DEFAULT_GOAL_DAYS)
    return {
        "goal": DEFAULT_GOAL,
        "currency": DEFAULT_CURRENCY,
        "start_date": today.isoformat(),
        "goal_date": target_date.isoformat(),
        "onboarded": False,
        "goals": [
            {
                "id": "main",
                "name": "Main Goal",
                "target": DEFAULT_GOAL,
                "start_date": today.isoformat(),
                "target_date": target_date.isoformat(),
            }
        ],
        "active_goal_id": "main",
    }


def version_key(version):
    return tuple(int(part) for part in version.lstrip("v").split(".") if part.isdigit())


def latest_release():
    request = Request(RELEASES_API, headers={"Accept": "application/vnd.github+json", "User-Agent": "Hustler-Menu"})
    try:
        with urlopen(request, timeout=2) as response:
            release = json.load(response)
    except (OSError, URLError, json.JSONDecodeError):
        return None

    tag = release.get("tag_name", "")
    if not tag or version_key(tag) <= version_key(APP_VERSION):
        return None
    asset_url = next(
        (asset.get("browser_download_url") for asset in release.get("assets", []) if asset.get("name") == "Hustler-macOS.zip"),
        release.get("html_url"),
    )
    return {"version": tag.lstrip("v"), "url": asset_url or release.get("html_url")}


def load_data():
    default = {
        "revenue": [],
        "expenses": [],
        "achievements": [],
        "milestones": [],
        "last_reset": None,
        "daily_log": {},
        "budgets": {},
        "recurring": [],
        "settings": default_settings(),
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            data = default
        for key in default:
            if key not in data:
                data[key] = default[key]
        settings = data.get("settings")
        if not isinstance(settings, dict):
            settings = {}
            data["settings"] = settings
        for key, value in default["settings"].items():
            if key not in {"goals", "active_goal_id"}:
                settings.setdefault(key, value)
        normalize_goal_settings(settings)
        active_id = settings["active_goal_id"]
        for entry_type in ("revenue", "expenses"):
            for entry in data.get(entry_type, []):
                entry.setdefault("goal_id", active_id)
        return data

    save_data(default)
    return default


def save_data(data):
    directory = os.path.dirname(DATA_FILE)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def settings(data):
    return data["settings"]


def normalize_goal_settings(config):
    goals = config.get("goals")
    if not isinstance(goals, list) or not goals:
        goals = [
            {
                "id": "main",
                "name": "Main Goal",
                "target": config.get("goal", DEFAULT_GOAL),
                "start_date": config.get("start_date", date.today().isoformat()),
                "target_date": config.get("goal_date", (date.today() + timedelta(days=DEFAULT_GOAL_DAYS)).isoformat()),
            }
        ]
        config["goals"] = goals

    valid_goals = []
    for index, goal in enumerate(goals, start=1):
        if not isinstance(goal, dict):
            continue
        goal.setdefault("id", f"goal-{index}")
        goal.setdefault("name", f"Goal {index}")
        goal.setdefault("target", DEFAULT_GOAL)
        goal.setdefault("start_date", date.today().isoformat())
        goal.setdefault("target_date", (date.today() + timedelta(days=DEFAULT_GOAL_DAYS)).isoformat())
        valid_goals.append(goal)
    config["goals"] = valid_goals or goals

    active_id = config.get("active_goal_id")
    if not any(goal["id"] == active_id for goal in config["goals"]):
        config["active_goal_id"] = config["goals"][0]["id"]
    sync_legacy_goal_settings(config)


def active_goal(data):
    config = settings(data)
    normalize_goal_settings(config)
    active_id = config["active_goal_id"]
    return next(goal for goal in config["goals"] if goal["id"] == active_id)


def sync_legacy_goal_settings(config):
    active_id = config.get("active_goal_id")
    active = next((goal for goal in config.get("goals", []) if goal.get("id") == active_id), None)
    if not active:
        return
    config["goal"] = active["target"]
    config["start_date"] = active["start_date"]
    config["goal_date"] = active["target_date"]


def goal_amount(data):
    try:
        return max(float(active_goal(data)["target"]), 0)
    except (KeyError, TypeError, ValueError):
        return DEFAULT_GOAL


def currency(data=None):
    if data is None:
        return DEFAULT_CURRENCY
    value = str(settings(data).get("currency", DEFAULT_CURRENCY)).strip()
    return value or DEFAULT_CURRENCY


def configured_date(data, key, fallback):
    try:
        return date.fromisoformat(settings(data)[key])
    except (KeyError, TypeError, ValueError):
        return fallback


def start_date(data):
    return configured_date({"settings": active_goal(data)}, "start_date", date.today())


def goal_date(data):
    return configured_date({"settings": active_goal(data)}, "target_date", date.today() + timedelta(days=DEFAULT_GOAL_DAYS))


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
    return sum(e["amount"] for e in active_entries(data, "revenue"))


def expense_total(data):
    return sum(e["amount"] for e in active_entries(data, "expenses"))


def net_profit(data):
    return revenue_total(data) - expense_total(data)


def active_entries(data, entry_type):
    goal_id = active_goal(data)["id"]
    return [entry for entry in data.get(entry_type, []) if entry.get("goal_id", goal_id) == goal_id]


def today_revenue(data):
    today = date.today().isoformat()
    return sum(e["amount"] for e in active_entries(data, "revenue") if e["timestamp"].startswith(today))


def today_expenses(data):
    today = date.today().isoformat()
    return sum(e["amount"] for e in active_entries(data, "expenses") if e["timestamp"].startswith(today))


def week_revenue(data):
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    return sum(e["amount"] for e in active_entries(data, "revenue") if e["timestamp"][:10] >= week_ago)


def month_revenue(data):
    month_start = date.today().replace(day=1).isoformat()
    return sum(e["amount"] for e in active_entries(data, "revenue") if e["timestamp"][:10] >= month_start)


def days_left(data):
    return max((goal_date(data) - date.today()).days, 0)


def daily_target(data):
    dl = days_left(data)
    if dl <= 0:
        return 0
    remaining = max(goal_amount(data) - net_profit(data), 0)
    return remaining / dl


def goal_progress(total, data):
    goal = goal_amount(data)
    if goal <= 0:
        return 0
    return max(0, min(total / goal, 1.0))


def pace_status(data):
    today = date.today()
    start = start_date(data)
    target_date = goal_date(data)
    total_days = max((target_date - start).days + 1, 1)
    elapsed_days = max((today - start).days + 1, 1)
    elapsed_ratio = min(elapsed_days / total_days, 1.0)
    expected = goal_amount(data) * elapsed_ratio
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


def forecast(data):
    net = net_profit(data)
    remaining = max(goal_amount(data) - net, 0)
    if remaining == 0:
        return {"label": "Goal reached", "date": date.today()}

    elapsed = max((date.today() - start_date(data)).days + 1, 1)
    average = net / elapsed
    if average <= 0:
        return {"label": "No forecast", "date": None}

    return {
        "label": "Forecast",
        "date": date.today() + timedelta(days=math.ceil(remaining / average)),
    }


def month_expenses_by_category(data):
    month_start = date.today().replace(day=1).isoformat()
    totals = {}
    for entry in active_entries(data, "expenses"):
        if entry.get("timestamp", "")[:10] < month_start:
            continue
        category = entry.get("category", "Other")
        totals[category] = totals.get(category, 0) + entry["amount"]
    return totals


def budget_statuses(data):
    spent = month_expenses_by_category(data)
    statuses = []
    for category, limit in data.get("budgets", {}).items():
        try:
            limit = float(limit)
        except (TypeError, ValueError):
            continue
        if limit <= 0:
            continue
        amount = spent.get(category, 0)
        statuses.append({"category": category, "spent": amount, "limit": limit, "ratio": amount / limit})
    return sorted(statuses, key=lambda item: item["ratio"], reverse=True)


def add_month(value):
    year = value.year + (value.month == 12)
    month = 1 if value.month == 12 else value.month + 1
    last_day = (date(year, month + 1, 1) - timedelta(days=1)).day if month < 12 else 31
    return date(year, month, min(value.day, last_day))


def apply_due_recurring(data, today=None):
    today = today or date.today()
    added = []
    for item in data.get("recurring", []):
        try:
            due = date.fromisoformat(item["next_due"])
        except (KeyError, TypeError, ValueError):
            continue
        while due <= today:
            entry_type = item.get("type", "expenses")
            entry = {
                "amount": float(item["amount"]),
                "description": item.get("description", "Recurring entry"),
                "timestamp": f"{due.isoformat()}T09:00:00",
                "goal_id": item.get("goal_id", active_goal(data)["id"]),
            }
            if entry_type == "expenses":
                entry["category"] = item.get("category", "Other")
            data[entry_type].append(entry)
            added.append(entry)
            due = add_month(due)
        item["next_due"] = due.isoformat()
    return added


def parse_quick_log(text, data):
    value = text.strip()
    if not value or value[0] not in "+-":
        raise ValueError("Start with + for revenue or - for an expense.")
    parts = value[1:].strip().split(maxsplit=1)
    if not parts:
        raise ValueError("Enter an amount after + or -.")
    try:
        amount = float(parts[0].replace(currency(data), "").replace(",", ""))
    except ValueError as error:
        raise ValueError("Enter a valid amount.") from error
    if amount <= 0:
        raise ValueError("Enter a positive amount.")

    entry_type = "revenue" if value[0] == "+" else "expenses"
    description = parts[1] if len(parts) > 1 else "Quick log"
    category = None
    if entry_type == "expenses":
        for candidate in EXPENSE_CATEGORIES:
            if description.lower().startswith(candidate.lower()):
                category = candidate
                description = description[len(candidate):].lstrip(" :-") or candidate
                break
        category = category or "Other"
    return entry_type, amount, description, category


def import_csv_entries(data, path):
    added = 0
    with open(path, "r", newline="", encoding="utf-8-sig") as source:
        for row in csv.DictReader(source):
            normalized = {str(key).strip().lower(): (value or "").strip() for key, value in row.items() if key}
            amount_text = normalized.get("amount", "")
            if not amount_text:
                continue
            try:
                amount = float(amount_text.replace(currency(data), "").replace(",", ""))
            except ValueError:
                continue
            type_text = normalized.get("type", "").lower()
            entry_type = "expenses" if "expense" in type_text or amount < 0 else "revenue"
            timestamp = normalized.get("date") or normalized.get("timestamp") or date.today().isoformat()
            try:
                timestamp = f"{date.fromisoformat(timestamp[:10]).isoformat()}T12:00:00"
            except ValueError:
                timestamp = datetime.now().isoformat()
            entry = {
                "amount": abs(amount),
                "description": normalized.get("description") or normalized.get("memo") or "Imported entry",
                "timestamp": timestamp,
                "goal_id": active_goal(data)["id"],
            }
            if entry_type == "expenses":
                entry["category"] = normalized.get("category") or "Other"
            data[entry_type].append(entry)
            added += 1
    return added


def monthly_review(data):
    month_start = date.today().replace(day=1).isoformat()
    revenue = sum(entry["amount"] for entry in active_entries(data, "revenue") if entry.get("timestamp", "")[:10] >= month_start)
    expenses = sum(entry["amount"] for entry in active_entries(data, "expenses") if entry.get("timestamp", "")[:10] >= month_start)
    categories = month_expenses_by_category(data)
    largest = max(categories, key=categories.get) if categories else "None"
    return "\n".join(
        [
            f"Revenue: {fmt(revenue, data)}",
            f"Expenses: {fmt(expenses, data)}",
            f"Net: {fmt(revenue - expenses, data)}",
            f"Top spending: {largest}",
            f"Goal progress: {pct_label(net_profit(data), data)}",
        ]
    )


def weekly_recap(data):
    week_start = date.today() - timedelta(days=6)
    revenue = sum(
        entry["amount"]
        for entry in active_entries(data, "revenue")
        if entry.get("timestamp", "")[:10] >= week_start.isoformat()
    )
    expenses = sum(
        entry["amount"]
        for entry in active_entries(data, "expenses")
        if entry.get("timestamp", "")[:10] >= week_start.isoformat()
    )
    return (
        f"Hustler weekly recap\n"
        f"{active_goal(data)['name']}: {pct_label(net_profit(data), data)} complete\n"
        f"Income: {fmt(revenue, data)} | Spending: {fmt(expenses, data)}\n"
        f"Net: {fmt(revenue - expenses, data)} | Streak: {streak(data)} days"
    )


def choose_csv_file():
    try:
        from AppKit import NSModalResponseOK, NSOpenPanel

        panel = NSOpenPanel.openPanel()
        panel.setCanChooseFiles_(True)
        panel.setCanChooseDirectories_(False)
        panel.setAllowsMultipleSelection_(False)
        panel.setAllowedFileTypes_(["csv"])
        return panel.URL().path() if panel.runModal() == NSModalResponseOK else None
    except Exception:
        return None


def copy_to_clipboard(text):
    try:
        from AppKit import NSPasteboard, NSPasteboardTypeString

        board = NSPasteboard.generalPasteboard()
        board.clearContents()
        board.setString_forType_(text, NSPasteboardTypeString)
        return True
    except Exception:
        return False


def streak(data):
    s = 0
    today = date.today()
    for i in range(365):
        day = today - timedelta(days=i)
        day_str = day.isoformat()
        if any(e["timestamp"].startswith(day_str) for e in active_entries(data, "revenue")):
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
        if any(e["timestamp"].startswith(day_str) for e in active_entries(data, "revenue")):
            s += 1
            best = max(best, s)
        else:
            s = 0
    return best


def expense_by_category(data):
    cats = {}
    for e in active_entries(data, "expenses"):
        cat = e.get("category", "Other")
        cats[cat] = cats.get(cat, 0) + e["amount"]
    return dict(sorted(cats.items(), key=lambda x: -x[1]))


def savings_rate(data):
    rev = revenue_total(data)
    if rev == 0:
        return 0
    return ((rev - expense_total(data)) / rev) * 100


def progress_bar(total, data):
    pct = goal_progress(total, data)
    filled = round(pct * 20)
    return "█" * filled + "░" * (20 - filled)


def pct_label(total, data):
    goal = goal_amount(data)
    return f"{int((total / goal) * 100) if goal else 0}%"


def fmt(amount, data=None):
    symbol = currency(data)
    if abs(amount) >= 1000:
        return f"{symbol}{amount/1000:.1f}k"
    return f"{symbol}{amount:,.0f}"


def recent_entries(data, limit=5):
    entries = []
    goal_id = active_goal(data)["id"]
    for entry_type in ("revenue", "expenses"):
        for idx, entry in enumerate(data.get(entry_type, [])):
            if entry.get("goal_id", goal_id) != goal_id:
                continue
            entries.append((entry.get("timestamp", ""), entry_type, idx, entry))
    entries.sort(key=lambda item: item[0], reverse=True)
    return entries[:limit]


def entry_summary(entry_type, entry, data=None):
    prefix = "+" if entry_type == "revenue" else "-"
    desc = entry.get("description", "No description")
    day = entry.get("timestamp", "")[:10] or "unknown"
    return f"{prefix}{currency(data)}{entry['amount']:,.2f}  {desc}  ({day})"


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
            elif key == "halfway" and total >= goal_amount(data) / 2:
                earned.append(key)
                new_achs.append(ach)
            elif key == "goal_crusher" and total >= goal_amount(data):
                earned.append(key)
                new_achs.append(ach)
            elif ach["threshold"] and total >= ach["threshold"]:
                earned.append(key)
                new_achs.append(ach)

    data["achievements"] = earned
    return new_achs


def check_milestones(data):
    total = net_profit(data)
    goal = goal_amount(data)
    pct = total / goal if goal else 0
    reached = data.get("milestones", [])
    new_miles = []
    for m in MILESTONES:
        if pct >= m and m not in reached:
            reached.append(m)
            new_miles.append(m)
    data["milestones"] = reached
    return new_miles


def export_csv(data):
    os.makedirs(EXPORT_DIR, exist_ok=True)
    path = os.path.join(EXPORT_DIR, "hustler_export.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Amount", "Description", "Category", "Date"])
        for e in active_entries(data, "revenue"):
            writer.writerow(["Revenue", e["amount"], e.get("description", ""), "", e["timestamp"][:10]])
        for e in active_entries(data, "expenses"):
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

    W, H = 1200, 1500
    PAPER = "#F4F6F2"
    INK = "#173027"
    MUTED = "#65726C"
    LINE = "#C9D1CB"
    SOFT = "#E5EAE4"
    GREEN = "#07805F"
    RED = "#CE5B4E"
    GOLD = "#D5A530"
    BLUE = "#3278B6"

    img = Image.new("RGB", (W, H), PAPER)
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

    net = net_profit(data)
    rev = revenue_total(data)
    exp = expense_total(data)
    s = streak(data)
    bs = best_streak(data)
    rate = savings_rate(data)
    pct = goal_progress(net, data)
    pace = pace_status(data)
    goal = goal_amount(data)
    remaining = max(goal - net, 0)
    cats = list(expense_by_category(data).items())[:3]

    pad = 72
    content_right = W - pad
    draw.rectangle((0, 0, 20, H), fill=GREEN)
    draw.text((pad, 58), "HUSTLER", fill=INK, font=font(54, bold=True))
    draw.text((pad, 126), "PERSONAL FINANCIAL SNAPSHOT", fill=MUTED, font=font(20, bold=True))
    text_right(content_right, 72, date.today().strftime("%d %b %Y").upper(), font(22, bold=True), INK)
    draw.line((pad, 172, content_right, 172), fill=INK, width=3)

    draw.text((pad, 222), "NET PROFIT", fill=MUTED, font=font(22, bold=True))
    fit_text(pad, 260, fmt(net, data), 650, 112, INK, bold=True)
    draw.text((pad, 393), f"{fmt(remaining, data)} remaining of {fmt(goal, data)} goal", fill=MUTED, font=font(27))

    cx, cy, r = 944, 327, 126
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=LINE, width=22)
    draw.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + int(360 * pct), fill=GREEN if pct >= 1 else GOLD, width=22)
    pct_text = f"{int(pct * 100)}%"
    pct_font = font(54, bold=True)
    draw.text((cx - draw.textlength(pct_text, font=pct_font) / 2, cy - 42), pct_text, fill=INK, font=pct_font)
    stamp_label = "OF GOAL"
    stamp_font = font(17, bold=True)
    draw.text((cx - draw.textlength(stamp_label, font=stamp_font) / 2, cy + 30), stamp_label, fill=MUTED, font=stamp_font)

    track_y = 485
    draw.text((pad, 446), "GOAL PROGRESS", fill=MUTED, font=font(19, bold=True))
    draw.rectangle((pad, track_y, content_right, track_y + 22), fill=SOFT)
    filled_x = pad + int((content_right - pad) * pct)
    if filled_x > pad:
        draw.rectangle((pad, track_y, filled_x, track_y + 22), fill=GREEN)
    text_right(content_right, 446, f"{fmt(net, data)} / {fmt(goal, data)}", font(19, bold=True), INK)

    metric_y = 580
    column_width = (content_right - pad) / 3
    metrics = [
        ("REVENUE", fmt(rev, data), GREEN),
        ("EXPENSES", fmt(exp, data), RED),
        ("SAVINGS RATE", f"{rate:.0f}%", BLUE),
    ]
    for index, (label, value, color) in enumerate(metrics):
        x = pad + int(index * column_width)
        if index:
            draw.line((x - 30, metric_y, x - 30, metric_y + 132), fill=LINE, width=2)
        draw.rectangle((x, metric_y, x + 8, metric_y + 38), fill=color)
        draw.text((x + 24, metric_y - 2), label, fill=MUTED, font=font(18, bold=True))
        fit_text(x, metric_y + 52, value, int(column_width - 30), 49, INK, bold=True)

    pace_y = 790
    draw.line((pad, pace_y, content_right, pace_y), fill=INK, width=3)
    draw.text((pad, pace_y + 34), "PACE", fill=MUTED, font=font(19, bold=True))
    pace_label = "AHEAD OF PLAN" if pace["delta"] >= 0 else "BEHIND PLAN"
    draw.text((pad, pace_y + 72), pace_label, fill=GREEN if pace["delta"] >= 0 else RED, font=font(45, bold=True))
    draw.text((pad, pace_y + 132), f"{fmt(abs(pace['delta']), data)} from planned progress", fill=INK, font=font(27))
    right_x = 760
    draw.text((right_x, pace_y + 34), "FROM HERE", fill=MUTED, font=font(19, bold=True))
    fit_text(right_x, pace_y + 70, f"{fmt(pace['needed_daily'], data)}/day", content_right - right_x, 44, INK, bold=True)
    draw.text((right_x, pace_y + 132), f"Day {pace['elapsed_days']} of {pace['total_days']}", fill=MUTED, font=font(24))

    flow_y = 1045
    draw.line((pad, flow_y, content_right, flow_y), fill=INK, width=3)
    draw.text((pad, flow_y + 34), "CASH FLOW", fill=MUTED, font=font(19, bold=True))
    rows = [
        ("TODAY", f"+{currency(data)}{today_revenue(data):,.2f}    -{currency(data)}{today_expenses(data):,.2f}", GREEN),
        ("THIS WEEK", fmt(week_revenue(data), data), GOLD),
        ("THIS MONTH", fmt(month_revenue(data), data), BLUE),
        ("ACTIVE STREAK", f"{s} day{'s' if s != 1 else ''}  /  best {bs}", GREEN if s else RED),
    ]
    for i, (label, value, color) in enumerate(rows):
        ry = flow_y + 82 + i * 54
        draw.rectangle((pad, ry + 7, pad + 12, ry + 26), fill=color)
        draw.text((pad + 30, ry), label, fill=MUTED, font=font(22, bold=True))
        text_right(content_right, ry, value, font(25, bold=True), INK)

    spend_y = 1320
    draw.line((pad, spend_y, content_right, spend_y), fill=LINE, width=2)
    draw.text((pad, spend_y + 28), "TOP SPENDING", fill=MUTED, font=font(18, bold=True))
    if cats:
        x = pad
        max_spend = max(total for _, total in cats) or 1
        for cat, total in cats:
            width = 310
            bar_width = int(width * total / max_spend)
            draw.text((x, spend_y + 64), cat[:18].upper(), fill=INK, font=font(17, bold=True))
            draw.rectangle((x, spend_y + 94, x + width, spend_y + 108), fill=SOFT)
            draw.rectangle((x, spend_y + 94, x + bar_width, spend_y + 108), fill=RED)
            draw.text((x, spend_y + 120), fmt(total, data), fill=MUTED, font=font(18, bold=True))
            x += 350
    else:
        draw.text((pad, spend_y + 66), "No expenses logged yet", fill=MUTED, font=font(20))

    text_right(content_right, H - 34, "LOCAL DATA / HUSTLER", font(17, bold=True), MUTED)

    os.makedirs(EXPORT_DIR, exist_ok=True)
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
        self.update_info = None
        self._ensure_onboarded()
        self._apply_recurring_on_startup()
        self._build_menu()
        self._update_title()
        rumps.timer(QUOTE_ROTATION_SECONDS)(self._cycle_title)
        self._update_timer = rumps.Timer(self._check_for_update, 3)
        self._update_timer.start()

    def _cycle_title(self, _):
        self._quote_idx = (self._quote_idx + 1) % len(QUOTES)
        self._update_title()

    def _check_for_update(self, timer):
        timer.stop()
        self.update_info = latest_release()
        if self.update_info:
            self._build_menu()

    def _open_update(self, _):
        if self.update_info and self.update_info.get("url"):
            webbrowser.open(self.update_info["url"])

    def _ensure_onboarded(self):
        if settings(self.data).get("onboarded"):
            return
        rumps.alert(
            title="Welcome to Hustler",
            message="Set your target once. You can change it later from Settings.",
            ok="Set Up",
        )
        self._edit_goal_settings(first_run=True)

    def _settings_input(self, title, message, default_text):
        response = rumps.Window(
            message=message,
            title=title,
            default_text=default_text,
            ok="Next",
            cancel="Cancel",
            dimensions=(240, 24),
        ).run()
        return response.text.strip() if response.clicked else None

    def _edit_goal_settings(self, _=None, first_run=False):
        current = active_goal(self.data)
        goal_text = self._settings_input(
            "Goal Settings",
            "What is your target amount?",
            str(int(goal_amount(self.data)) if goal_amount(self.data).is_integer() else goal_amount(self.data)),
        )
        if goal_text is None:
            if first_run:
                settings(self.data)["onboarded"] = True
                save_data(self.data)
            return

        try:
            goal = float(goal_text.replace(currency(self.data), "").replace(",", ""))
            if goal <= 0:
                raise ValueError
        except ValueError:
            rumps.alert(title="Invalid goal", message="Enter a positive number, such as 5000.")
            return self._edit_goal_settings(None, first_run=first_run)

        symbol = self._settings_input("Goal Settings", "What currency symbol should Hustler use?", currency(self.data))
        if symbol is None:
            return
        symbol = symbol.strip() or DEFAULT_CURRENCY

        start_text = self._settings_input(
            "Goal Settings",
            "When does this goal start? Use YYYY-MM-DD.",
            start_date(self.data).isoformat(),
        )
        if start_text is None:
            return

        target_text = self._settings_input(
            "Goal Settings",
            "When is the target date? Use YYYY-MM-DD.",
            goal_date(self.data).isoformat(),
        )
        if target_text is None:
            return

        try:
            configured_start = date.fromisoformat(start_text)
            configured_goal = date.fromisoformat(target_text)
            if configured_goal < configured_start:
                raise ValueError
        except ValueError:
            rumps.alert(
                title="Invalid dates",
                message="Use YYYY-MM-DD and set a target date on or after the start date.",
            )
            return self._edit_goal_settings(None, first_run=first_run)

        current["target"] = goal
        current["start_date"] = configured_start.isoformat()
        current["target_date"] = configured_goal.isoformat()
        settings(self.data)["currency"] = symbol
        settings(self.data)["onboarded"] = True
        sync_legacy_goal_settings(settings(self.data))
        save_data(self.data)
        self._update_title()
        self._build_menu()
        rumps.notification(
            title="Goal settings saved",
            subtitle=f"{fmt(goal, self.data)} by {configured_goal.isoformat()}",
            message="",
            sound=False,
        )

    def _apply_recurring_on_startup(self):
        added = apply_due_recurring(self.data)
        if not added:
            return
        check_achievements(self.data)
        check_milestones(self.data)
        save_data(self.data)

    def _add_goal(self, _):
        name = self._settings_input("Add Goal", "Name this goal.", "New Goal")
        if name is None or not name:
            return
        amount_text = self._settings_input("Add Goal", "Target amount.", "5000")
        if amount_text is None:
            return
        try:
            amount = float(amount_text.replace(currency(self.data), "").replace(",", ""))
            if amount <= 0:
                raise ValueError
        except ValueError:
            rumps.alert(title="Invalid goal", message="Enter a positive number.")
            return
        start = self._settings_input("Add Goal", "Start date (YYYY-MM-DD).", date.today().isoformat())
        target = self._settings_input("Add Goal", "Target date (YYYY-MM-DD).", (date.today() + timedelta(days=30)).isoformat())
        if start is None or target is None:
            return
        try:
            start_date_value = date.fromisoformat(start)
            target_date_value = date.fromisoformat(target)
            if target_date_value < start_date_value:
                raise ValueError
        except ValueError:
            rumps.alert(title="Invalid dates", message="Use YYYY-MM-DD with a target date after the start date.")
            return
        goals = settings(self.data)["goals"]
        goal_id = f"goal-{int(datetime.now().timestamp())}"
        goals.append({
            "id": goal_id,
            "name": name,
            "target": amount,
            "start_date": start_date_value.isoformat(),
            "target_date": target_date_value.isoformat(),
        })
        settings(self.data)["active_goal_id"] = goal_id
        sync_legacy_goal_settings(settings(self.data))
        save_data(self.data)
        self._update_title()
        self._build_menu()

    def _switch_goal(self, _):
        goals = settings(self.data)["goals"]
        options = "\n".join(f"{index}. {goal['name']} ({fmt(goal['target'], self.data)})" for index, goal in enumerate(goals, start=1))
        choice = self._settings_input("Switch Goal", f"Choose a goal:\n{options}", "1")
        if choice is None:
            return
        try:
            goal = goals[int(choice) - 1]
        except (ValueError, IndexError):
            rumps.alert(title="Invalid choice", message="Enter a goal number from the list.")
            return
        settings(self.data)["active_goal_id"] = goal["id"]
        sync_legacy_goal_settings(settings(self.data))
        save_data(self.data)
        self._update_title()
        self._build_menu()

    def _set_budget(self, _):
        categories = "\n".join(f"{index}. {name}" for index, name in enumerate(EXPENSE_CATEGORIES, start=1))
        choice = self._settings_input("Category Budget", f"Choose a category:\n{categories}", "1")
        if choice is None:
            return
        try:
            category = EXPENSE_CATEGORIES[int(choice) - 1]
        except (ValueError, IndexError):
            rumps.alert(title="Invalid category", message="Enter a category number from the list.")
            return
        current = self.data.get("budgets", {}).get(category, "")
        amount = self._settings_input("Category Budget", f"Monthly limit for {category}. Enter 0 to remove it.", str(current))
        if amount is None:
            return
        try:
            limit = float(amount.replace(currency(self.data), "").replace(",", ""))
            if limit < 0:
                raise ValueError
        except ValueError:
            rumps.alert(title="Invalid budget", message="Enter a positive number or 0 to remove the limit.")
            return
        self.data.setdefault("budgets", {})
        if limit == 0:
            self.data["budgets"].pop(category, None)
        else:
            self.data["budgets"][category] = limit
        save_data(self.data)
        self._build_menu()

    def _add_recurring(self, _):
        kind = self._settings_input("Recurring Entry", "Type Revenue or Expense.", "Expense")
        if kind is None:
            return
        entry_type = "revenue" if kind.lower().startswith("r") else "expenses"
        amount = self._settings_input("Recurring Entry", "Monthly amount.", "")
        description = self._settings_input("Recurring Entry", "Description.", "")
        due = self._settings_input("Recurring Entry", "First due date (YYYY-MM-DD).", date.today().isoformat())
        if amount is None or description is None or due is None:
            return
        try:
            value = float(amount.replace(currency(self.data), "").replace(",", ""))
            due_date = date.fromisoformat(due)
            if value <= 0:
                raise ValueError
        except ValueError:
            rumps.alert(title="Invalid recurring entry", message="Use a positive amount and a YYYY-MM-DD date.")
            return
        category = "Other"
        if entry_type == "expenses":
            category_input = self._settings_input("Recurring Entry", f"Expense category: {', '.join(EXPENSE_CATEGORIES)}", "Bills")
            if category_input is None:
                return
            category = category_input if category_input in EXPENSE_CATEGORIES else "Other"
        self.data.setdefault("recurring", []).append({
            "type": entry_type,
            "amount": value,
            "description": description or "Recurring entry",
            "category": category,
            "next_due": due_date.isoformat(),
            "goal_id": active_goal(self.data)["id"],
        })
        save_data(self.data)

    def _quick_log(self, _):
        response = self._settings_input("Quick Log", "Use +500 client work or -120 Food lunch.", "")
        if response is None:
            return
        try:
            entry_type, amount, description, category = parse_quick_log(response, self.data)
        except ValueError as error:
            rumps.alert(title="Quick Log", message=str(error))
            return
        self._record_entry(entry_type, amount, description, category)

    def _import_csv(self, _):
        path = choose_csv_file()
        if path is None:
            return
        try:
            added = import_csv_entries(self.data, path)
        except OSError as error:
            rumps.alert(title="Import failed", message=str(error))
            return
        if not added:
            rumps.alert(title="Nothing imported", message="No usable rows were found in that CSV file.")
            return
        check_achievements(self.data)
        check_milestones(self.data)
        save_data(self.data)
        self._update_title()
        self._build_menu()
        rumps.notification(title="CSV imported", subtitle=f"{added} entries added", message="", sound=False)

    def _monthly_review(self, _):
        rumps.alert(title=f"{date.today():%B} Review", message=monthly_review(self.data), ok="Done")

    def _weekly_recap(self, _):
        recap = weekly_recap(self.data)
        copied = copy_to_clipboard(recap)
        rumps.alert(
            title="Weekly Recap",
            message=f"{recap}\n\n{'Copied to your clipboard.' if copied else 'Ready to share.'}",
            ok="Done",
        )

    def _select_recent_entry(self, title):
        entries = recent_entries(self.data, limit=12)
        if not entries:
            rumps.alert(title=title, message="No entries exist for the active goal yet.")
            return None
        options = "\n".join(
            f"{index}. {entry_summary(entry_type, entry, self.data)}"
            for index, (_, entry_type, _, entry) in enumerate(entries, start=1)
        )
        choice = self._settings_input(title, f"Choose an entry:\n{options}", "1")
        if choice is None:
            return None
        try:
            return entries[int(choice) - 1]
        except (ValueError, IndexError):
            rumps.alert(title=title, message="Enter an entry number from the list.")
            return None

    def _edit_entry(self, _):
        selected = self._select_recent_entry("Edit Entry")
        if not selected:
            return
        _, entry_type, _, entry = selected
        amount_text = self._settings_input("Edit Entry", "Amount.", f"{entry['amount']:.2f}")
        description = self._settings_input("Edit Entry", "Description.", entry.get("description", ""))
        if amount_text is None or description is None:
            return
        try:
            amount = float(amount_text.replace(currency(self.data), "").replace(",", ""))
            if amount <= 0:
                raise ValueError
        except ValueError:
            rumps.alert(title="Invalid amount", message="Enter a positive number.")
            return
        entry["amount"] = amount
        entry["description"] = description or "No description"
        if entry_type == "expenses":
            category = self._settings_input("Edit Entry", f"Category: {', '.join(EXPENSE_CATEGORIES)}", entry.get("category", "Other"))
            if category is None:
                return
            entry["category"] = category if category in EXPENSE_CATEGORIES else "Other"
        save_data(self.data)
        self._update_title()
        self._build_menu()

    def _delete_entry(self, _):
        selected = self._select_recent_entry("Delete Entry")
        if not selected:
            return
        _, entry_type, index, entry = selected
        response = rumps.alert(
            title="Delete Entry?",
            message=entry_summary(entry_type, entry, self.data),
            ok="Delete",
            cancel="Cancel",
        )
        if response != 1:
            return
        del self.data[entry_type][index]
        save_data(self.data)
        self._update_title()
        self._build_menu()

    def _manage_recurring(self, _):
        goal_id = active_goal(self.data)["id"]
        items = [item for item in self.data.get("recurring", []) if item.get("goal_id", goal_id) == goal_id]
        if not items:
            rumps.alert(title="Recurring Entries", message="No monthly entries are set for this goal.")
            return
        options = "\n".join(
            f"{index}. {item['description']}  {currency(self.data)}{item['amount']:,.2f}  / month"
            for index, item in enumerate(items, start=1)
        )
        choice = self._settings_input("Recurring Entries", f"Choose an entry to remove:\n{options}", "1")
        if choice is None:
            return
        try:
            selected = items[int(choice) - 1]
        except (ValueError, IndexError):
            rumps.alert(title="Recurring Entries", message="Enter an entry number from the list.")
            return
        if rumps.alert(title="Remove Recurring Entry?", message=selected["description"], ok="Remove", cancel="Cancel") != 1:
            return
        self.data["recurring"].remove(selected)
        save_data(self.data)

    def _update_title(self):
        net = net_profit(self.data)
        quote = QUOTES[self._quote_idx]
        self.title = f"{fmt(net, self.data)} | {pct_label(net, self.data)}  |  {quote}"

    def _build_menu(self):
        self.menu.clear()
        net = net_profit(self.data)
        today_rev = today_revenue(self.data)
        today_exp = today_expenses(self.data)
        wk = week_revenue(self.data)
        mo = month_revenue(self.data)
        bar = progress_bar(net, self.data)
        pct = pct_label(net, self.data)
        target = daily_target(self.data)
        pace = pace_status(self.data)
        s = streak(self.data)
        best = best_streak(self.data)
        rate = savings_rate(self.data)
        cats = expense_by_category(self.data)
        projection = forecast(self.data)
        budgets = budget_statuses(self.data)

        self.menu.add(rumps.MenuItem(f"🎯 Hustler  |  {active_goal(self.data)['name']}"))
        if self.update_info:
            self.menu.add(rumps.MenuItem(f"⬇️ Update Available: v{self.update_info['version']}", callback=self._open_update))
        self.menu.add(rumps.separator)

        symbol = currency(self.data)
        self.menu.add(rumps.MenuItem(f"💵 Today: +{symbol}{today_rev:,.2f}  -{symbol}{today_exp:,.2f}"))
        self.menu.add(rumps.MenuItem(f"Progress:  {bar} {pct}"))
        self.menu.add(rumps.MenuItem(f"📈 Pace: {pace['label']}  •  {fmt(target, self.data)}/day"))
        if projection["date"]:
            self.menu.add(rumps.MenuItem(f"🔮 Forecast: {projection['date']:%b %d, %Y}"))
        if budgets and budgets[0]["ratio"] >= 0.8:
            budget = budgets[0]
            self.menu.add(rumps.MenuItem(f"⚠️ Budget: {budget['category']} at {int(budget['ratio'] * 100)}%"))
        self.menu.add(rumps.separator)

        quick_add = rumps.MenuItem("⚡ Quick Add")
        for amount in [25, 50, 100, 250, 500]:
            quick_add.add(rumps.MenuItem(f"+{symbol}{amount}", callback=self._quick_add))
        self.menu.add(quick_add)
        self.menu.add(rumps.MenuItem("✍️ Quick Log", callback=self._quick_log))
        self.menu.add(rumps.separator)

        self.menu.add(rumps.MenuItem("➕ Add Revenue", callback=self.add_revenue))
        self.menu.add(rumps.MenuItem("➖ Add Expense", callback=self.add_expense))
        self.menu.add(rumps.separator)

        insights_menu = rumps.MenuItem("📊 Insights")
        insights_menu.add(rumps.MenuItem(f"📅 This Week: {fmt(wk, self.data)}"))
        insights_menu.add(rumps.MenuItem(f"📆 This Month: {fmt(mo, self.data)}"))
        insights_menu.add(rumps.MenuItem(f"🔥 Streak: {s} day{'s' if s != 1 else ''}  •  Best: {best}"))
        insights_menu.add(rumps.MenuItem(f"💰 Savings Rate: {rate:.0f}%"))
        if budgets:
            budget_menu = rumps.MenuItem("💳 Budgets")
            for budget in budgets[:5]:
                budget_menu.add(rumps.MenuItem(f"{budget['category']}: {fmt(budget['spent'], self.data)} / {fmt(budget['limit'], self.data)}"))
            insights_menu.add(budget_menu)

        if cats:
            spending_menu = rumps.MenuItem("💸 Spending")
            for cat, total in list(cats.items())[:5]:
                spending_menu.add(rumps.MenuItem(f"{cat}: {fmt(total, self.data)}"))
            insights_menu.add(spending_menu)

        earned = self.data.get("achievements", [])
        if earned:
            achievement_menu = rumps.MenuItem("🏅 Achievements")
            for key in earned:
                if key in ACHIEVEMENTS:
                    achievement_menu.add(rumps.MenuItem(ACHIEVEMENTS[key]["name"]))
            insights_menu.add(achievement_menu)

        reached = self.data.get("milestones", [])
        if reached:
            labels = {0.25: "25%", 0.50: "50%", 0.75: "75%", 1.0: "100%"}
            milestone_menu = rumps.MenuItem("🏁 Milestones")
            for m in sorted(reached):
                milestone_menu.add(rumps.MenuItem(labels.get(m, f"{int(m * 100)}%")))
            insights_menu.add(milestone_menu)

        recent = recent_entries(self.data, limit=4)
        if recent:
            recent_menu = rumps.MenuItem("🧾 Recent Activity")
            for _, entry_type, _, entry in recent:
                recent_menu.add(rumps.MenuItem(entry_summary(entry_type, entry, self.data)))
            insights_menu.add(recent_menu)
        self.menu.add(insights_menu)

        tools_menu = rumps.MenuItem("🛠 Tools")
        tools_menu.add(rumps.MenuItem("📋 Monthly Review", callback=self._monthly_review))
        tools_menu.add(rumps.MenuItem("📣 Weekly Recap", callback=self._weekly_recap))
        tools_menu.add(rumps.MenuItem("📥 Import CSV", callback=self._import_csv))
        tools_menu.add(rumps.MenuItem("📤 Export CSV", callback=self._export_csv))
        tools_menu.add(rumps.MenuItem("🖼 Export Image", callback=self._export_image))
        self.menu.add(tools_menu)

        settings_menu = rumps.MenuItem("⚙️ Settings")
        settings_menu.add(rumps.MenuItem("🎯 Edit Active Goal", callback=self._edit_goal_settings))
        settings_menu.add(rumps.MenuItem("➕ Add Goal", callback=self._add_goal))
        settings_menu.add(rumps.MenuItem("🔄 Switch Goal", callback=self._switch_goal))
        settings_menu.add(rumps.MenuItem("💳 Set Category Budget", callback=self._set_budget))
        settings_menu.add(rumps.MenuItem("🔁 Add Monthly Recurring", callback=self._add_recurring))
        settings_menu.add(rumps.MenuItem("🗂 Manage Recurring", callback=self._manage_recurring))
        self.menu.add(settings_menu)
        entries_menu = rumps.MenuItem("🧾 Manage Entries")
        entries_menu.add(rumps.MenuItem("✏️ Edit Recent Entry", callback=self._edit_entry))
        entries_menu.add(rumps.MenuItem("🗑 Delete Recent Entry", callback=self._delete_entry))
        entries_menu.add(rumps.MenuItem("↩️ Undo Last Entry", callback=self._undo_last_entry))
        self.menu.add(entries_menu)
        self.menu.add(rumps.MenuItem("🔄 Reset Month", callback=self._reset_month))
        self.menu.add(rumps.separator)

        self.menu.add(rumps.MenuItem("Quit", callback=self.quit_app))

    def _quick_add(self, sender):
        amount = float(sender.title.replace("+", "").replace(currency(self.data), "").replace(",", ""))
        self._record_entry("revenue", amount, "Quick add")

    def _record_entry(self, entry_type, amount, description, category=None):
        entry = {
            "amount": amount,
            "description": description or "No description",
            "timestamp": datetime.now().isoformat(),
            "goal_id": active_goal(self.data)["id"],
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
            title=f"{emoji} {sign}{currency(self.data)}{entry['amount']:,.2f} added!",
            subtitle=entry.get("description", "No description"),
            message=f"Net: {currency(self.data)}{net:,.2f}  •  {pct_label(net, self.data)} to goal",
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
            amount = float(amount_resp.text.strip().replace(currency(self.data), "").replace(",", ""))
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
            message=entry_summary(entry_type, entry, self.data),
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
            subtitle=entry_summary(entry_type, entry, self.data),
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
