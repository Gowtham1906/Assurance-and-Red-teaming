"""Render the Capability 4 architecture diagram to PNG using Pillow (no system libs)."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 900
BG = (15, 22, 38)
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)


def font(size, bold=False):
    names = (["seguisb.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"])
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def ctext(x, y, s, size, color, bold=False):
    f = font(size, bold)
    w = d.textlength(s, font=f)
    d.text((x - w / 2, y), s, fill=color, font=f)


def ltext(x, y, s, size, color, bold=False):
    d.text((x, y), s, fill=color, font=font(size, bold))


def box(x, y, w, h, fill, outline, width=2, r=12):
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill, outline=outline, width=width)


def arrow(x1, y1, x2, y2, color=(159, 182, 224), width=3):
    d.line([x1, y1, x2, y2], fill=color, width=width)
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    L = 12
    for da in (2.6, -2.6):
        d.line([x2, y2, x2 - L * math.cos(ang + da), y2 - L * math.sin(ang + da)], fill=color, width=width)


# ---- title ----
ctext(640, 24, "Capability 4 - Assurance & Red-Teaming", 30, (255, 255, 255), True)
ctext(640, 62, "End goal: a repeatable \"SAFE TO RELEASE?\" decision for our AI, with evidence", 16, (143, 180, 255))

# ---- AI under test ----
box(40, 120, 220, 150, (21, 34, 60), (63, 111, 209))
ctext(150, 132, "AI UNDER TEST", 17, (255, 255, 255), True)
box(60, 166, 180, 38, (29, 45, 77), (47, 73, 118))
ctext(150, 176, "BoK  (RAG Q&A)   T2", 13, (207, 224, 255))
box(60, 212, 180, 38, (29, 45, 77), (47, 73, 118))
ctext(150, 222, "Agent (tools)    T1", 13, (207, 224, 255))

# ---- Inputs ----
box(330, 110, 250, 175, (21, 34, 60), (63, 111, 209))
ctext(455, 120, "INPUTS", 17, (255, 255, 255), True)
ltext(348, 150, "- Golden dataset", 13, (207, 224, 255))
ltext(362, 170, "(questions + known answers)", 11, (138, 160, 200))
ltext(348, 196, "- Sealed set (secret, anti-cheat)", 13, (207, 224, 255))
ltext(348, 222, "- Policy file (the rules)", 13, (207, 224, 255))
ltext(348, 248, "held by the assurance team", 11, (138, 160, 200))

# ---- Harness ----
box(650, 100, 330, 200, (22, 42, 34), (59, 189, 126))
ctext(815, 110, "THE HARNESS  (conductor)", 18, (255, 255, 255), True)
ltext(668, 140, "for each question:", 13, (191, 231, 210))
ltext(682, 164, "1. run the AI", 13, (234, 255, 232))
box(670, 190, 290, 44, (19, 53, 31), (47, 125, 82))
ltext(684, 196, "2. DETERMINISTIC checks D01-D11", 13, (143, 240, 180), True)
ltext(684, 214, "fixed rules  -  HARD gate", 11, (127, 214, 160))
box(670, 240, 290, 46, (43, 40, 56), (138, 106, 214))
ltext(684, 246, "3. LLM JUDGES", 13, (201, 182, 255), True)
ltext(684, 265, "quality scores  -  SOFT signal", 11, (176, 154, 224))

# ---- MLflow ----
box(330, 360, 650, 110, (19, 42, 63), (42, 166, 214), 3)
ctext(655, 374, "MLflow - SYSTEM OF RECORD", 19, (255, 255, 255), True)
ctext(655, 404, "stores: traces - runs - metrics - datasets - baseline", 14, (191, 230, 245))
ctext(655, 430, "the webpage you saw at http://localhost:5000", 13, (127, 196, 224))

# ---- Gate ----
box(330, 520, 650, 150, (46, 36, 54), (217, 140, 255))
ctext(655, 532, "THE GATE  (decision)", 19, (255, 255, 255), True)
ctext(655, 560, "compares to BASELINE using statistics, then decides:", 13, (228, 200, 255))
box(356, 588, 290, 30, (58, 31, 34), (224, 102, 102), 1, 6)
ltext(370, 594, "deterministic check failed  ->  BLOCK", 12, (255, 179, 179))
box(356, 624, 290, 30, (58, 51, 31), (224, 192, 102), 1, 6)
ltext(370, 630, "judge score dropped a lot  ->  REVIEW", 12, (255, 230, 163))
box(664, 588, 290, 30, (31, 58, 40), (102, 224, 138), 1, 6)
ltext(678, 594, "all good  ->  PASS", 12, (174, 240, 196))
box(664, 624, 290, 30, (58, 31, 34), (224, 102, 102), 1, 6)
ltext(678, 630, "broken / unknown  ->  FAIL (fail closed)", 12, (255, 179, 179))

# ---- Report ----
box(330, 720, 650, 120, (42, 42, 22), (214, 194, 59))
ctext(655, 732, "THE REPORT", 19, (255, 255, 255), True)
ctext(655, 762, "JUnit XML -> CI pipeline blocks / allows the release", 14, (240, 236, 192))
ctext(655, 786, "Markdown / PDF -> humans: results - severity - evidence", 14, (240, 236, 192))
ctext(655, 812, "RELEASE RECOMMENDATION", 14, (255, 224, 102), True)

# ---- Red team ----
box(1020, 360, 220, 310, (51, 28, 28), (224, 122, 95))
ctext(1130, 372, "RED-TEAMING", 17, (255, 255, 255), True)
ctext(1130, 398, "attack the UNEXPECTED", 12, (243, 194, 179))
ltext(1040, 428, "- 50 attack cases (Nov)", 12, (246, 210, 198))
ltext(1040, 454, "- prompt injection", 12, (246, 210, 198))
ltext(1040, 480, "- data / PII leakage", 12, (246, 210, 198))
ltext(1040, 506, "- jailbreaks", 12, (246, 210, 198))
ltext(1040, 532, "- tool misuse", 12, (246, 210, 198))
ltext(1040, 566, "severity scored:", 12, (243, 194, 179))
ltext(1054, 588, "Critical>High>Med>Low", 11, (255, 179, 179))
ltext(1040, 622, "feeds the same gate", 12, (243, 194, 179))

# ---- Key design rule box ----
box(40, 320, 250, 150, (20, 27, 46), (42, 55, 88), 1, 10)
ltext(58, 328, "Key design rule", 14, (255, 255, 255), True)
ltext(58, 354, "Deterministic = HARD gate", 12, (143, 240, 180), True)
ltext(72, 372, "same every time - free - blocks", 11, (127, 214, 160))
ltext(58, 396, "Judges = SOFT signal", 12, (201, 182, 255), True)
ltext(72, 414, "drift - cost - only warn", 11, (176, 154, 224))
ltext(58, 440, "A judge blocks only if stats prove it", 11, (159, 182, 224))

# ---- Assurance vs Red bottom labels ----
ctext(150, 628, "ASSURANCE", 13, (143, 240, 180), True)
ctext(150, 648, "test the EXPECTED", 11, (127, 214, 160))
ctext(150, 688, "RED-TEAM", 13, (243, 194, 179), True)
ctext(150, 708, "attack the UNEXPECTED", 11, (232, 160, 138))
ctext(150, 748, "both -> record -> gate -> report", 11, (159, 182, 224))

# ---- arrows ----
arrow(260, 195, 326, 195)                 # AI -> Inputs
arrow(580, 190, 646, 190)                 # Inputs -> Harness
d.line([150, 270, 150, 415, 326, 415], fill=(111, 136, 184), width=2)  # AI traces -> MLflow
arrow(300, 415, 326, 415, (111, 136, 184), 2)
arrow(815, 300, 815, 356)                 # Harness -> MLflow
arrow(655, 470, 655, 516)                 # MLflow -> Gate
arrow(655, 670, 655, 716)                 # Gate -> Report
d.line([1020, 500, 1000, 500, 1000, 560, 984, 560], fill=(224, 122, 95), width=2)  # Red -> Gate
arrow(1000, 560, 984, 560, (224, 122, 95), 2)

img.save("docs/architecture-diagram.png")
print("PNG_OK docs/architecture-diagram.png", img.size)
