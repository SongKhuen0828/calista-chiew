"""Build the link-preview card (assets/img/og.jpg) shown when the page is shared.

Run from the project root:  python3 tools/build_og.py
Needs assets/img/portrait.webp (made by build_assets.py). Plus Jakarta Sans is
downloaded from Google Fonts into a temporary folder.
"""
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = {
    500: "https://fonts.gstatic.com/s/plusjakartasans/v12/LDIbaomQNQcsA88c7O9yZ4KMCoOg4IA6-91aHEjcWuA_m07NSg.ttf",
    700: "https://fonts.gstatic.com/s/plusjakartasans/v12/LDIbaomQNQcsA88c7O9yZ4KMCoOg4IA6-91aHEjcWuA_TknNSg.ttf",
}
SAGE, INK, INK_SOFT, CLAY, CLAY_DEEP = "#E4E8DF", "#1F2A22", "#3A463D", "#B4583A", "#9A4529"
W, H, SCALE = 1200, 630, 2  # drawn at 2x, then downsampled for smooth edges


def font(path, size):
    return ImageFont.truetype(str(path), size * SCALE)


def main():
    tmp = Path(tempfile.mkdtemp())
    for weight, url in FONTS.items():
        subprocess.run(["curl", "-s", "-o", str(tmp / f"{weight}.ttf"), url], check=True)

    s = SCALE
    card = Image.new("RGB", (W * s, H * s), SAGE)
    draw = ImageDraw.Draw(card)

    # Portrait as an arch, outer clay arch, ground line (same gesture as the page)
    pw, ph = 330, 440
    px, ground = 110, 560
    portrait = Image.open("assets/img/portrait.webp").convert("RGB").resize((pw * s, ph * s), Image.LANCZOS)
    mask = Image.new("L", portrait.size, 0)
    md = ImageDraw.Draw(mask)
    r = pw * s // 2
    md.ellipse((0, 0, pw * s, pw * s), fill=255)
    md.rectangle((0, r, pw * s, ph * s), fill=255)
    card.paste(portrait, (px * s, (ground - ph) * s), mask)
    gap = 16
    ox0, ox1, oy = (px - gap) * s, (px + pw + gap) * s, (ground - ph - gap) * s
    orr = (ox1 - ox0) // 2
    draw.arc((ox0, oy, ox1, oy + 2 * orr), 180, 360, fill=CLAY, width=3 * s)
    draw.line((ox0, oy + orr, ox0, ground * s), fill=CLAY, width=3 * s)
    draw.line((ox1, oy + orr, ox1, ground * s), fill=CLAY, width=3 * s)
    draw.line(((px - 44) * s, ground * s, (px + pw + 44) * s, ground * s), fill=INK, width=3 * s)

    # Text column
    x = 560 * s
    draw.text((x, 120 * s), "Calista Chiew", font=font(tmp / "700.ttf", 74), fill=INK)
    draw.text((x, 222 * s), "Architectural graduate", font=font(tmp / "500.ttf", 30), fill=CLAY_DEEP)
    draw.text((x, 262 * s), "BSc (Hons) Architecture, SEGi University", font=font(tmp / "500.ttf", 26), fill=INK_SOFT)
    y = 340
    for line in ("CGPA 3.88 · Dean's List, 4 semesters",
                 "Intern, DP Architects · 2026",
                 "Champion, PAM PAASWE Booth Design 2024"):
        draw.ellipse((x, (y + 12) * s, x + 10 * s, (y + 22) * s), fill=CLAY)
        draw.text((x + 26 * s, y * s), line, font=font(tmp / "500.ttf", 25), fill=INK)
        y += 44
    draw.text((x, 520 * s), "calista-chiew.vercel.app", font=font(tmp / "700.ttf", 24), fill=CLAY_DEEP)

    card.resize((W, H), Image.LANCZOS).save("assets/img/og.jpg", "JPEG", quality=88)
    print("assets/img/og.jpg")


if __name__ == "__main__":
    main()
