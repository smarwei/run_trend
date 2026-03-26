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
    """Create .ico file from PNG icons."""
    icons_dir = Path("icons/hicolor")
    output_file = icons_dir / "de.arneweiss.RunTrend.ico"

    # Load base image (largest available)
    base_img_path = icons_dir / "512x512/apps/de.arneweiss.RunTrend.png"

    if not base_img_path.exists():
        print(f"Error: Base image not found: {base_img_path}")
        return

    base_img = Image.open(base_img_path)

    # Create resized versions
    images = []
    for size in SIZES:
        img = base_img.resize(size, Image.Resampling.LANCZOS)
        images.append(img)

    # Save as .ico
    images[0].save(
        output_file,
        format='ICO',
        sizes=[img.size for img in images],
        append_images=images[1:]
    )

    print(f"Created: {output_file}")
    print(f"Sizes: {', '.join(f'{w}x{h}' for w, h in SIZES)}")

if __name__ == "__main__":
    create_ico()
