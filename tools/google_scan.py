# Copyright 2026 Aerium Browser
# SPDX-License-Identifier: GPL-3.0-only

import argparse
import os
import re
import sys

STRING_DIRS = [
    "chrome/browser/ui/android/strings",
    "chrome/android/java/res",
    "components/browser_ui/strings/android",
]

TOP_STRING_DIRS = [
    "components",
]

FEATURE_FILES = [
    "chrome/browser/flags/android/chrome_feature_list.cc",
    "chrome/browser/ui/ui_features.cc",
    "chrome/common/chrome_features.cc",
    "components/signin/public/base/signin_switches.cc",
    "components/omnibox/common/omnibox_features.cc",
    "components/sync/base/features.cc",
    "components/search/ntp_features.cc",
    "components/feed/feed_feature_list.cc",
    "components/lens/lens_features.cc",
    "components/optimization_guide/core/optimization_guide_features.cc",
    "components/password_manager/core/common/password_manager_features.cc",
    "components/autofill/core/common/autofill_features.cc",
]

TEXT = re.compile(r"\b(Google|Gemini|Chrome)\b")
MESSAGE = re.compile(r'<message\s+name="(IDS_[A-Z0-9_]+)"[^>]*>(.*?)</message>', re.S)
FEATURE = re.compile(r"BASE_FEATURE\(\s*k(\w+)\s*,(.*?)\)\s*;", re.S)
FEATURE_WORDS = re.compile(
    r"Google|Gemini|Glic|Signin|SignIn|Account|Sync|Lens|Aim|AiMode|Gsa|Agsa|Promo|"
    r"Discover|Feed|Hats|Survey|Ntp|Optimization|Telemetry|Metrics|Report|Upload|Assistant|Cloud"
)
ENABLED = re.compile(r"ENABLED_BY_DEFAULT|\bENABLED\b|enable_if\(")


def strings(src):
    found = {}
    for top in STRING_DIRS:
        root = os.path.join(src, top)
        for base, _, names in os.walk(root):
            for name in names:
                if not name.endswith((".grd", ".grdp")):
                    continue
                path = os.path.join(base, name)
                with open(path, encoding="utf-8", errors="replace") as f:
                    body = f.read()
                for m in MESSAGE.finditer(body):
                    text = " ".join(re.sub(r"<[^>]+>", " ", m.group(2)).split())
                    if TEXT.search(text):
                        found["string " + m.group(1)] = text[:140]
    for top in TOP_STRING_DIRS:
        root = os.path.join(src, top)
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            if not name.endswith((".grd", ".grdp")):
                continue
            with open(os.path.join(root, name), encoding="utf-8", errors="replace") as f:
                body = f.read()
            for m in MESSAGE.finditer(body):
                text = " ".join(re.sub(r"<[^>]+>", " ", m.group(2)).split())
                if TEXT.search(text):
                    found["string " + m.group(1)] = text[:140]
    return found


def features(src):
    found = {}
    for rel in FEATURE_FILES:
        path = os.path.join(src, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            body = f.read()
        for m in FEATURE.finditer(body):
            name, rest = m.group(1), m.group(2)
            if FEATURE_WORDS.search(name) and ENABLED.search(rest):
                found["feature " + name] = rel
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default=".")
    parser.add_argument("--known", required=True)
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()

    found = {}
    found.update(strings(args.src))
    found.update(features(args.src))

    if args.update:
        with open(args.known, "w", encoding="utf-8") as f:
            for key in sorted(found):
                f.write(key + "\n")
        print("[aerium] google scan: %d known entries written" % len(found))
        return 0

    known = set()
    if os.path.exists(args.known):
        with open(args.known, encoding="utf-8") as f:
            known = {line.strip() for line in f if line.strip()}
    new = sorted(k for k in found if k not in known)

    lines = ["[aerium] google scan: %d new of %d" % (len(new), len(found))]
    for key in new:
        lines.append("  NEW %s | %s" % (key, found[key]))
    print("\n".join(lines))

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary and new:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("### Google leftovers to review\n\n")
            for key in new:
                f.write("- `%s` %s\n" % (key, found[key].replace("`", "'")))
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
