# Hustler Menu

A lightweight macOS menu bar app for tracking a money goal. It shows your net profit, goal percentage, and a rotating motivational quote directly in the menu bar.

Recommended GitHub repo name: `hustler-menubar`

## What It Does

- Tracks revenue and expenses locally.
- Shows goal progress in the macOS menu bar.
- Calculates daily target, goal pace, streaks, savings rate, and recent activity.
- Supports quick-add revenue amounts.
- Exports a CSV and a shareable progress card.
- Runs without accounts, cloud sync, or analytics.

## Requirements

- macOS
- Python 3
- `rumps`
- `pillow`

Install dependencies:

```bash
python3 -m pip install rumps pillow
```

## Quick Start

Clone the repo:

```bash
git clone https://github.com/YOUR_USERNAME/hustler-menubar.git
cd hustler-menubar
```

Run it:

```bash
python3 hustler.py
```

Hustler will appear in the macOS menu bar. On first launch it asks for your target amount, currency symbol, start date, and target date. No code changes are needed.

## Install For Daily Use

Copy the script into `~/scripts`:

```bash
mkdir -p ~/scripts
mkdir -p ~/scripts/assets
cp hustler.py ~/scripts/hustler.py
cp assets/* ~/scripts/assets/
python3 ~/scripts/hustler.py
```

## Start Automatically On Login

Create a LaunchAgent:

```bash
cat > ~/Library/LaunchAgents/com.hustler.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hustler</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which python3)</string>
        <string>$HOME/scripts/hustler.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.hustler.plist
```

Stop auto-start:

```bash
launchctl unload ~/Library/LaunchAgents/com.hustler.plist
```

## Usage

Click the menu bar item to open the menu.

Common actions:

- `Quick Add`: add common revenue amounts.
- `Add Revenue`: add a custom revenue entry.
- `Add Expense`: add a custom expense entry with a category.
- `Undo Last Entry`: remove the most recent revenue or expense.
- `Export CSV`: saves `~/Downloads/hustler_export.csv`.
- `Export Image`: saves `~/Downloads/hustler_progress.png`.
- `Reset Month`: clears revenue and expenses while keeping achievements.
- `Settings > Edit Goal Settings`: changes your amount, currency, or dates later.

## First-Run Setup

The first launch opens a short setup flow. Enter a positive goal amount, a currency symbol such as `$` or `EGP`, and dates in `YYYY-MM-DD` format.

To change these later, click the menu bar item and choose `Settings > Edit Goal Settings`. Your existing entries stay intact when you update a goal.

## Data Storage

Data, including the goal settings, is stored next to the script:

```text
hustler_data.json
```

Nothing is sent anywhere. There is no server, account, tracking, or cloud sync.

## Troubleshooting

If the app does not show in the menu bar:

```bash
python3 ~/scripts/hustler.py
```

If dependencies are missing:

```bash
python3 -m pip install rumps pillow
```

If the old Python rocket appears in the Dock, quit the old process and start the latest script:

```bash
pkill -f "$HOME/scripts/hustler.py"
python3 ~/scripts/hustler.py
```

The app sets itself as a menu-bar accessory app so it should not keep a Dock icon.

## Repo Name Ideas

Best option:

```text
hustler-menubar
```

Other solid options:

```text
hustler-menu
money-menubar
goalbar
cashbar
profitbar
```

I would avoid `hustler-terminal` because the app is not really a terminal app. It only uses the terminal to start.

## License

MIT
