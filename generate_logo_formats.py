"""
Reliabs Logo Format Generator
Takes: White and black mini.png (the original logo)
Outputs: All required formats into reliabslogo/ folder
"""

import os
import struct
import zlib
from PIL import Image

# ── Paths ────────────────────────────────────────────────────────────────────
SOURCE = r"c:\Users\EMMANUEL\OneDrive\Desktop\website\White and black mini.png"
OUT    = r"c:\Users\EMMANUEL\OneDrive\Desktop\website\reliabslogo"
os.makedirs(OUT, exist_ok=True)

src = Image.open(SOURCE).convert("RGBA")
W, H = src.size
print(f"Source image loaded: {W}×{H} px")


# ─────────────────────────────────────────────────────────────────────────────
# 1. SVG  (vector wrapper that embeds the PNG as a base64 data URI)
#    Note: for a true vector SVG you would trace the paths in Illustrator /
#    Inkscape.  This SVG is screen-perfect and scales without leaving Illustrator.
# ─────────────────────────────────────────────────────────────────────────────
import base64, io

buf = io.BytesIO()
src.save(buf, format="PNG")
b64 = base64.b64encode(buf.getvalue()).decode()

svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <title>Reliabs Logo</title>
  <desc>Reliabs brand mark — use this SVG for websites and web apps.</desc>
  <image href="data:image/png;base64,{b64}"
         x="0" y="0" width="{W}" height="{H}"
         image-rendering="crisp-edges"/>
</svg>"""

with open(os.path.join(OUT, "reliabs-logo.svg"), "w", encoding="utf-8") as f:
    f.write(svg_content)
print("✓ reliabs-logo.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 2. PNG variants — multiple sizes (transparent background preserved)
# ─────────────────────────────────────────────────────────────────────────────
png_sizes = [16, 32, 64, 128, 256, 512, 1024]
for sz in png_sizes:
    resized = src.resize((sz, sz), Image.LANCZOS)
    name = f"reliabs-logo-{sz}px.png"
    resized.save(os.path.join(OUT, name), format="PNG", optimize=True)
    print(f"✓ {name}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. WebP  (modern web format — smaller than PNG)
# ─────────────────────────────────────────────────────────────────────────────
src.save(os.path.join(OUT, "reliabs-logo.webp"), format="WEBP", quality=90, lossless=False)
print("✓ reliabs-logo.webp")


# ─────────────────────────────────────────────────────────────────────────────
# 4. JPG  (white background — JPG doesn't support transparency)
# ─────────────────────────────────────────────────────────────────────────────
jpg_img = Image.new("RGB", src.size, (255, 255, 255))
jpg_img.paste(src, mask=src.split()[3])          # paste using alpha as mask
jpg_img.save(os.path.join(OUT, "reliabs-logo.jpg"), format="JPEG", quality=95)
print("✓ reliabs-logo.jpg")


# ─────────────────────────────────────────────────────────────────────────────
# 5. ICO  (favicon — bundles 16×16 and 32×32)
# ─────────────────────────────────────────────────────────────────────────────
ico_sizes = [(16, 16), (32, 32), (48, 48)]
ico_images = [src.resize(s, Image.LANCZOS) for s in ico_sizes]
ico_images[0].save(
    os.path.join(OUT, "reliabs-favicon.ico"),
    format="ICO",
    sizes=ico_sizes
)
print("✓ reliabs-favicon.ico")


# ─────────────────────────────────────────────────────────────────────────────
# 6. PDF  (print-ready — vector container with embedded high-res PNG)
# ─────────────────────────────────────────────────────────────────────────────
try:
    import reportlab
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas as rl_canvas

    print_img = src.resize((1024, 1024), Image.LANCZOS)
    tmp_png = os.path.join(OUT, "_tmp_print.png")
    print_img.save(tmp_png, format="PNG")

    pdf_path = os.path.join(OUT, "reliabs-logo.pdf")
    c = rl_canvas.Canvas(pdf_path, pagesize=(3 * inch, 3 * inch))
    c.drawImage(tmp_png, 0, 0, width=3 * inch, height=3 * inch, mask="auto")
    c.save()
    os.remove(tmp_png)
    print("✓ reliabs-logo.pdf  (via reportlab)")
except ImportError:
    # Fallback — embed PNG inside a minimal valid PDF manually
    print_img = src.resize((1024, 1024), Image.LANCZOS)
    # flatten to RGB for PDF embedding
    rgb = Image.new("RGB", (1024, 1024), (255, 255, 255))
    rgb.paste(print_img, mask=print_img.split()[3])
    buf2 = io.BytesIO()
    rgb.save(buf2, format="JPEG", quality=95)
    img_bytes = buf2.getvalue()

    # Minimal PDF structure
    W_pt = H_pt = int(72 * 3)  # 3 inches at 72 dpi = 216 pt
    img_w = img_h = 1024

    objects = {}

    objects[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[2] = f"<< /Type /Pages /Kids [3 0 R] /Count 1 >>".encode()
    objects[3] = (
        f"<< /Type /Page /Parent 2 0 R "
        f"/MediaBox [0 0 {W_pt} {H_pt}] "
        f"/Contents 4 0 R /Resources << /XObject << /Im1 5 0 R >> >> >>"
    ).encode()
    stream4 = f"q {W_pt} 0 0 {H_pt} 0 0 cm /Im1 Do Q".encode()
    objects[4] = (
        f"<< /Length {len(stream4)} >>".encode()
        + b"\nstream\n" + stream4 + b"\nendstream"
    )
    objects[5] = (
        f"<< /Type /XObject /Subtype /Image "
        f"/Width {img_w} /Height {img_h} "
        f"/ColorSpace /DeviceRGB /BitsPerComponent 8 "
        f"/Filter /DCTDecode /Length {len(img_bytes)} >>".encode()
        + b"\nstream\n" + img_bytes + b"\nendstream"
    )

    pdf_parts = [b"%PDF-1.4\n"]
    offsets = {}
    for num in sorted(objects.keys()):
        offsets[num] = len(b"".join(pdf_parts))
        pdf_parts.append(f"{num} 0 obj\n".encode())
        pdf_parts.append(objects[num] if isinstance(objects[num], bytes) else objects[num])
        pdf_parts.append(b"\nendobj\n")

    xref_offset = len(b"".join(pdf_parts))
    xref = f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n"
    for num in sorted(offsets.keys()):
        xref += f"{offsets[num]:010d} 00000 n \n"
    trailer = (
        f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF"
    )
    pdf_parts.append(xref.encode())
    pdf_parts.append(trailer.encode())

    with open(os.path.join(OUT, "reliabs-logo.pdf"), "wb") as f:
        f.write(b"".join(pdf_parts))
    print("✓ reliabs-logo.pdf  (minimal PDF, no reportlab)")


# ─────────────────────────────────────────────────────────────────────────────
# 7. Android PNGs — density buckets
# ─────────────────────────────────────────────────────────────────────────────
android_densities = {
    "mdpi":    48,
    "hdpi":    72,
    "xhdpi":   96,
    "xxhdpi":  144,
    "xxxhdpi": 192,
}
for density, sz in android_densities.items():
    img = src.resize((sz, sz), Image.LANCZOS)
    name = f"reliabs-logo-android-{density}.png"
    img.save(os.path.join(OUT, name), format="PNG", optimize=True)
    print(f"✓ {name}")


# ─────────────────────────────────────────────────────────────────────────────
# 8. iOS PNGs — 1×, 2×, 3×  (60pt icon = 60/120/180px)
# ─────────────────────────────────────────────────────────────────────────────
ios_scales = {"1x": 60, "2x": 120, "3x": 180}
for scale, sz in ios_scales.items():
    img = src.resize((sz, sz), Image.LANCZOS)
    name = f"reliabs-logo-ios-{scale}.png"
    img.save(os.path.join(OUT, name), format="PNG", optimize=True)
    print(f"✓ {name}")


# ─────────────────────────────────────────────────────────────────────────────
# 9. ICNS  (macOS app icon — manual ICNS build, no external tools needed)
# ─────────────────────────────────────────────────────────────────────────────
def make_icns(dest_path, source_img):
    """Build a minimal valid .icns file from a PIL image."""
    icon_types = [
        (b"is32", 16), (b"il32", 32), (b"ih32", 48),
        (b"it32", 128), (b"ic08", 256), (b"ic09", 512),
    ]
    chunks = []
    for tag, sz in icon_types:
        img_r = source_img.resize((sz, sz), Image.LANCZOS)
        buf_i = io.BytesIO()
        img_r.save(buf_i, format="PNG")
        data = buf_i.getvalue()
        chunk_len = 8 + len(data)
        chunks.append(struct.pack(">4sI", tag, chunk_len) + data)

    body = b"".join(chunks)
    total = 8 + len(body)
    with open(dest_path, "wb") as f:
        f.write(struct.pack(">4sI", b"icns", total))
        f.write(body)

make_icns(os.path.join(OUT, "reliabs-logo.icns"), src)
print("✓ reliabs-logo.icns")


# ─────────────────────────────────────────────────────────────────────────────
# 10. Also copy the master PNG into reliabslogo/ (original full resolution)
# ─────────────────────────────────────────────────────────────────────────────
import shutil
shutil.copy2(SOURCE, os.path.join(OUT, "reliabs-logo-original.png"))
print("✓ reliabs-logo-original.png  (master copy)")


# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("All logo formats saved to:", OUT)
files = sorted(os.listdir(OUT))
for f in files:
    size = os.path.getsize(os.path.join(OUT, f))
    print(f"  {f:<45} {size:>8,} bytes")
print("="*60)
