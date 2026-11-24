# Copyright 2026 Aerium Browser
# SPDX-License-Identifier: GPL-3.0-only

import argparse
import json
import os
import sys
import urllib.request

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "badge-font", "onest-latin.woff2")
REPO = "aerium-browser/aerium-browser-core"
CHROMIUM = ("https://versionhistory.googleapis.com/v1/chrome/platforms/android/"
            "channels/stable/versions?order_by=version%20desc&pageSize=1")

HEIGHT = 22
SIZE = 11.5
PAD = 9
LABEL = "#1B2C5E"
VALUE = "#2A4485"
TEXT = "#FFFFFF"
DIM = "#C9D3E8"

LOGO = (
    "<path d='M330 384.17 149.1 488.61A256 256 0 0 1 108 47.12L108 256A148 148 0 0 0 330 384.17Z' fill='#0E1838'/>"
    "<path d='M108 256 108 47.12A256 256 0 0 1 510.9 232.27L330 127.83A148 148 0 0 0 108 256Z' fill='#3A5BA8'/>"
    "<path d='M330 127.83 510.9 232.27A256 256 0 0 1 149.1 488.61L330 384.17A148 148 0 0 0 330 127.83Z' fill='#111C42'/>"
    "<circle cx='256' cy='256' r='134' fill='#E9F1FB'/><circle cx='256' cy='256' r='104' fill='#2C6BAE'/>"
    "<circle cx='238' cy='236' r='82' fill='#4C97CF'/><circle cx='222' cy='218' r='46' fill='#7FC4E4'/>"
)
STAR = "M12 2.5l2.94 6.1 6.56.9-4.78 4.6 1.17 6.6L12 17.6l-5.89 3.1 1.17-6.6L2.5 9.5l6.56-.9z"


class Font:
    def __init__(self, weight):
        font = TTFont(FONT)
        self.font = instancer.instantiateVariableFont(font, {"wght": weight})
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font["head"].unitsPerEm

    def width(self, text, size):
        return sum(self.glyphs[self.cmap[ord(c)]].width for c in text) * size / self.upm

    def path(self, text, size, x, baseline):
        scale = size / self.upm
        out = []
        for c in text:
            name = self.cmap[ord(c)]
            pen = SVGPathPen(self.glyphs)
            self.glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x, baseline)))
            d = pen.getCommands()
            if d:
                out.append(d)
            x += self.glyphs[name].width * scale
        return " ".join(out)


def badge(regular, bold, label, value, icon=None):
    baseline = HEIGHT / 2 + SIZE * 0.36
    x = PAD
    parts = []
    if icon == "logo":
        parts.append(f"<svg x='{PAD - 2}' y='4' width='14' height='14' viewBox='0 0 512 512'>{LOGO}</svg>")
        x += 16
    elif icon == "star":
        parts.append(f"<path transform='translate({PAD - 2} 4) scale(0.58)' d='{STAR}' fill='{TEXT}'/>")
        x += 16
    label_w = bold.width(label, SIZE)
    split = round(x + label_w + PAD - 1)
    value_w = regular.width(value, SIZE)
    total = round(split + PAD - 1 + value_w + PAD)
    label_d = bold.path(label, SIZE, x, baseline)
    value_d = regular.path(value, SIZE, split + PAD - 1, baseline)
    r = HEIGHT / 2
    title = f"{label}: {value}"
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{total}' height='{HEIGHT}' "
        f"viewBox='0 0 {total} {HEIGHT}' role='img' aria-label='{title}'>"
        f"<title>{title}</title>"
        f"<clipPath id='c'><rect width='{total}' height='{HEIGHT}' rx='{r}'/></clipPath>"
        f"<g clip-path='url(#c)'><rect width='{total}' height='{HEIGHT}' fill='{VALUE}'/>"
        f"<rect width='{split}' height='{HEIGHT}' fill='{LABEL}'/></g>"
        + "".join(parts)
        + f"<path d='{label_d}' fill='{TEXT}'/><path d='{value_d}' fill='{DIM}'/></svg>\n"
    )


def fetch(url):
    headers = {"User-Agent": "aerium-badges", "Accept": "application/json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
        return json.load(r)


def short(n):
    if n >= 1000:
        k = n / 1000
        return f"{k:.1f}k".replace(".0k", "k")
    return str(n)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=os.path.join(HERE, "..", "badges"))
    parser.add_argument("--downloads", default="20k+")
    parser.add_argument("--version")
    parser.add_argument("--chromium")
    parser.add_argument("--stars")
    args = parser.parse_args()

    version = args.version or fetch(f"https://api.github.com/repos/{REPO}/releases/latest")["tag_name"].lstrip("v")
    chromium = args.chromium or fetch(CHROMIUM)["versions"][0]["version"]
    stars = args.stars or short(fetch(f"https://api.github.com/repos/{REPO}")["stargazers_count"])

    regular, bold = Font(400), Font(600)
    badges = {
        "aerium.svg": badge(regular, bold, "Aerium", version, "logo"),
        "chromium.svg": badge(regular, bold, "Latest Chromium", chromium),
        "downloads.svg": badge(regular, bold, "Downloads", args.downloads),
        "stars.svg": badge(regular, bold, "Stars", stars, "star"),
        "license.svg": badge(regular, bold, "License", "GPLv3"),
    }
    os.makedirs(args.out, exist_ok=True)
    for name, svg in badges.items():
        with open(os.path.join(args.out, name), "w", encoding="utf-8") as f:
            f.write(svg)
    print(f"[aerium] badges: Aerium {version}, Chromium {chromium}, {stars} stars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
