# Hustler Menu

Hustler Menu is a lightweight, local-first macOS menu bar app for tracking a financial goal. It keeps the current net profit, goal progress, and a rotating motivational quote visible in the menu bar.

![Hustler progress card preview](assets/hustler-progress-preview.gif)

It has no account, server, analytics, subscription, or cloud sync.

## Download For Mac

Download the latest `Hustler-macOS.zip` from [Releases](https://github.com/momenbuilds/hustler-menubar/releases/latest), unzip it, and drag `Hustler.app` into Applications.

On the first launch, macOS may ask for confirmation because the app is not distributed through the App Store. Control-click `Hustler.app`, choose `Open`, then confirm once.

## What You Can Do

- Set a money goal during first launch, without editing Python code.
- Track revenue and expenses with a description and expense category.
- See net profit, goal percentage, daily target, pace, forecast date, streaks, savings rate, and recent activity.
- Add common revenue amounts quickly.
- Add recurring monthly income or expenses.
- Set monthly category budgets and get an alert when a budget is nearly used.
- Keep multiple goals and switch the active goal whenever you need to.
- Keep entries separate for each goal.
- Import a CSV file and review the current month in the app.
- Copy a share-ready weekly recap in one click.
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
- `Quick Log`: type `+500 client work` or `-120 Food lunch` for a fast entry.
- `Add Revenue`: record a custom revenue entry.
- `Add Expense`: record an expense and category.
- `Undo Last Entry`: remove the newest revenue or expense entry.
- `Manage Entries`: edit or delete a recent entry.
- `Export CSV`: writes `hustler_export.csv` to Downloads.
- `Export Image`: writes `hustler_progress.png` to Downloads.
- `Reset Month`: clears revenue and expenses, but retains achievements and goal settings.

## Goals, Budgets, And Tools

Open `Settings` to edit the active goal, add another goal, switch goals, set a category budget, or add and remove monthly recurring entries. Each goal has its own entries and progress. Recurring entries are added when Hustler next opens, so they do not require a background process.

Open `Tools` for monthly review, a copied weekly recap, CSV import, and exports. CSV import uses the normal macOS file picker and supports Hustler exports plus common CSV files with `Amount`, `Date`, and optional `Description`, `Type`, and `Category` columns.

## Local Data And Privacy

Hustler stores entries, achievements, milestones, and settings in `hustler_data.json` beside the script that is running. The file is ignored by Git so personal data is not committed with the app.

Nothing is sent over the network. Deleting `hustler_data.json` resets Hustler completely on its next launch.

## Troubleshooting

**The app does not appear in the menu bar**

Run it from the repository folder and check the terminal for an error:

```bash
python3 hustler.py
```

**Python cannot find a dependency**

Install the dependencies for the same Python interpreter used to launch the app:

```bash
python3 -m pip install rumps pillow
```

## License

MIT
