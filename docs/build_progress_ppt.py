"""
Build a Qualbot progress presentation (.pptx) using only the Python standard
library. A .pptx file is a ZIP archive of XML parts that follow the Office
Open XML (OOXML) spec, so we emit the minimum set of parts PowerPoint,
Keynote and LibreOffice all accept.

Run:
    python3 build_progress_ppt.py
Produces:
    Qualbot_Progress.pptx (next to this script)
"""
from __future__ import annotations

import os
import zipfile
from html import escape
from typing import Iterable

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Qualbot_Progress.pptx")

# ----------------------------- slide content ----------------------------- #
# Each slide = (title, [bullet_or_paragraph, ...]). A bullet beginning with
# "## " is rendered as a sub-heading (no bullet marker). "- " prefix becomes
# an indented sub-bullet.
SLIDES: list[tuple[str, list[str]]] = [
    (
        "QualBot",
        [
            "## AI-Powered Lead Qualification Chatbot",
            "Progress Report  •  October 2026",
            "",
            "A conversational agent that qualifies sales leads in real time",
            "using Google Gemini + the BANT framework.",
        ],
    ),
    (
        "The Problem",
        [
            "Sales teams waste hours on unqualified website visitors.",
            "Manual BANT discovery (Budget, Authority, Need, Timeline) is slow and inconsistent.",
            "Hot leads cool off before anyone follows up.",
            "",
            "## Goal",
            "Automate the first-touch qualification conversation and route only hot leads to humans.",
        ],
    ),
    (
        "Our Solution — QualBot",
        [
            "A chat widget that talks to visitors, extracts BANT data from their replies, and scores the lead live.",
            "",
            "Key ideas:",
            "- Conversational: one BANT question per turn, friendly tone.",
            "- Structured: Gemini returns a strict Pydantic BANT schema (not free text).",
            "- Actionable: hot leads get a Calendly booking button automatically.",
            "- Observable: every transcript + score is stored for the sales dashboard.",
        ],
    ),
    (
        "Tech Stack",
        [
            "## Backend",
            "FastAPI  •  Pydantic  •  SQLite  •  Uvicorn",
            "Google Gemini (google-genai)  •  python-dotenv",
            "",
            "## Frontend",
            "React 18  •  Vite 6  •  Tailwind CSS 4",
            "LocalStorage session persistence",
            "",
            "## Dev / Ops",
            "Virtualenv, .env secrets, CORS allow-list, Git",
        ],
    ),
    (
        "System Architecture",
        [
            "Visitor  →  React ChatWidget  →  POST /chat (FastAPI)",
            "",
            "Inside /chat the backend:",
            "- Loads prior transcript from SQLite (db.py).",
            "- Calls Gemini twice: one reply, one structured BANT extraction.",
            "- Merges new BANT answers with saved ones (never overwrites with 'unknown').",
            "- Scores the lead and classifies tier (hot / warm / cold).",
            "- Persists messages + lead row, routes hot leads to Calendly.",
            "",
            "Dashboard reads GET /leads and GET /leads/{session_id} for transcripts.",
        ],
    ),
    (
        "BANT Scoring Model",
        [
            "## Weights (total 100)",
            "Need 30  •  Budget 25  •  Timeline 25  •  Authority 20",
            "",
            "## Category points (multiplier applied to weight)",
            "- Budget: confirmed 1.0 / limited 0.6 / none 0.0",
            "- Authority: decision_maker 1.0 / influencer 0.6",
            "- Need: clear 1.0 / vague 0.6",
            "- Timeline: immediate 1.0 / soon 0.6 / long_term 0.3",
            "",
            "## Tiering",
            "Hot ≥ 70   •   Warm 40–69   •   Cold < 40",
        ],
    ),
    (
        "Features Delivered",
        [
            "Conversational chat with Gemini, with graceful fallback reply when the API is down.",
            "Structured BANT extraction via Pydantic schema + response_mime_type=application/json.",
            "Multi-model fallback: tries gemini-3.5-flash → 2.5-flash → gemma, with retry.",
            "SQLite persistence of leads and full message transcripts (db.py).",
            "Live lead scorecard: score / tier / BANT badges update after every turn.",
            "Sales dashboard: table of leads + click-through transcript view.",
            "Hot-lead routing: Calendly booking button + console sales alert.",
            "Prompt-injection resilience: system prompt + strict schema output.",
            "Session persistence via localStorage; 'New Chat' starts a fresh lead.",
        ],
    ),
    (
        "Backend API",
        [
            "GET  /health                 →  liveness check",
            "GET  /leads?limit=&offset=    →  paginated list of leads (newest first)",
            "GET  /leads/{session_id}      →  lead + full transcript + booking action",
            "POST /chat                    →  { reply, bant, score, tier, action }",
            "",
            "Request validation via Pydantic (session_id ≤128 chars, message ≤4000).",
            "CORS driven by CORS_ALLOWED_ORIGINS env var (comma-separated).",
        ],
    ),
    (
        "Frontend UI",
        [
            "## Prospect Chat tab",
            "- Chat thread with typing indicator and auto-scroll.",
            "- Right rail: live Lead Score + tier badge.",
            "- BANT panel showing budget / authority / need / timeline with colored states.",
            "- 'Schedule Meeting' CTA appears when the lead turns hot.",
            "",
            "## Lead Dashboard tab",
            "- Hot / Warm / Cold counters.",
            "- Sortable, clickable leads table.",
            "- Transcript panel with role-tagged messages and timestamps.",
        ],
    ),
    (
        "Reliability & Safety",
        [
            "Model fallback chain + retry window so a single bad model does not break /chat.",
            "If Gemini fails for the reply: user sees a safe fallback message, chat keeps working.",
            "If Gemini fails for BANT extraction: previous qualification data is preserved (merge_bant).",
            "Visitor-only transcript is fed into the BANT extractor to limit prompt-injection surface.",
            "System prompt explicitly rejects attempts to change role / rules.",
            "Verified behavior with test_bant.py (budget phrases, mixed-language input, injection probe).",
        ],
    ),
    (
        "Progress Snapshot",
        [
            "## Completed",
            "- End-to-end chat → score → persist → dashboard flow",
            "- BANT scoring + hot-lead routing",
            "- Styled React UI (Tailwind) with session persistence",
            "- BANT extraction test harness",
            "",
            "## In Progress",
            "- Tightening prompt + eval cases for edge inputs",
            "- Dashboard filters and search",
            "",
            "## Next Up",
            "- Auth for the dashboard, email / Slack alerts on hot leads",
            "- Real Calendly API integration (not just a link)",
            "- Deployment (Docker + managed Postgres), analytics, unit tests in CI",
        ],
    ),
    (
        "Thank You",
        [
            "## Demo time",
            "Chat tab  →  ask about pricing / timeline  →  watch the score climb.",
            "",
            "Repo: suyash-pratuyash/Qualbot-",
            "Questions welcome.",
        ],
    ),
]

# ----------------------------- OOXML templates ----------------------------- #

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
__SLIDE_OVERRIDES__
</Types>
"""

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>
"""

PRESENTATION_RELS_TMPL = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdMaster" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  <Relationship Id="rIdTheme" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
__SLIDE_RELS__
</Relationships>
"""

PRESENTATION_TMPL = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                saveSubsetFonts="1">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rIdMaster"/>
  </p:sldMasterIdLst>
  <p:sldIdLst>
__SLIDE_IDS__
  </p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>
  <p:notesSz cx="6858000" cy="9144000"/>
  <p:defaultTextStyle/>
</p:presentation>
"""

# Slide master and layout are intentionally minimal — slide-level XML carries
# all the real styling. A master with an empty cSld is accepted by Office,
# LibreOffice, Keynote, and Google Slides.
SLIDE_MASTER = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg>
      <p:bgPr>
        <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
        <a:effectLst/>
      </p:bgPr>
    </p:bg>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2"
            accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6"
            hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst>
    <p:sldLayoutId id="2147483649" r:id="rIdLayout1"/>
  </p:sldLayoutIdLst>
  <p:txStyles>
    <p:titleStyle/>
    <p:bodyStyle/>
    <p:otherStyle/>
  </p:txStyles>
</p:sldMaster>
"""

SLIDE_MASTER_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdLayout1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rIdTheme" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>
"""

SLIDE_LAYOUT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             type="blank" preserve="1">
  <p:cSld name="Blank">
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
    </p:spTree>
  </p:cSld>
</p:sldLayout>
"""

SLIDE_LAYOUT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdMaster" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>
"""

# A compact theme1.xml — some viewers reject the file without one.
THEME = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="QualBot">
  <a:themeElements>
    <a:clrScheme name="QualBot">
      <a:dk1><a:srgbClr val="0F172A"/></a:dk1>
      <a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="1E293B"/></a:dk2>
      <a:lt2><a:srgbClr val="F1F5F9"/></a:lt2>
      <a:accent1><a:srgbClr val="4F46E5"/></a:accent1>
      <a:accent2><a:srgbClr val="06B6D4"/></a:accent2>
      <a:accent3><a:srgbClr val="10B981"/></a:accent3>
      <a:accent4><a:srgbClr val="F59E0B"/></a:accent4>
      <a:accent5><a:srgbClr val="EF4444"/></a:accent5>
      <a:accent6><a:srgbClr val="8B5CF6"/></a:accent6>
      <a:hlink><a:srgbClr val="4F46E5"/></a:hlink>
      <a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="QualBot">
      <a:majorFont>
        <a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/>
      </a:majorFont>
      <a:minorFont>
        <a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/>
      </a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="QualBot">
      <a:fillStyleLst>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
      </a:fillStyleLst>
      <a:lnStyleLst>
        <a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
        <a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
        <a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
      </a:lnStyleLst>
      <a:effectStyleLst>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst/></a:effectStyle>
      </a:effectStyleLst>
      <a:bgFillStyleLst>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
      </a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
</a:theme>
"""

SLIDE_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rIdLayout" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>
"""

# ----------------------------- slide builders ----------------------------- #

# EMU constants (English Metric Units — 914400 per inch, 12700 per point).
SLIDE_W = 12192000  # 13.333" (widescreen)
SLIDE_H = 6858000   # 7.5"

INDIGO = "4F46E5"
INDIGO_DARK = "3730A3"
SLATE_900 = "0F172A"
SLATE_700 = "334155"
SLATE_500 = "64748B"
SLATE_200 = "E2E8F0"
WHITE = "FFFFFF"
ACCENT_BAR = "6366F1"


def _text_run(text: str, size_pt: int, bold: bool = False, color: str = SLATE_700) -> str:
    """Emit one <a:r> run inside a paragraph."""
    bold_attr = ' b="1"' if bold else ""
    return (
        f'<a:r><a:rPr lang="en-US" sz="{size_pt * 100}"{bold_attr} dirty="0">'
        f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
        f'<a:latin typeface="Calibri"/></a:rPr>'
        f'<a:t>{escape(text)}</a:t></a:r>'
    )


def _para(runs_xml: str, bullet: str = "none", indent: int = 0,
          spc_before: int = 300, align: str = "l") -> str:
    """
    Wrap one or more runs in a paragraph.

    bullet: "none" | "disc" | "sub"
    indent: 0 for top-level, 1 for sub-bullet.
    """
    buChar = ""
    if bullet == "disc":
        buChar = '<a:buFont typeface="Arial" panose="020B0604020202020204" pitchFamily="34" charset="0"/><a:buChar char="•"/>'
    elif bullet == "sub":
        buChar = '<a:buFont typeface="Arial" panose="020B0604020202020204" pitchFamily="34" charset="0"/><a:buChar char="–"/>'
    elif bullet == "none":
        buChar = '<a:buNone/>'

    lvl_attr = f' lvl="{indent}"' if indent else ""
    marL = 342900 if bullet in ("disc", "sub") else 0
    indent_attr = f' marL="{marL}" indent="-342900"' if marL else ""

    return (
        f'<a:p>'
        f'<a:pPr{lvl_attr}{indent_attr} algn="{align}">'
        f'<a:spcBef><a:spcPts val="{spc_before}"/></a:spcBef>'
        f'{buChar}'
        f'</a:pPr>'
        f'{runs_xml}'
        f'</a:p>'
    )


def _shape(sp_id: int, name: str, x: int, y: int, cx: int, cy: int,
           body_xml: str, fill_hex: str | None = None,
           line_hex: str | None = None) -> str:
    """Emit a text-bearing rectangle shape with optional fill/outline."""
    fill = (
        f'<a:solidFill><a:srgbClr val="{fill_hex}"/></a:solidFill>'
        if fill_hex else '<a:noFill/>'
    )
    line = (
        f'<a:ln w="12700"><a:solidFill><a:srgbClr val="{line_hex}"/></a:solidFill></a:ln>'
        if line_hex else '<a:ln><a:noFill/></a:ln>'
    )
    return f'''<p:sp>
  <p:nvSpPr>
    <p:cNvPr id="{sp_id}" name="{name}"/>
    <p:cNvSpPr txBox="1"/>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm>
      <a:off x="{x}" y="{y}"/>
      <a:ext cx="{cx}" cy="{cy}"/>
    </a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    {fill}
    {line}
  </p:spPr>
  <p:txBody>
    <a:bodyPr wrap="square" lIns="137160" tIns="91440" rIns="137160" bIns="91440" anchor="t"/>
    <a:lstStyle/>
    {body_xml}
  </p:txBody>
</p:sp>'''


def _bg_rect(sp_id: int, x: int, y: int, cx: int, cy: int, fill_hex: str) -> str:
    """A plain colored rectangle used for banners / accent bars."""
    return f'''<p:sp>
  <p:nvSpPr>
    <p:cNvPr id="{sp_id}" name="Accent{sp_id}"/>
    <p:cNvSpPr/>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm>
      <a:off x="{x}" y="{y}"/>
      <a:ext cx="{cx}" cy="{cy}"/>
    </a:xfrm>
    <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
    <a:solidFill><a:srgbClr val="{fill_hex}"/></a:solidFill>
    <a:ln><a:noFill/></a:ln>
  </p:spPr>
  <p:txBody>
    <a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="en-US"/></a:p>
  </p:txBody>
</p:sp>'''


def _build_title_slide(title: str, lines: list[str]) -> str:
    """First slide: hero layout with accent band and big title."""
    paras = []
    # Big QualBot title
    paras.append(_para(_text_run(title, 72, bold=True, color=WHITE),
                       bullet="none", spc_before=0))

    for line in lines:
        if not line.strip():
            paras.append(_para('<a:endParaRPr lang="en-US" sz="1800"/>',
                               bullet="none", spc_before=200))
            continue
        if line.startswith("## "):
            paras.append(_para(_text_run(line[3:], 28, bold=True, color=WHITE),
                               bullet="none", spc_before=600))
        else:
            paras.append(_para(_text_run(line, 20, color="E0E7FF"),
                               bullet="none", spc_before=300))

    body = "".join(paras)

    shapes = [
        _bg_rect(2, 0, 0, SLIDE_W, SLIDE_H, INDIGO_DARK),
        _bg_rect(3, 0, SLIDE_H - 400000, SLIDE_W, 400000, INDIGO),
        _shape(4, "Hero", 914400, 1600000, SLIDE_W - 1828800, SLIDE_H - 2600000,
               body),
    ]
    return "\n".join(shapes)


def _build_content_slide(title: str, lines: list[str], slide_num: int,
                         total: int) -> str:
    """Standard content slide: colored title bar + bulleted body + footer."""
    # ---- title bar ----
    title_body = _para(
        _text_run(title, 32, bold=True, color=WHITE),
        bullet="none", spc_before=0,
    )
    # ---- body paragraphs ----
    paras: list[str] = []
    for line in lines:
        if not line.strip():
            paras.append(_para('<a:endParaRPr lang="en-US" sz="1600"/>',
                               bullet="none", spc_before=100))
            continue
        if line.startswith("## "):
            paras.append(_para(
                _text_run(line[3:], 20, bold=True, color=INDIGO),
                bullet="none", spc_before=500,
            ))
        elif line.startswith("- "):
            paras.append(_para(
                _text_run(line[2:], 16, color=SLATE_700),
                bullet="sub", indent=1, spc_before=200,
            ))
        else:
            paras.append(_para(
                _text_run(line, 18, color=SLATE_900),
                bullet="disc", spc_before=250,
            ))
    body_xml = "".join(paras) if paras else _para(
        '<a:endParaRPr lang="en-US"/>', bullet="none"
    )

    # ---- footer ----
    footer_body = _para(
        _text_run(f"QualBot — Progress Report", 10, color=SLATE_500),
        bullet="none", spc_before=0,
    )
    page_body = _para(
        _text_run(f"{slide_num} / {total}", 10, color=SLATE_500),
        bullet="none", spc_before=0, align="r",
    )

    shapes = [
        # left accent bar
        _bg_rect(2, 0, 0, 200000, SLIDE_H, INDIGO),
        # title band
        _bg_rect(3, 200000, 0, SLIDE_W - 200000, 900000, INDIGO_DARK),
        _shape(4, "Title", 500000, 180000, SLIDE_W - 700000, 600000,
               title_body),
        # thin accent divider under title
        _bg_rect(5, 200000, 900000, SLIDE_W - 200000, 40000, ACCENT_BAR),
        # body card
        _shape(6, "Body", 600000, 1150000, SLIDE_W - 1200000,
               SLIDE_H - 1600000, body_xml),
        # footer
        _shape(7, "Footer", 500000, SLIDE_H - 400000, 4000000, 300000,
               footer_body),
        _shape(8, "Page", SLIDE_W - 1500000, SLIDE_H - 400000,
               1000000, 300000, page_body),
    ]
    return "\n".join(shapes)


def build_slide_xml(index: int, title: str, lines: list[str], total: int) -> str:
    """Assemble the full <p:sld> XML for one slide."""
    if index == 0:
        shapes = _build_title_slide(title, lines)
    else:
        shapes = _build_content_slide(title, lines, index + 1, total)

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      {shapes}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>
'''


# ----------------------------- packaging ----------------------------- #

def write(zf: zipfile.ZipFile, name: str, data: str) -> None:
    zf.writestr(name, data.encode("utf-8"))


def main() -> None:
    total = len(SLIDES)

    slide_overrides = "\n".join(
        f'  <Override PartName="/ppt/slides/slide{i+1}.xml" '
        f'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(total)
    )

    slide_rels = "\n".join(
        f'  <Relationship Id="rIdSlide{i+1}" '
        f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" '
        f'Target="slides/slide{i+1}.xml"/>'
        for i in range(total)
    )

    # Slide IDs start at 256 by convention; must be unique.
    slide_ids = "\n".join(
        f'    <p:sldId id="{256 + i}" r:id="rIdSlide{i+1}"/>'
        for i in range(total)
    )

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        write(zf, "[Content_Types].xml",
              CONTENT_TYPES.replace("__SLIDE_OVERRIDES__", slide_overrides))
        write(zf, "_rels/.rels", ROOT_RELS)

        write(zf, "ppt/presentation.xml",
              PRESENTATION_TMPL.replace("__SLIDE_IDS__", slide_ids))
        write(zf, "ppt/_rels/presentation.xml.rels",
              PRESENTATION_RELS_TMPL.replace("__SLIDE_RELS__", slide_rels))

        write(zf, "ppt/theme/theme1.xml", THEME)
        write(zf, "ppt/slideMasters/slideMaster1.xml", SLIDE_MASTER)
        write(zf, "ppt/slideMasters/_rels/slideMaster1.xml.rels", SLIDE_MASTER_RELS)
        write(zf, "ppt/slideLayouts/slideLayout1.xml", SLIDE_LAYOUT)
        write(zf, "ppt/slideLayouts/_rels/slideLayout1.xml.rels", SLIDE_LAYOUT_RELS)

        for i, (title, lines) in enumerate(SLIDES):
            write(zf, f"ppt/slides/slide{i+1}.xml",
                  build_slide_xml(i, title, lines, total))
            write(zf, f"ppt/slides/_rels/slide{i+1}.xml.rels", SLIDE_RELS)

    print(f"Wrote {OUT}  ({total} slides, {os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    main()
