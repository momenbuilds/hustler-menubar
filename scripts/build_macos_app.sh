#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build"
VENV_DIR="$ROOT_DIR/.build-venv"
ICONSET_DIR="$BUILD_DIR/Hustler.iconset"
ICON_FILE="$BUILD_DIR/Hustler.icns"

rm -rf "$BUILD_DIR" "$ROOT_DIR/dist"
mkdir -p "$ICONSET_DIR"

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/python" -m pip install --quiet -r "$ROOT_DIR/requirements.txt" pyinstaller

sips -z 16 16 "$ROOT_DIR/assets/hustler_app_icon.png" --out "$ICONSET_DIR/icon_16x16.png" >/dev/null
sips -z 32 32 "$ROOT_DIR/assets/hustler_app_icon.png" --out "$ICONSET_DIR/icon_16x16@2x.png" >/dev/null
sips -z 32 32 "$ROOT_DIR/assets/hustler_app_icon.png" --out "$ICONSET_DIR/icon_32x32.png" >/dev/null
sips -z 64 64 "$ROOT_DIR/assets/hustler_app_icon.png" --out "$ICONSET_DIR/icon_32x32@2x.png" >/dev/null
sips -z 128 128 "$ROOT_DIR/assets/hustler_app_icon.png" --out "$ICONSET_DIR/icon_128x128.png" >/dev/null
sips -z 256 256 "$ROOT_DIR/assets/hustler_app_icon.png" --out "$ICONSET_DIR/icon_128x128@2x.png" >/dev/null
sips -z 256 256 "$ROOT_DIR/assets/hustler_app_icon.png" --out "$ICONSET_DIR/icon_256x256.png" >/dev/null
sips -z 512 512 "$ROOT_DIR/assets/hustler_app_icon.png" --out "$ICONSET_DIR/icon_256x256@2x.png" >/dev/null
sips -z 512 512 "$ROOT_DIR/assets/hustler_app_icon.png" --out "$ICONSET_DIR/icon_512x512.png" >/dev/null
sips -z 1024 1024 "$ROOT_DIR/assets/hustler_app_icon.png" --out "$ICONSET_DIR/icon_512x512@2x.png" >/dev/null
iconutil -c icns "$ICONSET_DIR" -o "$ICON_FILE"

"$VENV_DIR/bin/python" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name Hustler \
  --osx-bundle-identifier com.momenbuilds.hustler \
  --icon "$ICON_FILE" \
  --add-data "$ROOT_DIR/assets:assets" \
  --distpath "$ROOT_DIR/dist" \
  --workpath "$BUILD_DIR/work" \
  --specpath "$BUILD_DIR" \
  "$ROOT_DIR/hustler.py"

ditto -c -k --sequesterRsrc --keepParent "$ROOT_DIR/dist/Hustler.app" "$ROOT_DIR/dist/Hustler-macOS.zip"
echo "Built: $ROOT_DIR/dist/Hustler-macOS.zip"
