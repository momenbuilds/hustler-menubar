# Hustler

Hustler is a private macOS menu bar app for tracking financial goals without accounts, subscriptions, or cloud sync.

![Hustler progress card preview](assets/hustler-progress-preview.gif)

## Download

Download the build for your Mac from [Releases](https://github.com/momenbuilds/hustler-menubar/releases/latest), unzip it, and drag `Hustler.app` into Applications:

- Intel Macs: `Hustler-macOS-x86_64.zip`
- Apple-silicon Macs (M1, M2, M3, M4): `Hustler-macOS-arm64.zip`

On first launch, macOS may ask for confirmation because Hustler is not distributed through the App Store. Control-click `Hustler.app`, choose `Open`, then confirm once.

## First Launch

Hustler helps you name a first goal, set the amount and deadline, then points you straight to your first Quick Log. A `Freedom Fund` example is ready to adapt—nothing is sent anywhere.

## Use It Daily

- `Quick Log`: type `+500 client work` or `-120 Food lunch`; it pre-fills your last entry so repeat logging is fast.
- `Quick Add` and `Quick Spend`: add common amounts in one click, or use `Repeat Last Entry` for recurring work.
- `Add Revenue` and `Add Expense`: log detailed entries.
- `Insights`: see spending, budgets, streaks, milestones, and recent activity without making the main menu long.
- `Manage Entries`: edit, delete, or undo recent entries.
- `Settings`: switch goals, create another goal, set category budgets, and manage monthly recurring entries.
- `Tools`: import/export CSV, create a progress card, read a monthly review, copy a weekly recap, and create or restore local backups.

Each goal keeps its own entries and progress. The menu bar always shows the active goal.

## Updates

Hustler checks GitHub Releases once after launch. When a newer version is available, click `Update Available` once: Hustler downloads the correct Intel or Apple-silicon build, briefly quits, replaces itself, and reopens automatically. `What’s New` is optional if you want to read the release notes first.

## Privacy

Your data stays on your Mac in `~/Library/Application Support/Hustler/hustler_data.json`. Hustler automatically keeps a daily pre-save snapshot in `~/Library/Application Support/Hustler/Backups`, and you can create or restore a backup any time. Hustler has no accounts, analytics, or cloud sync.

The only network request is the one-time update check after launch. It only asks GitHub whether a newer public release exists.

## License

MIT
