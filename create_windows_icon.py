#!/usr/bin/env python3
"""Create Windows .ico file from PNG icons."""

from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow")
    exit(1)

# Icon sizes for Windows .ico
SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

def create_ico():
    """Create .ico file from PNG icons.

    Briefcase's Windows backend resolves the icon path from
    pyproject.toml's [tool.briefcase] icon = "icons/hicolor/512x512/apps/
    de.arneweiss.RunTrend" by appending the platform-appropriate
    extension — so on Windows it looks for
    icons/hicolor/512x512/apps/de.arneweiss.RunTrend.ico, NOT
    icons/hicolor/de.arneweiss.RunTrend.ico. Write directly to the
    Briefcase-expected location.
    """
    icons_dir = Path("icons/hicolor")
    apps_dir = icons_dir / "512x512" / "apps"
    output_file = apps_dir / "de.arneweiss.RunTrend.ico"

    # Load base image (largest available).
    base_img_path = apps_dir / "de.arneweiss.RunTrend.png"

    if not base_img_path.exists():
        print(f"Error: Base image not found: {base_img_path}")
        return

    apps_dir.mkdir(parents=True, exist_ok=True)
    base_img = Image.open(base_img_path)

    # Pillow's ICO writer takes a *single* image plus a list of sizes —
    # it generates the resized variants internally. Using
    # `append_images` with pre-resized images produces a malformed .ico
    # on some Pillow versions (the file ends up with only the smallest
    # variant), which is why the previous run shipped a 16x16-only
    # icon. Pass sizes explicitly instead.
    base_img.save(output_file, format="ICO", sizes=SIZES)

    print(f"Created: {output_file}")
    print(f"Sizes: {', '.join(f'{w}x{h}' for w, h in SIZES)}")

if __name__ == "__main__":
    create_ico()
