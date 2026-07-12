#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build"
VENV_DIR="$ROOT_DIR/.build-venv"
ICON_FILE="$BUILD_DIR/Hustler.icns"
TARGET_ARCH="${1:-$(uname -m)}"

case "$TARGET_ARCH" in
  x86_64|arm64|universal2) ;;
  *)
    echo "Unsupported macOS architecture: $TARGET_ARCH" >&2
    echo "Use x86_64, arm64, or universal2." >&2
    exit 1
    ;;
esac

rm -rf "$BUILD_DIR" "$ROOT_DIR/dist"
mkdir -p "$BUILD_DIR"
export PYINSTALLER_CONFIG_DIR="$BUILD_DIR/pyinstaller-config"

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/python" -m pip install --quiet -r "$ROOT_DIR/requirements.txt" pyinstaller

sips -s format icns "$ROOT_DIR/assets/hustler_app_icon.png" --out "$ICON_FILE" >/dev/null

"$VENV_DIR/bin/python" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name Hustler \
  --target-architecture "$TARGET_ARCH" \
  --osx-bundle-identifier com.momenbuilds.hustler \
  --icon "$ICON_FILE" \
  --add-data "$ROOT_DIR/assets:assets" \
  --distpath "$ROOT_DIR/dist" \
  --workpath "$BUILD_DIR/work" \
  --specpath "$BUILD_DIR" \
  "$ROOT_DIR/hustler.py"

ditto -c -k --sequesterRsrc --keepParent "$ROOT_DIR/dist/Hustler.app" "$ROOT_DIR/dist/Hustler-macOS-$TARGET_ARCH.zip"
echo "Built: $ROOT_DIR/dist/Hustler-macOS-$TARGET_ARCH.zip"
