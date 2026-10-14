"""Extract web images from the CV / portfolio PDFs into assets/img as WebP.

Run from the project root:  python3 tools/build_assets.py
Each entry is (output name, page number, source, *options) where source is
an image xref (int) or "page" to render the whole page (used for line drawings).
Options: "trim" removes flat margins, ("crop-top", px) cuts a stray header.
"""
import io
import shutil
import fitz
from PIL import Image, ImageChops

PORTFOLIO = "Portfolio_Calista Chiew.pdf"
CV = "CV_Calista Chiew.pdf"
OUT = "assets/img"

MANIFEST = [
    # Where We Belong — holiday residence, Langkawi
    ("belong-1", 25, 355), ("belong-2", 22, 294, "trim", ("crop-top", 24)), ("belong-3", 24, 344),
    ("belong-4", 25, 351), ("belong-5", 27, 386), ("belong-6", 23, 682),
    # Pasar Borong Gong Pauh — market redevelopment
    ("pasar-1", 17, 220), ("pasar-2", 16, 213), ("pasar-3", 20, 273),
    ("pasar-4", 21, 284), ("pasar-5", 21, 282), ("pasar-6", 18, 231),
    # Tidesmith Atelier — boat-making academy
    ("tide-1", 33, 484), ("tide-2", 32, 475), ("tide-3", 35, 691),
    ("tide-4", 34, 491), ("tide-5", 36, "page"),
    # Merdeka Morphosis — stadium adaptive reuse
    ("merdeka-1", 14, 181), ("merdeka-2", 13, 171), ("merdeka-3", 13, 172),
    ("merdeka-4", 14, 182), ("merdeka-5", 15, 196), ("merdeka-6", 13, 169),
    # The Crossroad of Life — visitor interpretive centre
    ("crossroad-1", 8, 115), ("crossroad-2", 10, 145), ("crossroad-3", 10, 146),
    ("crossroad-4", 8, 119), ("crossroad-5", 9, 672),
    # Trade Through Time — community pavilion
    ("trade-1", 29, 426), ("trade-2", 28, 414, "trim"), ("trade-3", 30, 452),
    ("trade-4", 31, 461), ("trade-5", 29, 437),
    # Technical work
    ("mori-1", 37, 520), ("mori-2", 37, 521),
    ("wd-1", 38, "page"), ("wd-2", 39, "page"),
    ("md-1", 40, "page"), ("md-2", 41, "page"),
]


def xref_to_image(doc, xref):
    pix = fitz.Pixmap(doc, xref)
    smask = doc.xref_get_key(xref, "SMask")
    if smask[0] == "xref":
        mask = fitz.Pixmap(doc, int(smask[1].split()[0]))
        pix = fitz.Pixmap(pix, mask)
    if pix.colorspace and pix.colorspace.n != 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    mode = "RGBA" if pix.alpha else "RGB"
    img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
    if mode == "RGBA":  # flatten transparent areas onto white, not black
        bg = Image.new("RGB", img.size, "white")
        bg.paste(img, mask=img.split()[3])
        img = bg
    return img


def trim(img):
    """Cut away flat white or black margins left over from the PDF layout."""
    for colour in ("white", "black"):
        diff = ImageChops.difference(img, Image.new("RGB", img.size, colour))
        diff = ImageChops.add(diff, diff, 2.0, -40)
        box = diff.getbbox()
        if box:
            img = img.crop(box)
    return img


def page_to_image(doc, pno):
    pix = doc[pno - 1].get_pixmap(dpi=200)
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")


def save(img, name):
    for suffix, width, q in (("", 1800, 80), ("-sm", 900, 78)):
        im = img.copy()
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(f"{OUT}/{name}{suffix}.webp", "WEBP", quality=q, method=6)


def main():
    doc = fitz.open(PORTFOLIO)
    for name, pno, src, *opts in MANIFEST:
        img = page_to_image(doc, pno) if src == "page" else xref_to_image(doc, src)
        if "trim" in opts:
            img = trim(img)
        for opt in opts:
            if isinstance(opt, tuple) and opt[0] == "crop-top":  # strip stray PDF header
                img = img.crop((0, opt[1], img.width, img.height))
        save(img, name)
        print(f"{name:12s} {img.width}x{img.height}")

    cv = fitz.open(CV)
    portrait = xref_to_image(cv, cv[0].get_images(full=True)[0][0])
    portrait.save(f"{OUT}/portrait.webp", "WEBP", quality=86, method=6)
    print("portrait", portrait.size)

    shutil.copy(CV, "assets/docs/Calista-Chiew-CV.pdf")
    # The source portfolio has a leftover editing note on page 22; publish a
    # copy with just that sentence removed and leave the original untouched.
    pub = fitz.open(PORTFOLIO)
    note = "can you change the name of Coastal Village"
    for rect in pub[21].search_for(note):
        pub[21].add_redact_annot(rect, fill=(1, 1, 1))
    pub[21].apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    pub.save("assets/docs/Calista-Chiew-Portfolio.pdf", garbage=3, deflate=True)


if __name__ == "__main__":
    main()
