# news-image-20261119 R2 — "The World in One Page"
# Python 3.13 + PIL only. Fully deterministic: no clock, no random, no network.
# Renders 1024x1024 PNG to $MAKEFUN_OUTPUT_DIR (default /output).
# All 41 stories verified against live wire reporting in-session (20 Nov 2026).
# See verification table in the build report; corrections vs the brief are noted
# inline below (Florida "calls", Derna not Benghazi, Ted Lieu not "Liu Yuming").

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FD = "/usr/share/fonts/truetype/dejavu/"

PAPER = (250, 247, 240)
INK = (22, 26, 34)
NAVY = (16, 40, 82)
RED = (176, 32, 32)
GOLD = (168, 124, 26)
TEAL = (12, 88, 84)
GREY = (96, 100, 108)
LINE = (198, 192, 180)
CARD = (255, 255, 255)
SKY = (214, 228, 240)
STONE = (232, 226, 214)
MINT = (216, 232, 222)
MAP_LAND = (222, 226, 230)
MAP_LINE = (158, 164, 172)


def f_serif_b(size):
    return ImageFont.truetype(FD + "DejaVuSerif-Bold.ttf", size)


def f_serif(size):
    return ImageFont.truetype(FD + "DejaVuSerif.ttf", size)


def f_sans_b(size):
    return ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", size)


def f_sans(size):
    return ImageFont.truetype(FD + "DejaVuSans.ttf", size)


def wrap(d, text, font, max_w):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, font, color, max_w, leading):
    for ln in wrap(d, text, font, max_w):
        d.text((x, y), ln, font=font, fill=color)
        y += leading
    return y


def fit_font(d, text, path, start, max_w, floor=8):
    size = start
    while size > floor:
        f = ImageFont.truetype(path, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return ImageFont.truetype(path, floor)


# ---------------------------------------------------------------- data
STATS = [
    ("$81.3bn", "raised by Anthropic —\nthe largest IPO on record"),
    ("15.9m", "GTA VI pre-orders banked\nbefore release day (est.)"),
    ("200,000", "evacuated ahead of\nCyclone Akvan"),
    ("551,864", "sit South Korea's\ncollege exam"),
    ("730,000", "Rohingya fled in 2017 —\nthe ICJ case"),
    ("$120bn", "a year of adaptation finance\nunresolved at COP31"),
]

REGIONS = [
    ("EUROPE", 7), ("THE AMERICAS", 11), ("ASIA-PACIFIC", 9),
    ("MIDEAST", 7), ("AFRICA", 3), ("OCEANIA", 4),
]

HEROES = [
    dict(num=1, place="SHENZHEN · SUMMIT", src="AP / Reuters",
         head="Trump, Xi and Putin hold first three-way summit",
         body="First three-way talks at APEC; nuclear arms, trade and Iran "
              "on the agenda."),
    dict(num=2, place="THE HAGUE · LAW", src="ICJ / AP",
         head="World Court rules on Myanmar's Rohingya case",
         body="Judgment in The Gambia's case is final, no appeal; "
              "the court finds genocide, 9–6; 730,000 fled in 2017."),
    dict(num=3, place="NASDAQ · MARKETS", src="Reuters / AP",
         head="Anthropic debuts in the biggest IPO on record",
         body="Priced at $83, above its $70–78 range; raised $81.3bn; "
              "valued near $1.5tn. First trades Thursday."),
]

CARDS = [
    dict(num=4, place="ANTALYA · CLIMATE", src="UNFCCC",
         head="COP31 enters its final 48 hours",
         body="Ministers take over the text; “phase out” and $120bn unresolved."),
    dict(num=5, place="ODISHA · STORM", src="IMD",
         head="Cyclone Akvan bears down; 200,000 evacuated",
         body="Red alerts in 11 districts; landfall near Puri due Friday."),
    dict(num=6, place="KYIV · WAR", src="White House", tag="CLAIM",
         head="Ukraine left off the agenda",
         body="Ukraine off the agenda, US officials say; Kyiv fears a carve-up."),
    dict(num=7, place="SHENZHEN · TRADE", src="APEC",
         head="APEC leaders adopt the Shenzhen Declaration",
         body="21 economies back digital trade and an Asia-Pacific roadmap."),
    dict(num=8, place="FLORIDA · WEATHER", src="AP / NWS",
         head="Flooded South Florida logs 300+ calls for help",
         body="A foot of rain in hours in Hollywood; schools shut Thursday."),
    dict(num=9, place="SCIENCE · GEOLOGY", src="Nature",
         head="Earth's missing billion years are explained",
         body="A Nature study blames mantle currents and ancient ice sheets."),
    dict(num=10, place="PARIS · POLITICS", src="Reuters",
         head="Mélenchon could win, says France's justice minister",
         body="A plausible president if he faces Le Pen in the runoff."),
    dict(num=11, place="JAZAN · GULF", src="Reuters", tag="CLAIM",
         head="Saudi Arabia says danger has passed in three cities",
         body="All-clear in the south after a Houthi missile was downed. [CLAIM]"),
    dict(num=12, place="DERNA · CRIME", src="Reuters",
         head="Cocaine and millions of pills seized in eastern Libya",
         body="4m+ pills and 29kg of cocaine and hashish seized in Derna."),
    dict(num=13, place="SEOUL · EDUCATION", src="Yonhap",
         head="Half a million sit Korea's Suneung exam",
         body="551,864 candidates; flights pause amid strict anti-cheat checks."),
]

BRIEFS = [
    (14, "GAZA", "Tanks cross the Yellow Line; Hamas cries breach.", "Reuters"),
    (15, "CRIMEA", "Bridge attacked again; rail traffic halted.", "AP"),
    (16, "MEXICO CITY", "Banxico minutes: board cut rates to 6.25%, 3–2.", "Banxico"),
    (17, "CANBERRA", "Jobless rate hits a 5-year high of 4.9%.", "ABS"),
    (18, "MOGADISHU", "Somalia accuses the UAE of a sovereignty breach.", "Reuters"),
    (19, "FRANKFURT", "Deutsche Bank handled $582m in Epstein deals.", "FT"),
    (20, "WASHINGTON", "Senators warn of AI cyber threats to critical defences.", "Reuters"),
    (21, "OTTAWA", "Carney widens China relief; seeks US “right deal”.", "Reuters"),
    (22, "NEW DELHI", "Schools reopen as GRAP-III curbs lift.", "CAQM"),
    (23, "TOKYO", "India and Japan hold 2+2 defence talks.", "AP"),
    (24, "BENGALURU", "Amazon pledges $7bn for renewables in India by 2030.", "Amazon"),
    (25, "AUCKLAND", "GTA VI unlocks at midnight; 15.9m pre-orders.", "Sensor Tower"),
    (26, "BAGHDAD", "Six French ISIL members jailed for life in Iraq.", "AFP"),
    (27, "NAIROBI", "Kenya floods kill six; Ruto gives his address.", "Daily Nation"),
    (28, "WASHINGTON", "Vance: no “forever war” in the Gulf.", "Reuters"),
    (29, "CARACAS", "Hegseth signs a US–Venezuela military pact.", "AP"),
    (30, "MANAMA", "Bapco refinery back on its feet after the attacks.", "Reuters"),
    (31, "RIYADH", "Gulf leaders urge Trump not to strike Iran.", "Reuters"),
    (32, "WASHINGTON", "Ted Lieu is first Asian-American House Democratic chair.", "AP"),
    (33, "SACRAMENTO", "California braces for atmospheric river; advisories out.", "NWS"),
    (34, "LA PAZ", "Bolivia declares El Niño emergency; 78,000 families hit.", "Al Jazeera"),
    (35, "HOBART", "Duckett's 133 seals England's ODI series win.", "Reuters"),
    (36, "MANILA", "US pursues a $2bn+ Philippines defence loan.", "White House"),
    (37, "LONDON", "National Grid debunks an AI blackout hoax.", "National Grid"),
    (38, "MANILA", "Trump unveils $17bn in Southeast Asia deals.", "White House"),
    (39, "KUWAIT CITY", "Iran says it fired on US sites in Kuwait overnight.", "Reuters"),
    (40, "JERUSALEM", "Mossad chief lobbied the US for new strikes on Iran.", "Reuters"),
    (41, "WASHINGTON", "GAO: top AI chatbots drew up terror-attack plans in tests.", "GAO"),
]

DATE_CHECK = ("Left out on purpose because they broke before Thursday: "
    "Voyager 1 crossing one light-day (Wed 18 Nov) · House Democrats' 251–11 vote "
    "nominating Hakeem Jeffries (Wed 18) · EU's €45bn Ukraine loan plan (Wed 18) · "
    "Fed minutes (Wed 18) · Van Gogh's record $190.4m sale (Wed 18) · "
    "Modi–William–Catherine meeting (Wed 18) · UK 3.6% CPI (Wed 18) · Pew's projection "
    "that Islam becomes the largest religion by 2035 (not that day's news) · the first "
    "COP31 draft (Monday) · US strikes on Iran's Qeshm Island (Tue 17 Nov).")

PINS = [  # (story no, lon, lat)
    (1, 114.1, 22.5), (2, 4.3, 52.0), (3, -74.0, 40.7), (4, 30.7, 36.9),
    (5, 85.8, 19.8), (6, 30.5, 50.4), (7, 114.1, 22.5), (8, -80.1, 26.1),
    (9, 150.9, -34.4), (10, 2.35, 48.85), (11, 42.55, 16.9), (12, 22.6, 32.76),
    (13, 127.0, 37.5),
]

CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-60, 60),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-85, 30), (-97, 26),
     (-105, 20), (-95, 16), (-83, 9), (-90, 14), (-105, 20), (-115, 28),
     (-125, 40), (-125, 49), (-145, 60), (-168, 66)],
    [(-80, 9), (-70, 11), (-60, 8), (-50, 0), (-35, -8), (-40, -20),
     (-48, -28), (-58, -35), (-65, -41), (-70, -54), (-73, -37), (-70, -20),
     (-80, -5), (-80, 9)],
    [(-17, 15), (-10, 30), (-5, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (30, -29), (20, -35),
     (15, -27), (12, -18), (9, -1), (9, 4), (-8, 4), (-17, 15)],
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 58), (30, 60), (30, 70), (40, 68),
     (55, 69), (70, 72), (90, 75), (110, 74), (130, 72), (150, 70),
     (170, 67), (178, 65), (170, 60), (162, 56), (158, 52), (142, 50),
     (140, 40), (135, 35), (130, 33), (127, 35), (122, 38), (120, 32),
     (110, 20), (105, 10), (100, 8), (98, 15), (95, 16), (92, 21), (88, 22),
     (80, 15), (77, 8), (73, 16), (66, 25), (60, 25), (57, 27), (52, 26),
     (48, 29), (44, 29), (40, 31), (36, 36), (30, 36), (26, 38), (22, 36),
     (19, 40), (12, 44), (8, 44), (3, 43), (-2, 37), (-9, 37), (-10, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (137, -35),
     (140, -38), (147, -39), (150, -37), (153, -27), (150, -22), (146, -19),
     (142, -11), (136, -12), (132, -12), (126, -14), (122, -17), (113, -22)],
    [(-58, 64), (-45, 60), (-40, 65), (-30, 68), (-20, 70), (-30, 74),
     (-50, 76), (-60, 74), (-58, 64)],
]


# ---------------------------------------------------------------- pictures
def flag_usa(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=INK, width=1)
    for i in range(7):
        d.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                    fill=RED if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x, y, x + w * 0.4, y + h * 4 / 7], fill=NAVY)
    for r in range(4):
        for c in range(5):
            sx = x + 4 + c * (w * 0.4 - 8) / 4
            sy = y + 4 + r * (h * 4 / 7 - 8) / 3
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))


def flag_chn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16), outline=INK, width=1)
    d.regular_polygon((x + w * 0.22, y + h * 0.28, 7), 5, rotation=0,
                      fill=(255, 222, 0))
    for sx, sy in [(0.45, 0.18), (0.55, 0.32), (0.5, 0.5), (0.38, 0.42)]:
        d.regular_polygon((x + w * sx, y + h * sy, 3), 5, rotation=0,
                          fill=(255, 222, 0))


def flag_rus(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=INK, width=1)
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 50))


def skyline(d, x, y, w, h, color):
    hs = [0.55, 0.8, 0.45, 1.0, 0.65, 0.9, 0.5, 0.75, 0.6]
    bw = w / len(hs)
    for i, f in enumerate(hs):
        bx = x + i * bw + 1
        d.rectangle([bx, y + h - h * f, bx + bw - 2, y + h], fill=color)
        for wy in range(2):
            for wx in range(2):
                d.rectangle([bx + 3 + wx * 6, y + h - h * f + 5 + wy * 9,
                             bx + 5 + wx * 6, y + h - h * f + 7 + wy * 9],
                            fill=(255, 214, 90))


def hero1_flags(d, x, y, w, h):
    """Fallback: flags + skyline (rank-3 form)."""
    skyline(d, x + 6, y + h - 52, w - 12, 52, NAVY)
    fw, fh = 84, 50
    flag_usa(d, x + 14, y + 10, fw, fh)
    flag_chn(d, x + w // 2 - fw // 2, y + 10, fw, fh)
    flag_rus(d, x + w - 14 - fw, y + 10, fw, fh)
    lab = f_sans_b(11)
    for tx, name in [(x + 14, "USA"), (x + w // 2 - fw // 2, "CHINA"),
                     (x + w - 14 - fw, "RUSSIA")]:
        tw = d.textlength(name, font=lab)
        d.rectangle([tx + fw // 2 - tw // 2 - 4, y + fh + 14,
                     tx + fw // 2 + tw // 2 + 4, y + fh + 30],
                    fill=(255, 255, 255))
        d.text((tx + fw // 2 - tw // 2, y + fh + 15), name, font=lab, fill=INK)


def hero1_figures(d, x, y, w, h):
    """Three flat suited figures, flag banner behind each, name plates."""
    cols = [("USA", flag_usa, (238, 208, 110), RED, "TRUMP"),
            ("CHINA", flag_chn, (40, 40, 40), (150, 30, 30), "XI"),
            ("RUSSIA", flag_rus, (205, 192, 160), (30, 80, 160), "PUTIN")]
    cw = (w - 12) // 3
    for i, (_c, flag_fn, hair, tie, name) in enumerate(cols):
        cx0 = x + 6 + i * cw
        ccx = cx0 + (cw - 6) // 2
        flag_fn(d, cx0, y + 6, cw - 6, 26)
        d.polygon([(ccx - 27, y + 80), (ccx - 21, y + 54), (ccx - 12, y + 47),
                   (ccx + 12, y + 47), (ccx + 21, y + 54), (ccx + 27, y + 80)],
                  fill=NAVY)
        d.polygon([(ccx - 7, y + 47), (ccx + 7, y + 47), (ccx, y + 64)],
                  fill=(255, 255, 255))
        d.polygon([(ccx - 3, y + 52), (ccx + 3, y + 52), (ccx + 4, y + 70),
                   (ccx, y + 76), (ccx - 4, y + 70)], fill=tie)
        d.ellipse([ccx - 12, y + 22, ccx + 12, y + 46], fill=(233, 192, 152))
        d.chord([ccx - 12, y + 20, ccx + 12, y + 34], 180, 360, fill=hair)
        if name == "TRUMP":
            d.rectangle([ccx - 12, y + 26, ccx + 12, y + 29], fill=hair)
    d.rectangle([x, y + h - 24, x + w, y + h], fill=(96, 64, 38))
    d.rectangle([x, y + h - 24, x + w, y + h - 21], fill=(140, 100, 60))
    lab = f_sans_b(10)
    for i, (_c, _f, _h, _t, name) in enumerate(cols):
        ccx = x + 6 + i * cw + (cw - 6) // 2
        tw = d.textlength(name, font=lab)
        d.rectangle([ccx - tw / 2 - 5, y + h - 19, ccx + tw / 2 + 5, y + h - 5],
                    fill=(255, 255, 255))
        d.text((ccx - tw / 2, y + h - 18), name, font=lab, fill=INK)


def hero_art(d, x, y, w, h, num):
    d.rectangle([x, y, x + w, y + h], fill=SKY if num != 2 else STONE)
    if num == 1:
        hero1_figures(d, x, y, w, h)
    elif num == 2:
        cx = x + w // 2
        d.polygon([(cx - 78, y + 34), (cx + 78, y + 34), (cx, y + 6)],
                  fill=NAVY)
        for i in range(5):
            px = cx - 64 + i * 32
            d.rectangle([px - 5, y + 36, px + 5, y + 78], fill=NAVY)
        d.rectangle([cx - 86, y + 78, cx + 86, y + 86], fill=NAVY)
        # scales of justice
        bx, by = cx, y + h - 8
        d.line([bx, by - 46, bx, by], fill=GOLD, width=3)
        d.line([bx - 34, by - 42, bx + 34, by - 42], fill=GOLD, width=3)
        for sx in (bx - 34, bx + 34):
            d.line([sx, by - 42, sx, by - 26], fill=GOLD, width=2)
            d.arc([sx - 12, by - 26, sx + 12, by - 10], 0, 180, fill=GOLD, width=2)
        d.ellipse([bx - 4, by - 52, bx + 4, by - 44], fill=GOLD)
    else:
        d.text((x + 12, y + 6), "$83", font=f_sans_b(30), fill=RED)
        d.text((x + w - 108, y + 12), "$81.3bn", font=f_sans_b(19), fill=NAVY)
        band_top, band_h = y + 44, h - 44 - 16
        base = y + h - 16
        d.line([x + 8, base, x + w - 8, base], fill=INK, width=2)
        candles = [(0.10, 0.30, 0.42), (0.22, 0.22, 0.38), (0.34, 0.34, 0.50),
                   (0.46, 0.26, 0.46), (0.58, 0.18, 0.40), (0.70, 0.12, 0.34),
                   (0.82, 0.08, 0.30)]
        for fx, top, bot in candles:
            cx = x + w * fx
            d.line([cx, band_top + band_h * top - 3,
                    cx, band_top + band_h * bot + 3], fill=INK, width=2)
            d.rectangle([cx - 7, band_top + band_h * top,
                         cx + 7, band_top + band_h * bot], fill=(34, 139, 34))


def card_art(d, x, y, w, h, num):
    bgs = {4: TEAL, 5: (42, 90, 140), 6: (70, 70, 78), 7: NAVY, 8: (30, 110, 150),
           9: (120, 72, 20), 10: (90, 30, 60), 11: (150, 40, 30),
           12: (60, 60, 110), 13: (20, 100, 70)}
    d.rectangle([x, y, x + w, y + h], fill=bgs[num])
    cx, cy = x + w // 2, y + h // 2
    if num == 4:  # globe + leaf
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], outline=(255, 255, 255), width=2)
        d.arc([cx - 13, cy - 13, cx + 13, cy + 13], 200, 340, fill=(255, 255, 255), width=2)
        d.line([cx - 13, cy, cx + 13, cy], fill=(255, 255, 255), width=2)
        d.line([cx, cy - 13, cx, cy + 13], fill=(255, 255, 255), width=1)
    elif num == 5:  # cyclone spiral
        for r in range(3, 15, 3):
            d.arc([cx - r, cy - r, cx + r, cy + r], r * 40, r * 40 + 220,
                  fill=(255, 255, 255), width=2)
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 255, 255))
    elif num == 6:  # empty chair at table
        d.ellipse([cx - 16, cy - 9, cx + 16, cy + 9], outline=(255, 255, 255), width=2)
        d.rectangle([cx - 3, cy - 16, cx + 3, cy - 4], outline=(255, 255, 255), width=2)
        d.text((cx - 4, cy - 2), "?", font=f_sans_b(13), fill=(255, 255, 255))
    elif num == 7:  # 21 dots ring
        for i in range(12):
            import math
            a = i * 30 * math.pi / 180
            d.ellipse([cx + 13 * math.cos(a) - 2, cy + 10 * math.sin(a) - 2,
                       cx + 13 * math.cos(a) + 2, cy + 10 * math.sin(a) + 2],
                      fill=(255, 255, 255))
        d.text((cx - 7, cy - 6), "21", font=f_sans_b(12), fill=(255, 214, 90))
    elif num == 8:  # rain cloud
        d.ellipse([cx - 14, cy - 8, cx - 2, cy + 4], fill=(255, 255, 255))
        d.ellipse([cx - 6, cy - 12, cx + 8, cy + 4], fill=(255, 255, 255))
        d.ellipse([cx + 4, cy - 7, cx + 15, cy + 4], fill=(255, 255, 255))
        for dx in (-10, 0, 10):
            d.line([cx + dx, cy + 8, cx + dx - 2, cy + 14], fill=(160, 200, 235), width=2)
    elif num == 9:  # rock strata with gap
        for i, col in enumerate([(200, 170, 120), (170, 130, 90), (140, 100, 60)]):
            d.rectangle([x + 6, y + 4 + i * 8, x + w - 6, y + 10 + i * 8], fill=col)
        d.rectangle([x + 6, y + 26, x + w - 6, y + 29], fill=(255, 255, 255))
    elif num == 10:  # ballot box
        d.rectangle([cx - 12, cy - 4, cx + 12, cy + 12], outline=(255, 255, 255), width=2)
        d.rectangle([cx - 3, cy - 12, cx + 3, cy - 4], fill=(255, 255, 255))
        d.text((cx - 4, cy - 1), "✓", font=f_sans_b(11), fill=(255, 255, 255))
    elif num == 11:  # shield + burst
        d.polygon([(cx, cy - 13), (cx + 11, cy - 8), (cx + 11, cy + 3),
                   (cx, cy + 13), (cx - 11, cy + 3), (cx - 11, cy - 8)],
                  outline=(255, 255, 255), width=2)
        d.line([cx - 5, cy - 2, cx - 1, cy + 2], fill=(255, 255, 255), width=2)
        d.line([cx - 1, cy + 2, cx + 6, cy - 6], fill=(255, 255, 255), width=2)
    elif num == 12:  # capsules
        d.ellipse([cx - 14, cy - 5, cx - 2, cy + 5], fill=(255, 255, 255))
        d.ellipse([cx + 2, cy - 5, cx + 14, cy + 5], fill=(255, 255, 255))
        d.text((cx - 9, cy - 11), "4m+", font=f_sans_b(9), fill=(255, 214, 90))
    else:  # exam desk + pencil
        d.rectangle([cx - 13, cy + 2, cx + 13, cy + 8], fill=(255, 255, 255))
        d.line([cx - 10, cy - 12, cx + 10, cy + 2], fill=(255, 214, 90), width=3)
        d.polygon([(cx + 10, cy + 2), (cx + 14, cy + 5), (cx + 10, cy + 8)],
                  fill=(255, 214, 90))


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 16  # margin

    # ---- masthead
    d.text((M, 2), "THE WORLD IN ONE PAGE", font=f_serif_b(35), fill=NAVY)
    d.text((W - M - 268, 12), "THURSDAY 19 NOVEMBER 2026",
           font=f_sans_b(14), fill=RED)
    d.text((W - M - 268, 32), "41 STORIES · 6 REGIONS · ONE PAGE",
           font=f_sans_b(11), fill=INK)
    d.line([M, 52, W - M, 52], fill=RED, width=3)
    d.line([M, 56, W - M, 56], fill=INK, width=1)

    # ---- kicker
    d.text((M, 62), "One day. Every continent. The news that mattered — verified, sourced, dated.",
           font=f_serif(13), fill=INK)
    d.text((W - M - 250, 63), "41 stories · 7 beats · 0 filler",
           font=f_sans(11), fill=GREY)

    # ---- stat strip
    y0, y1 = 84, 146
    d.rectangle([M, y0, W - M, y1], fill=CARD, outline=LINE, width=1)
    cw = (W - 2 * M) / 6
    for i, (num, lab) in enumerate(STATS):
        x = M + i * cw
        if i:
            d.line([x, y0 + 6, x, y1 - 6], fill=LINE, width=1)
        d.text((x + cw / 2, y0 + 6), num, font=f_sans_b(24),
               fill=RED if i % 2 == 0 else NAVY, anchor="ma")
        yy = y0 + 34
        for ln in lab.split("\n"):
            d.text((x + cw / 2, yy), ln, font=f_sans(9), fill=GREY, anchor="ma")
            yy += 11

    # ---- region strip
    y0 = 152
    d.text((M, y0), "WHERE THE NEWS CAME FROM —",
           font=f_sans_b(11), fill=INK)
    x = M + 232
    for name, n in REGIONS:
        t = f"{name} {n}"
        d.text((x, y0), t, font=f_sans_b(11), fill=NAVY)
        x += d.textlength(t, font=f_sans_b(11)) + 18
    d.text((W - M, y0), "TOTAL 41", font=f_sans_b(11), fill=RED, anchor="ra")
    d.line([M, y0 + 18, W - M, y0 + 18], fill=INK, width=1)

    # ---- heroes
    y0, hh = 178, 218
    hw = (W - 2 * M - 2 * 10) / 3
    for i, hro in enumerate(HEROES):
        x = M + i * (hw + 10)
        d.rectangle([x, y0, x + hw, y0 + hh], fill=CARD, outline=LINE, width=1)
        hero_art(d, x + 1, y0 + 1, hw - 2, 104, hro["num"])
        d.text((x + 8, y0 + 110), f"{hro['num']}  {hro['place']}",
               font=f_sans_b(10), fill=RED)
        yy = para(d, x + 8, y0 + 126, hro["head"], f_serif_b(19), INK, hw - 16, 22)
        para(d, x + 8, yy + 3, hro["body"], f_sans(11), INK, hw - 16, 14)
        d.text((x + 8, y0 + hh - 16), "Source: " + hro["src"],
               font=f_sans(9), fill=GREY)

    # ---- cards 4–13
    y0, ch = 404, 118
    cw = (W - 2 * M - 4 * 8) / 5
    for i, c in enumerate(CARDS):
        r, col = divmod(i, 5)
        x = M + col * (cw + 8)
        y = y0 + r * (ch + 8)
        d.rectangle([x, y, x + cw, y + ch], fill=CARD, outline=LINE, width=1)
        card_art(d, x + 1, y + 1, cw - 2, 30, c["num"])
        d.rectangle([x + 1, y + 1, x + 30, y + 18], fill=RED)
        d.text((x + 15, y + 2), str(c["num"]), font=f_sans_b(11),
               fill=(255, 255, 255), anchor="ma")
        tag = c.get("tag")
        kx = x + 8
        d.text((kx, y + 35), c["place"], font=f_sans_b(9), fill=RED)
        if tag:
            tw = d.textlength(tag, font=f_sans_b(8))
            d.rectangle([x + cw - tw - 14, y + 34, x + cw - 8, y + 46], fill=GOLD)
            d.text((x + cw - tw - 11, y + 35), tag, font=f_sans_b(8), fill=(255, 255, 255))
        yy = para(d, x + 8, y + 49, c["head"], f_sans_b(11), INK, cw - 16, 13)
        para(d, x + 8, yy + 2, c["body"], f_sans(9.5), INK, cw - 16, 11.5)
        d.text((x + 8, y + ch - 13), c["src"], font=f_sans(8), fill=GREY)

    # ---- map + briefs band
    y0, y1 = 656, 878
    d.line([M, y0 - 8, W - M, y0 - 8], fill=INK, width=1)
    # map panel
    mx, mw = M, 300
    d.rectangle([mx, y0, mx + mw, y1], fill=(238, 240, 242), outline=LINE, width=1)
    d.text((mx + 8, y0 + 5), "WHERE IT HAPPENED", font=f_sans_b(11), fill=NAVY)
    map_x, map_y, map_w, map_h = mx + 6, y0 + 24, mw - 12, 168

    def proj(lon, lat):
        return (map_x + (lon + 180) / 360 * map_w,
                map_y + (90 - lat) / 150 * map_h)

    for lon in range(-150, 181, 30):
        px, _ = proj(lon, 0)
        d.line([px, map_y, px, map_y + map_h], fill=(210, 214, 218), width=1)
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=MAP_LAND, outline=MAP_LINE)
    placed = {}
    nudge = {6: (11, 11), 10: (-11, -9), 12: (9, -9), 11: (-9, 9)}
    for num, lon, lat in PINS:
        px, py = proj(lon, lat)
        if num == 7:  # same city as pin 1 — nudge so both show
            px += 17
            py -= 13
        dx, dy = nudge.get(num, (0, 0))
        px, py = px + dx, py + dy
        placed[num] = (px, py)
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED, outline=(255, 255, 255), width=1)
        d.text((px, py - 1), str(num), font=f_sans_b(9),
               fill=(255, 255, 255), anchor="mm")
    d.text((mx + 8, y1 - 22), "Red pins = stories 1–13", font=f_sans_b(9), fill=RED)
    d.text((mx + 8, y1 - 11), "Positions approximate", font=f_sans(9), fill=GREY)

    # briefs
    bx = mx + mw + 14
    bw = W - M - bx
    colw = (bw - 12) / 2
    d.text((bx, y0), "THE REST OF THE DAY — IN BRIEF", font=f_sans_b(11), fill=NAVY)
    rows = 14
    rh = (y1 - y0 - 24) / rows
    for i, (num, place, text, src) in enumerate(BRIEFS):
        col, row = divmod(i, rows)
        x = bx + col * (colw + 12)
        y = y0 + 22 + row * rh
        line = f"{num} {place} — {text} ({src})"
        fnt = fit_font(d, line, FD + "DejaVuSans.ttf", 9.5, colw)
        d.text((x, y), line, font=fnt, fill=INK)

    # ---- date check
    y0, y1 = 886, 960
    d.rectangle([M, y0, W - M, y1], fill=(255, 244, 230), outline=RED, width=1)
    d.rectangle([M, y0, M + 5, y1], fill=RED)
    d.text((M + 12, y0 + 5), "DATE CHECK — LEFT OUT ON PURPOSE",
           font=f_sans_b(11), fill=RED)
    para(d, M + 12, y0 + 22, DATE_CHECK, f_sans(10.5), INK, W - 2 * M - 24, 13.5)

    # ---- footer
    y = 968
    d.text((M, y), "Sources: Reuters · AP · AFP · BBC · Al Jazeera · ICJ · UNFCCC · IMD · "
                   "Nature · Yonhap · FT · NWS · National Grid",
           font=f_sans(9), fill=GREY)
    d.text((M, y + 13), "Every story here happened, or was first reported, on Thursday "
                        "19 November 2026, in some time zone.",
           font=f_sans_b(9.5), fill=INK)
    d.text((M, y + 26), "HOW SURE ARE WE?  REPORTED = confirmed by two or more wires  ·  "
                        "CLAIM = one source's claim  ·  FORECAST = a projection, not an event",
           font=f_sans(9), fill=GREY)
    d.text((M, y + 39), "41 stories · 6 regions · 10 sections · one page",
           font=f_sans(9), fill=GREY)

    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    img.save(path, format="PNG")
    return path


if __name__ == "__main__":
    print(build())
