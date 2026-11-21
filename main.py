#!/usr/bin/env python3
"""The Catalogue Photo of an Impossible Gadget.

Programmatically renders a studio catalogue photograph of the
BANANAFORM 3000: a benchtop banana straightener. A curved banana
feeds in on the left, the machine's rollers press it flat, and a
perfectly straight banana emerges on the right. One accessory only:
a single spare curved banana resting on the bench.

Three candidate concepts were sketched before this one was chosen:
  1. Sock-sorting toaster -- joke reads, but a toaster is a cliche.
  2. BANANAFORM 3000 banana straightener -- CHOSEN: the absurd job
     (straightening a banana) reads at a glance, the engineering is
     specific (rollers, hinge, dial set to STRAIGHT), and the
     before/after banana makes the joke without any caption.
  3. Wi-Fi cable (plugs at both ends) -- reads as an ordinary cable
     at a glance; the joke is too weak.

Selection criteria: closest to the brief, most original, most
striking at first glance, absurd function legible without a caption.

No network, no randomness: fully deterministic output.
Writes /output/entry.png (1024x1024 PNG).
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024
OUT = "/output/entry.png"


# ---------------------------------------------------------------- helpers

def load_font(bold=False, size=20):
    for name in ("DejaVuSans-Bold.ttf", "DejaVuSans.ttf",
                 "LiberationSans-Bold.ttf", "LiberationSans-Regular.ttf"):
        for base in ("/usr/share/fonts/truetype/dejavu/",
                     "/usr/share/fonts/truetype/liberation/",
                     "/usr/share/fonts/"):
            p = os.path.join(base, name)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except OSError:
                    pass
    return ImageFont.load_default()


def vgrad(size, top, bottom):
    """Vertical linear gradient image."""
    w, h = size
    g = Image.new("RGB", (1, h))
    px = g.load()
    for y in range(h):
        t = y / max(1, h - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t)
                         for i in range(3))
    return g.resize((w, h))


def hgrad(size, left, right):
    w, h = size
    g = Image.new("RGB", (w, 1))
    px = g.load()
    for x in range(w):
        t = x / max(1, w - 1)
        px[x, 0] = tuple(int(left[i] + (right[i] - left[i]) * t)
                         for i in range(3))
    return g.resize((w, h))


def steel(size, vertical=True):
    """Brushed-steel gradient with a soft sheen band."""
    if vertical:
        img = vgrad(size, (226, 228, 232), (168, 172, 180))
    else:
        img = hgrad(size, (214, 217, 222), (176, 180, 188))
    ov = Image.new("L", size, 0)
    d = ImageDraw.Draw(ov)
    w, h = size
    d.polygon([(int(w * 0.15), 0), (int(w * 0.45), 0),
               (int(w * 0.30), h), (int(w * 0.05), h)], fill=38)
    sheen = Image.new("RGB", size, (255, 255, 255))
    img = Image.composite(sheen, img, ov)
    return img


def paste_masked(base, img, box, mask):
    base.paste(img, box, mask)


def rrect_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1],
                                        radius=radius, fill=255)
    return m


def soft_shadow(layer, box, blur, alpha):
    """Draw a soft elliptical shadow onto an RGBA layer."""
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.ellipse(box, fill=(30, 28, 26, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    layer.alpha_composite(sh)


# ---------------------------------------------------------------- bananas

def draw_curved_banana(draw, cx, cy, r, a0, a1, width, flip=False):
    """A banana as a thick arc with tapered ends and a highlight.

    (cx, cy) arc centre, r radius, a0..a1 angles in degrees (PIL
    convention, clockwise from 3 o'clock)."""
    # outer skin
    draw.arc([cx - r, cy - r, cx + r, cy + r], a0, a1,
             fill=(196, 148, 20), width=width + 6)
    draw.arc([cx - r, cy - r, cx + r, cy + r], a0, a1,
             fill=(245, 205, 60), width=width)
    # pale inner highlight, offset toward the light
    draw.arc([cx - r + 4, cy - r - 6, cx + r + 4, cy + r - 6], a0 + 6, a1 - 6,
             fill=(252, 226, 120), width=max(6, width // 4))
    # tips: stem (brown) at a0 end, blossom end at a1 end
    for ang, col in ((a0, (96, 62, 26)), (a1, (120, 84, 40))):
        t = math.radians(ang)
        x = cx + r * math.cos(t)
        y = cy + r * math.sin(t)
        rr = width // 2 - 2
        draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col)


def draw_straight_banana(draw, x0, y0, x1, y1, width):
    """A perfectly straight banana: tapered capsule with highlight."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    hw = width / 2.0
    pts = []
    for t in (0.0, 0.12, 0.5, 0.88, 1.0):
        w = hw * (0.55 + 0.45 * math.sin(math.pi * min(1.0, t * 1.05)))
        px, py = x0 + dx * t, y0 + dy * t
        pts.append((px + nx * w, py + ny * w))
    for t in (1.0, 0.88, 0.5, 0.12, 0.0):
        w = hw * (0.55 + 0.45 * math.sin(math.pi * min(1.0, t * 1.05)))
        px, py = x0 + dx * t, y0 + dy * t
        pts.append((px - nx * w, py - ny * w))
    draw.polygon(pts, fill=(245, 205, 60), outline=(196, 148, 20))
    # top highlight stripe
    hl = []
    for t in (0.08, 0.5, 0.92):
        w = hw * (0.55 + 0.45 * math.sin(math.pi * min(1.0, t * 1.05)))
        px, py = x0 + dx * t, y0 + dy * t
        hl.append((px + nx * w * 0.45, py + ny * w * 0.45))
    draw.line(hl, fill=(252, 226, 120), width=max(5, width // 5))
    # brown tips
    for (px, py) in ((x0, y0), (x1, y1)):
        rr = width // 4
        draw.ellipse([px - rr, py - rr, px + rr, py + rr],
                     fill=(96, 62, 26))


# ---------------------------------------------------------------- scene

def build():
    img = Image.new("RGB", (W, H))
    # studio backdrop: warm off-white gradient, floor below y=742
    bg = vgrad((W, H), (232, 229, 224), (248, 247, 244))
    img.paste(bg, (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    # seamless backdrop: floor slightly darker, soft horizon line
    d.rectangle([0, 742, W, H], fill=(226, 223, 218))
    d.rectangle([0, 742, W, 744], fill=(205, 202, 197))
    # gentle radial light pool behind the product
    pool = Image.new("L", (W, H), 0)
    pd = ImageDraw.Draw(pool)
    pd.ellipse([170, 120, 854, 900], fill=42)
    pool = pool.filter(ImageFilter.GaussianBlur(140))
    img.paste(Image.new("RGB", (W, H), (255, 255, 255)), (0, 0), pool)

    # ---- shadows (RGBA layer, composited under the product)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    soft_shadow(sh, [205, 700, 815, 756], 16, 110)   # machine base
    soft_shadow(sh, [120, 690, 400, 724], 10, 70)    # curved banana in
    soft_shadow(sh, [640, 688, 940, 722], 10, 70)    # straight banana out
    soft_shadow(sh, [560, 800, 900, 852], 14, 90)    # spare banana
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- input banana: curved, feeding into the machine from the left.
    # The crescent's right tip slides behind the tower housing, so the
    # banana visibly disappears INTO the machine.
    draw_curved_banana(d, 180, 250, 200, 60, 125, 46)
    # its tail disappears behind the machine housing

    # ---- output banana: perfectly straight, emerging to the right
    draw_straight_banana(d, 640, 545, 918, 545, 48)

    # ---- machine base (brushed steel body)
    base_box = (215, 560, 805, 706)
    base = steel((base_box[2] - base_box[0], base_box[3] - base_box[1]))
    mask = rrect_mask(base.size, 26)
    img.paste(base, base_box[:2], mask)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle(base_box, radius=26, outline=(120, 124, 132), width=3)
    # front panel inset
    d.rounded_rectangle([238, 600, 782, 690], radius=14,
                        outline=(150, 154, 162), width=2)
    # feet
    d.rounded_rectangle([250, 700, 300, 716], radius=6, fill=(70, 72, 78))
    d.rounded_rectangle([720, 700, 770, 716], radius=6, fill=(70, 72, 78))

    # ---- back tower + hinge (left side, holds the press arm)
    tower = steel((86, 190))
    tmask = rrect_mask(tower.size, 18)
    img.paste(tower, (222, 372), tmask)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([222, 372, 308, 562], radius=18,
                        outline=(120, 124, 132), width=3)
    # hinge disc
    d.ellipse([238, 372, 302, 436], fill=(96, 100, 108),
              outline=(70, 74, 82), width=3)
    d.ellipse([256, 390, 284, 418], fill=(200, 204, 210),
              outline=(120, 124, 132), width=2)

    # ---- press arm: angled steel arm, open above the banana path
    arm_pts = [(262, 396), (788, 470), (788, 528), (262, 454)]
    arm = steel((560, 140), vertical=False)
    amask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(amask).polygon(arm_pts, fill=255)
    # build the arm as a cropped steel strip then mask it
    strip = Image.new("RGB", (W, H), (0, 0, 0))
    strip.paste(arm, (240, 400))
    img.paste(strip, (0, 0), amask)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(arm_pts, outline=(120, 124, 132), width=3)
    # arm underside shadow line
    d.line([(262, 454), (788, 528)], fill=(110, 114, 122), width=4)
    # top-edge highlight so the arm reads as solid steel, not a plank
    d.line([(266, 400), (784, 474)], fill=(245, 246, 248), width=4)
    # handle grip on the arm's free end
    d.rounded_rectangle([742, 478, 786, 500], radius=8, fill=(70, 74, 82))
    # roller visible under the arm, pressing the banana
    d.ellipse([560, 500, 640, 560], fill=(88, 92, 100),
              outline=(60, 64, 72), width=3)
    d.ellipse([586, 516, 614, 544], fill=(190, 194, 202))

    # (the curved banana vanishes behind the tower housing on the left;
    #  no feed rollers are shown there -- the housing is the feed.)

    # ---- control dial on the front panel (kept clear of the brand text)
    cx, cy, r = 732, 645, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(238, 240, 243),
              outline=(110, 114, 122), width=3)
    d.ellipse([cx - r + 7, cy - r + 7, cx + r - 7, cy + r - 7],
              outline=(170, 174, 180), width=2)
    # tick marks: CURVED at 215 deg, STRAIGHT at 325 deg (needle -> STRAIGHT)
    for ang in (215, 325):
        t = math.radians(ang)
        d.line([(cx + (r - 12) * math.cos(t), cy + (r - 12) * math.sin(t)),
                (cx + (r - 4) * math.cos(t), cy + (r - 4) * math.sin(t))],
               fill=(90, 94, 100), width=3)
    # needle pointing at STRAIGHT
    t = math.radians(325)
    d.line([(cx, cy), (cx + (r - 12) * math.cos(t),
                       cy + (r - 12) * math.sin(t))],
           fill=(200, 40, 40), width=4)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(60, 64, 72))
    # green power LED
    d.ellipse([648, 636, 666, 654], fill=(60, 200, 90),
              outline=(30, 120, 50), width=2)

    # ---- brand plate on the front panel
    f_brand = load_font(True, 30)
    f_model = load_font(False, 16)
    d.text((300, 628), "BANANAFORM", font=f_brand, fill=(52, 56, 64))
    d.text((300, 662), "MODEL 3000  ·  ONE BANANA AT A TIME",
           font=f_model, fill=(110, 114, 120))

    # ---- the one accessory: a spare curved banana on the bench
    draw_curved_banana(d, 700, 640, 150, 18, 108, 40)

    # ---- subtle top light streak on the backdrop
    d.rectangle([0, 0, W, 6], fill=(255, 255, 255, 60))

    return img


def main():
    os.makedirs("/output", exist_ok=True)
    img = build()
    img.save(OUT, format="PNG", optimize=True)
    os.chmod(OUT, 0o644)
    size = os.path.getsize(OUT)
    print(f"wrote {OUT}: {img.size[0]}x{img.size[1]} {size} bytes")
    assert img.size == (1024, 1024)
    assert size <= 1_048_576


if __name__ == "__main__":
    main()
