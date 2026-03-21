#!/usr/bin/env python3
"""
The Signal — Preflight Validation Script
Checks a finished HTML issue against the machine-verifiable rules in the editorial brief.
Returns exit code 0 if all MUST-PASS checks pass, 1 if any fail.

Usage:
    python validate-issue.py /path/to/issue.html
"""

import sys
import re
from html.parser import HTMLParser
from collections import Counter, OrderedDict

# ──────────────────────────────────────────────
# HTML PARSER
# ──────────────────────────────────────────────

class SignalParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = Counter()
        self.img_tags = []          # list of dicts with src, alt
        self.css_content = ""
        self.text_content = []      # all visible text
        self.in_style = False
        self.in_script = False
        self.current_tag = None

        # Section tracking
        self.sections_found = []    # ordered list of section class names
        self.in_section = None

        # Specific element tracking
        self.foreword_text = []
        self.in_foreword = False
        self.history_text = []
        self.in_history = False
        self.history_main_text = []  # text before "Also This Week in History"
        self.history_past_also = False

        # Radar items
        self.radar_row_count = 0
        self.radar_subsections = []

        # Also-list items per section
        self.also_items = Counter()

        # League tables
        self.league_table_count = 0

        # Long shelf items
        self.long_shelf_items = 0
        self.in_long_shelf = False

        # Nav cards
        self.nav_card_count = 0

        # Link hrefs (for source checking)
        self.link_hrefs = []

        # Track section context for images
        self.section_images = {}  # section_class -> count

        # Divider count
        self.divider_count = 0

        # Book cards
        self.book_card_count = 0

        # Angle boxes
        self.angle_box_count = 0

        # DYK boxes
        self.dyk_box_count = 0

        # Also-title sections
        self.also_title_texts = []
        self.in_also_title = False

        # Track depth for nested divs
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        self.tags[tag] += 1
        self.current_tag = tag
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")

        if tag == "style":
            self.in_style = True
        if tag == "script":
            self.in_script = True

        # Images
        if tag == "img":
            self.img_tags.append({
                "src": attrs_dict.get("src", ""),
                "alt": attrs_dict.get("alt", None)
            })
            if self.in_section and self.in_section in self.section_images:
                self.section_images[self.in_section] += 1

        # Links
        if tag == "a" and "href" in attrs_dict:
            self.link_hrefs.append(attrs_dict["href"])

        # Sections
        if tag in ("section", "header", "footer"):
            if "cover" in cls and "brand" not in cls:
                self.sections_found.append("cover")
                self.in_section = "cover"
            elif "nav-section" in cls:
                self.sections_found.append("navigator")
                self.in_section = "navigator"
            elif "foreword" in cls:
                self.sections_found.append("foreword")
                self.in_foreword = True
                self.in_section = "foreword"
            elif "longshelf" in cls:
                self.sections_found.append("long-shelf")
                self.in_long_shelf = True
                self.in_section = "long-shelf"
            elif "world-section" in cls:
                self.sections_found.append("world")
                self.in_section = "world"
                self.section_images["world"] = 0
            elif "tech-section" in cls:
                self.sections_found.append("pixel-byte")
                self.in_section = "pixel-byte"
                self.section_images["pixel-byte"] = 0
            elif "touchline-section" in cls:
                self.sections_found.append("touchline")
                self.in_section = "touchline"
                self.section_images["touchline"] = 0
            elif "screen-section" in cls:
                self.sections_found.append("screen-sound")
                self.in_section = "screen-sound"
                self.section_images["screen-sound"] = 0
            elif "shelf-section" in cls:
                self.sections_found.append("shelf")
                self.in_section = "shelf"
                self.section_images["shelf"] = 0
            elif "session-section" in cls:
                self.sections_found.append("session")
                self.in_section = "session"
                self.section_images["session"] = 0
            elif "history-section" in cls:
                self.sections_found.append("history")
                self.in_history = True
                self.in_section = "history"
                self.section_images["history"] = 0
            elif "radar-section" in cls:
                self.sections_found.append("on-the-radar")
                self.in_section = "on-the-radar"
            elif "footer" in cls:
                self.sections_found.append("footer")
                self.in_section = "footer"

        # Dividers
        if tag == "hr" and "divider" in cls:
            self.divider_count += 1

        # Nav cards
        if "nav-card" in cls and "nav-card-tag" not in cls:
            self.nav_card_count += 1

        # Radar rows
        if "radar-row" in cls and self.in_section == "screen-sound":
            self.radar_row_count += 1

        # League tables
        if tag == "table" and "league-table" in cls:
            self.league_table_count += 1

        # Long shelf items
        if "shelf-item" in cls and self.in_long_shelf:
            self.long_shelf_items += 1

        # Book cards
        if "book-card" in cls:
            self.book_card_count += 1

        # Angle boxes
        if cls == "angle":
            self.angle_box_count += 1

        # DYK boxes
        if "dyk" in cls and "dyk-title" not in cls:
            self.dyk_box_count += 1

        # Also titles
        if "also-title" in cls:
            self.in_also_title = True

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False
        if tag == "script":
            self.in_script = False
        if tag in ("section", "header", "footer"):
            if self.in_foreword:
                self.in_foreword = False
            if self.in_long_shelf:
                self.in_long_shelf = False
            if self.in_history:
                self.in_history = False
            self.in_section = None

    def handle_data(self, data):
        if self.in_style:
            self.css_content += data
            return
        if self.in_script:
            return

        stripped = data.strip()
        if stripped:
            self.text_content.append(stripped)

            if self.in_foreword:
                self.foreword_text.append(stripped)

            if self.in_history:
                if "Also This Week in History" in stripped:
                    self.history_past_also = True
                if not self.history_past_also:
                    self.history_main_text.append(stripped)

            if self.in_also_title:
                self.also_title_texts.append(stripped)
                self.in_also_title = False


# ──────────────────────────────────────────────
# VALIDATION CHECKS
# ──────────────────────────────────────────────

class ValidationResult:
    def __init__(self):
        self.passes = []
        self.failures = []
        self.warnings = []

    def ok(self, msg):
        self.passes.append(msg)

    def fail(self, msg):
        self.failures.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def validate(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    parser = SignalParser()
    parser.feed(html)

    r = ValidationResult()
    full_text = " ".join(parser.text_content).lower()
    word_count = len(full_text.split())

    # ── SECTION ORDER ──
    expected_order = [
        "cover", "navigator", "foreword", "long-shelf",
        "world", "pixel-byte", "touchline", "screen-sound", "shelf"
    ]
    # Session is optional but if present must be after shelf
    # History must come after shelf (or session if present)
    # on-the-radar and footer come last

    actual_core = [s for s in parser.sections_found if s in expected_order]
    if actual_core == expected_order:
        r.ok("Section order: correct (core sections in expected order)")
    else:
        r.fail(f"Section order: WRONG. Expected {expected_order}, got {actual_core}")

    # Check history comes after shelf/session and before on-the-radar
    if "history" in parser.sections_found:
        hist_idx = parser.sections_found.index("history")
        shelf_idx = parser.sections_found.index("shelf") if "shelf" in parser.sections_found else -1
        if hist_idx > shelf_idx:
            r.ok("This Week in History: correctly positioned after The Shelf")
        else:
            r.fail("This Week in History: should come after The Shelf")
    else:
        r.fail("This Week in History: MISSING — must appear every week")

    if "on-the-radar" in parser.sections_found:
        r.ok("On the Radar: present")
    else:
        r.fail("On the Radar: MISSING")

    if "footer" in parser.sections_found:
        r.ok("Footer: present")
    else:
        r.fail("Footer: MISSING")

    # ── DIVIDERS ──
    # Should be at least one divider per main section (world, tech, touchline, screen, shelf, session, history)
    main_sections = [s for s in parser.sections_found if s in (
        "world", "pixel-byte", "touchline", "screen-sound", "shelf", "session", "history"
    )]
    if parser.divider_count >= len(main_sections):
        r.ok(f"Section dividers: {parser.divider_count} dividers for {len(main_sections)} main sections")
    else:
        r.fail(f"Section dividers: only {parser.divider_count} dividers for {len(main_sections)} main sections")

    # ── WORD COUNTS ──
    if 5000 <= word_count <= 12000:
        r.ok(f"Total word count: {word_count} (target 6,000–8,000+)")
    elif word_count < 5000:
        r.fail(f"Total word count: {word_count} — UNDER minimum of 5,000")
    else:
        r.warn(f"Total word count: {word_count} — very long, but not necessarily bad")

    foreword_words = len(" ".join(parser.foreword_text).split())
    if 50 <= foreword_words <= 80:
        r.ok(f"Foreword word count: {foreword_words} (target 50–80)")
    elif foreword_words < 50:
        r.fail(f"Foreword word count: {foreword_words} — UNDER minimum of 50")
    else:
        r.fail(f"Foreword word count: {foreword_words} — OVER maximum of 80")

    # History main feature word count
    history_words = len(" ".join(parser.history_main_text).split())
    if history_words > 0:
        if 100 <= history_words <= 400:
            r.ok(f"History feature word count: {history_words} (target 150–300)")
        elif history_words < 100:
            r.warn(f"History feature word count: {history_words} — shorter than target 150–300")
        else:
            r.warn(f"History feature word count: {history_words} — longer than target 150–300")

    # ── LONG SHELF ──
    if 6 <= parser.long_shelf_items <= 8:
        r.ok(f"Long Shelf items: {parser.long_shelf_items} (target 6–8)")
    elif parser.long_shelf_items < 6:
        r.fail(f"Long Shelf items: {parser.long_shelf_items} — UNDER minimum of 6")
    else:
        r.warn(f"Long Shelf items: {parser.long_shelf_items} — over target of 8, but not a failure")

    # ── RELEASE RADAR ──
    if parser.radar_row_count >= 15:
        r.ok(f"Release Radar items: {parser.radar_row_count} (minimum 15)")
    else:
        r.fail(f"Release Radar items: {parser.radar_row_count} — UNDER minimum of 15")

    # Check for radar sub-sections
    radar_subsections_needed = ["now showing", "coming soon", "leaving soon", "streaming"]
    found_subs = []
    for sub in radar_subsections_needed:
        if sub in full_text:
            found_subs.append(sub)
    if len(found_subs) >= 4:
        r.ok("Release Radar sub-sections: all 4 present")
    else:
        missing = [s for s in radar_subsections_needed if s not in found_subs]
        r.fail(f"Release Radar sub-sections: missing {missing}")

    # ── IMAGES ──
    img_count = len(parser.img_tags)
    if img_count >= 6:
        r.ok(f"Images: {img_count} total (minimum 6)")
    else:
        r.fail(f"Images: {img_count} total — UNDER minimum of 6. Every major section needs at least one image.")

    # Check per-section images
    section_img_checks = {
        "world": "The World This Week",
        "pixel-byte": "Pixel & Byte",
        "touchline": "The Touchline",
        "screen-sound": "Screen & Sound",
        "shelf": "The Shelf",
    }
    for sec_key, sec_name in section_img_checks.items():
        count = parser.section_images.get(sec_key, 0)
        if count >= 1:
            r.ok(f"Images in {sec_name}: {count}")
        else:
            r.fail(f"Images in {sec_name}: NONE — at least 1 required")

    # Check alt attributes
    missing_alt = [img for img in parser.img_tags if img["alt"] is None or img["alt"].strip() == ""]
    if parser.img_tags and not missing_alt:
        r.ok("Image alt text: all images have alt attributes")
    elif missing_alt:
        r.fail(f"Image alt text: {len(missing_alt)} images missing alt attributes")

    # ── TYPOGRAPHY ──
    css = parser.css_content

    fonts_expected = {
        "Playfair Display": "headlines",
        "Source Serif 4": "body text",
        "Source Sans 3": "UI elements"
    }
    for font, usage in fonts_expected.items():
        if font.lower().replace(" ", "") in css.lower().replace(" ", ""):
            r.ok(f"Font '{font}' ({usage}): found in CSS")
        else:
            r.fail(f"Font '{font}' ({usage}): NOT FOUND in CSS")

    # Check for wrong fonts
    wrong_fonts = ["Cormorant Garamond", "DM Sans", "JetBrains Mono", "Inter", "Roboto"]
    for font in wrong_fonts:
        # Use word-boundary-aware regex to avoid false positives
        # e.g. 'Inter' should not match 'pointer-events' or 'pointer'
        pattern = r"(?i)(?<![a-z-])" + re.escape(font) + r"(?![a-z-])"
        if re.search(pattern, css):
            r.fail(f"Wrong font '{font}' found in CSS — should use Playfair Display / Source Serif 4 / Source Sans 3")

    # ── COLOUR PALETTE ──
    expected_colours = {
        "#1A1A2E": "primary dark",
        "#16213E": "mid dark",
        "#E94560": "warm accent (rose)",
        "#FF6B35": "secondary accent (amber)",
        "#2D2D3A": "body text",
    }
    for hex_code, name in expected_colours.items():
        if hex_code.lower() in css.lower():
            r.ok(f"Colour {hex_code} ({name}): found")
        else:
            r.fail(f"Colour {hex_code} ({name}): NOT FOUND in CSS")

    # ── LAYOUT ──
    if "max-width: 880px" in css or "max-width:880px" in css:
        r.ok("Magazine max-width: 880px")
    else:
        # Check for close values
        max_w_match = re.search(r'max-width:\s*(\d+)px', css)
        if max_w_match:
            r.fail(f"Magazine max-width: {max_w_match.group(1)}px — should be 880px")
        else:
            r.fail("Magazine max-width: not found — should be 880px")

    if "max-width: 700px" in css or "max-width:700px" in css or "700px" in css:
        r.ok("Responsive breakpoint: ≤700px present")
    else:
        r.warn("Responsive breakpoint: ≤700px not found — check manually")

    # ── LEAGUE TABLES ──
    if parser.league_table_count >= 2:
        r.ok(f"League tables: {parser.league_table_count} (need Serie A + PL minimum)")
    elif parser.league_table_count == 1:
        r.fail(f"League tables: only {parser.league_table_count} — need both Serie A and PL top 6")
    else:
        r.fail("League tables: NONE — The Touchline must lead with tables")

    # ── TOUCHLINE CONTENT ──
    if "serie a" in full_text:
        r.ok("Touchline: Serie A mentioned")
    else:
        r.fail("Touchline: Serie A NOT mentioned")

    if "premier league" in full_text:
        r.ok("Touchline: Premier League mentioned")
    else:
        r.fail("Touchline: Premier League NOT mentioned")

    # ── MANDATORY SEARCH COVERAGE ──
    coverage_checks = [
        (["iran", "war"], "Iran / dominant running story"),
        (["northern ireland", " ni ", "belfast", "ballymena"], "Northern Ireland"),
        (["switch 2", "nintendo"], "Nintendo Switch 2"),
        (["consumer ai", "chatgpt", "claude", "gemini", "gpt-", "apple intelligence"], "Consumer AI"),
        (["star wars", "lucasfilm"], "Star Wars"),
        (["lego"], "LEGO"),
        (["juventus", "juve"], "Juventus"),
        (["serie a"], "Serie A"),
        (["premier league"], "Premier League"),
        (["champions league"], "Champions League"),
        (["synthwave", "carpenter brut", "kavinsky", "gunship", "perturbator", "fm-84", "the midnight", "madeon", "awolnation"], "Synthwave / tracked artists"),
        (["kettlebell", "dan john", "strongfirst"], "Kettlebells / training"),
        (["disney"], "Disney"),
    ]

    for keywords, topic in coverage_checks:
        found = any(kw in full_text for kw in keywords)
        if found:
            r.ok(f"Coverage: {topic} — present")
        else:
            r.fail(f"Coverage: {topic} — NOT FOUND in the issue")

    # ── REDDIT SOURCES ──
    reddit_links = [h for h in parser.link_hrefs if "reddit.com" in h]
    reddit_mentions = "reddit" in full_text or "r/" in full_text
    if reddit_links:
        r.ok(f"Reddit sources: {len(reddit_links)} Reddit links found")
    elif reddit_mentions:
        r.warn("Reddit mentioned but no direct Reddit links — consider linking to threads")
    else:
        r.fail("Reddit sources: NONE — brief requires consulting Reddit as a source")

    # ── ALSO THIS WEEK LISTS ──
    also_sections = parser.also_title_texts
    expected_also = ["Also This Week", "Also in Tech", "Also on the Pitch", "Also in Film"]
    found_also = 0
    for title in also_sections:
        found_also += 1
    if found_also >= 3:
        r.ok(f"'Also' one-liner lists: {found_also} found across sections")
    else:
        r.fail(f"'Also' one-liner lists: only {found_also} — most sections need 'Also This Week' lists")

    # ── SOURCE ATTRIBUTION ──
    external_links = [h for h in parser.link_hrefs if h.startswith("http") and "fonts.google" not in h]
    if len(external_links) >= 10:
        r.ok(f"Source links: {len(external_links)} external links")
    else:
        r.fail(f"Source links: only {len(external_links)} — stories need attributed source links")

    # ── NAV CARDS ──
    if parser.nav_card_count >= 8:
        r.ok(f"Navigator cards: {parser.nav_card_count}")
    else:
        r.fail(f"Navigator cards: only {parser.nav_card_count} — should have 8+")

    # ══════════════════════════════════════════════
    # EDITORIAL QUALITY — Machine-Verifiable Subset
    # ══════════════════════════════════════════════

    # Foreword banned phrases
    foreword_text_joined = " ".join(parser.foreword_text).lower()
    banned_foreword = ["meanwhile", "elsewhere", "also this week"]
    found_banned = [phrase for phrase in banned_foreword if phrase in foreword_text_joined]
    if not found_banned:
        r.ok("Foreword: no banned phrases (meanwhile/elsewhere/also this week)")
    else:
        r.fail(f"Foreword: contains banned phrase(s): {found_banned}")

    # Foreword should not start with the same words as the cover headline
    cover_start = full_text[:200]  # rough cover area
    foreword_start = foreword_text_joined[:50] if foreword_text_joined else ""
    # This is a heuristic — check if first 5 words match
    if foreword_start:
        fw_words = foreword_start.split()[:5]
        if len(fw_words) >= 5:
            fw_opening = " ".join(fw_words)
            if fw_opening in cover_start:
                r.fail(f"Foreword: opens with same words as cover headline — should be a distinct hook")
            else:
                r.ok("Foreword: distinct opening from cover headline")

    # Exclusion zones — work content
    work_terms = ["enterprise", "ci/cd", "devops", "saas", "microservices", "kubernetes", "terraform"]
    found_work = [t for t in work_terms if t in full_text]
    if not found_work:
        r.ok("Exclusion: no work/enterprise content detected")
    else:
        r.fail(f"Exclusion: work/enterprise terms found: {found_work} — only allowed if Monday-morning threshold is met")

    # Exclusion zones — celebrity/gossip
    celeb_terms = ["celebrity", "gossip", "kardashian", "love island", "reality tv"]
    found_celeb = [t for t in celeb_terms if t in full_text]
    if not found_celeb:
        r.ok("Exclusion: no celebrity/gossip content detected")
    else:
        r.fail(f"Exclusion: celebrity/gossip terms found: {found_celeb}")

    # Exclusion zones — crypto/web3
    crypto_terms = ["crypto", "web3", "blockchain", "nft ", " defi "]
    found_crypto = [t for t in crypto_terms if t in full_text]
    if not found_crypto:
        r.ok("Exclusion: no crypto/web3 content detected")
    else:
        r.warn(f"Exclusion: crypto/web3 terms found: {found_crypto} — only acceptable if major crossover into mainstream")

    # Book recommendation format — "if you liked" / "try"
    shelf_text = ""
    in_shelf = False
    for i, section in enumerate(parser.sections_found):
        if section == "shelf":
            in_shelf = True
    # Simpler approach: check if the phrases exist in the full text near book-related content
    has_rec = ("if you liked" in full_text or "if you enjoyed" in full_text or
               "if you finished" in full_text or "readers who enjoyed" in full_text or
               "fans of" in full_text.lower())
    if has_rec:
        r.ok("Book recommendations: 'If you liked X' format detected")
    else:
        r.warn("Book recommendations: no 'If you liked X, try Y' format detected — should appear most weeks")

    return r


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-issue.py <path-to-issue.html>")
        sys.exit(2)

    html_path = sys.argv[1]
    print(f"\n{'='*60}")
    print(f"  THE SIGNAL — PREFLIGHT VALIDATION")
    print(f"  File: {html_path}")
    print(f"{'='*60}\n")

    result = validate(html_path)

    # Print results
    print(f"  ✅ PASSED: {len(result.passes)}")
    print(f"  ❌ FAILED: {len(result.failures)}")
    print(f"  ⚠️  WARNINGS: {len(result.warnings)}")
    print()

    if result.passes:
        print("─── PASSED ───")
        for msg in result.passes:
            print(f"  ✅ {msg}")
        print()

    if result.warnings:
        print("─── WARNINGS ───")
        for msg in result.warnings:
            print(f"  ⚠️  {msg}")
        print()

    if result.failures:
        print("─── FAILURES ───")
        for msg in result.failures:
            print(f"  ❌ {msg}")
        print()

    # Summary
    print(f"{'='*60}")
    if result.failures:
        print(f"  ❌ PREFLIGHT FAILED — {len(result.failures)} issue(s) must be fixed before publishing")
        print(f"{'='*60}\n")
        sys.exit(1)
    else:
        print(f"  ✅ PREFLIGHT PASSED — ready to publish")
        print(f"{'='*60}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
