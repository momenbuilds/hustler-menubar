# Hustler Menu

Hustler Menu is a lightweight, local-first macOS menu bar app for tracking a financial goal. It keeps the current net profit, goal progress, and a rotating motivational quote visible in the menu bar.

It has no account, server, analytics, subscription, or cloud sync.

## What You Can Do

- Set a money goal during first launch, without editing Python code.
- Track revenue and expenses with a description and expense category.
- See net profit, goal percentage, daily target, pace, streaks, savings rate, and recent activity.
- Add common revenue amounts quickly.
- Undo the latest revenue or expense entry.
- Export your entries as CSV and a shareable progress image.
- Change the goal amount, currency, and dates whenever you need to.

## Requirements

- macOS
- Python 3
- `rumps`
- `pillow`

## Install

Clone the repository and install the two Python dependencies:

```bash
git clone https://github.com/momenbuilds/hustler-menubar.git
cd hustler-menubar
python3 -m pip install rumps pillow
```

Start the app:

```bash
python3 hustler.py
```

Hustler appears in the macOS menu bar. It is designed as a menu bar app and should not keep an icon in the Dock.

## First Launch

The first launch asks for four values:

1. Target amount, for example `5000`.
2. Currency symbol or label, for example `$`, `EGP`, or `EUR`.
3. Start date in `YYYY-MM-DD` format.
4. Target date in `YYYY-MM-DD` format.

The target date must be on or after the start date. The app saves these settings locally and uses them for the menu bar percentage, pace, milestones, notifications, and progress image.

To change them later, open the menu bar item and select `Settings > Edit Goal Settings`. Updating a goal does not remove your entries.

## Daily Use

Click the menu bar item to open Hustler.

- `Quick Add`: record a common revenue amount.
- `Add Revenue`: record a custom revenue entry.
- `Add Expense`: record an expense and category.
- `Undo Last Entry`: remove the newest revenue or expense entry.
- `Export CSV`: writes `hustler_export.csv` to Downloads.
- `Export Image`: writes `hustler_progress.png` to Downloads.
- `Reset Month`: clears revenue and expenses, but retains achievements and goal settings.

## Install For Daily Use

To keep the app outside of the cloned repository, copy the script and icon assets to `~/scripts`:

```bash
mkdir -p ~/scripts/assets
cp hustler.py ~/scripts/hustler.py
cp assets/*.png ~/scripts/assets/
python3 ~/scripts/hustler.py
```

When using this installation, the local data file lives at `~/scripts/hustler_data.json`.

## Start On Login

Create a LaunchAgent after confirming that `python3 ~/scripts/hustler.py` works:

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

To stop automatic startup:

```bash
launchctl unload ~/Library/LaunchAgents/com.hustler.plist
```

## Local Data And Privacy

Hustler stores entries, achievements, milestones, and settings in `hustler_data.json` beside the script that is running. The file is ignored by Git so personal data is not committed with the app.

Nothing is sent over the network. Deleting `hustler_data.json` resets Hustler completely on its next launch.

## Troubleshooting

**The app does not appear in the menu bar**

Run it directly and check the terminal for an error:

```bash
python3 ~/scripts/hustler.py
```

**Python cannot find a dependency**

Install the dependencies for the same Python interpreter used to launch the app:

```bash
python3 -m pip install rumps pillow
```

**An old Dock icon is still visible**

Quit the old script process, then start the current version:

```bash
pkill -f "$HOME/scripts/hustler.py"
python3 ~/scripts/hustler.py
```

## Development Check

Run a syntax check before committing changes:

```bash
python3 -m py_compile hustler.py
```

## License

MIT
