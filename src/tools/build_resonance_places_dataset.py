#!/usr/bin/env python3
"""
Build MGK "Ur-Interfaces / Resonance Places" dataset.

Inputs (expected in-repo):
  - incoming/arunachala_bundle_notebooklm_research.md
  - incoming/malta_bundle_notebooklm_research.md
  - incoming/delphi_bundle_notebooklm_research.md
  - data/human_cartography/overlays/resonance_strands/raw/*_resonance.json (v0)

Outputs:
  data/human_cartography/resonance_places/
    bundles/
    synthesis/
    sources/metadata/
    sources/resonance_raw/
    aggregates/
    comparative/
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
INCOMING_DIR = REPO_ROOT / "incoming"
V0_TRANSCRIPT_RESONANCE_DIR = (
    REPO_ROOT / "data" / "human_cartography" / "overlays" / "resonance_strands" / "raw"
)

OUT_ROOT = REPO_ROOT / "data" / "human_cartography" / "resonance_places"
OUT_BUNDLES = OUT_ROOT / "bundles"
OUT_SYNTHESIS = OUT_ROOT / "synthesis"
OUT_SRC_META = OUT_ROOT / "sources" / "metadata"
OUT_SRC_RESONANCE = OUT_ROOT / "sources" / "resonance_raw"
OUT_AGG = OUT_ROOT / "aggregates"
OUT_COMP = OUT_ROOT / "comparative"


PLACE_CONFIG: Dict[str, Dict[str, Any]] = {
    "ARUNACHALA": {
        "incoming": "arunachala_bundle_notebooklm_research.md",
        "primary_place": "Arunachala",
        "place_type": "mountain/sacred_site",
    },
    "MALTA": {
        "incoming": "malta_bundle_notebooklm_research.md",
        "primary_place": "Megalithic Temples Malta",
        "place_type": "megalithic_temple_complex",
    },
    "DELPHI": {
        "incoming": "delphi_bundle_notebooklm_research.md",
        "primary_place": "Delphi",
        "place_type": "archaeological_sanctuary/ruins",
    },
}


ALLOWED_SOURCE_TYPES = {
    "first_person_report",
    "academic_paper",
    "official_site",
    "travel_guide",
    "video_report",
    "forum_post",
    "review_platform",
    "secondary_blog",
    "encyclopedia",
    "book_excerpt",
    "portal",
}

ALLOWED_RELIABILITY_TIERS = {"A", "B", "C", "D"}


GLOBAL_MARKERS: List[Dict[str, str]] = [
    {
        "marker_id": "RP-MKR-PLACE-AS-AGENT-GURU-0001",
        "definition": "Ort wird als Akteur/Lehrinstanz gerahmt (place-as-guru/agency), inkl. Authority-Transfer.",
    },
    {
        "marker_id": "RP-MKR-ACOUSTIC-REVERBERATION-0002",
        "definition": "Akustische Resonanz/Echo als zentraler Wirkfaktor (Reverberation, Frequenzen, 'wie in einer Glocke').",
    },
    {
        "marker_id": "RP-MKR-VERTICAL-ASCENT-CHOREOGRAPHY-0003",
        "definition": "Aufstieg/Vertikalität und Weg-Choreographie als somatischer Trigger (Serpentinen, Stufen, Entschleunigung).",
    },
    {
        "marker_id": "RP-MKR-CROWD-RITUAL-MASS-0004",
        "definition": "Ritual-Masse/Crowd-Synchronisation als Verstärker (Pilgerdichte, Massenbewegung, kollektiv).",
    },
    {
        "marker_id": "RP-MKR-TIME-DENSITY-THINNING-0005",
        "definition": "Zeitdichte/Temporal-Thinning: subjektive Zeitverschiebung, 'Ewigkeit', Vorher/Nachher-Zäsur.",
    },
    {
        "marker_id": "RP-MKR-SENSORY-SMELL-FUMES-0006",
        "definition": "Geruch/Dämpfe/Incense als sensorischer Anker, der Deutungsrahmen verstärkt.",
    },
    {
        "marker_id": "RP-MKR-ACCESS-CONTROL-MUSEUMIZATION-0007",
        "definition": "Access-Control/Museumisierung: Zäune, Regeln, Time-Slots, Schutzdächer, kuratierte Inszenierung.",
    },
    {
        "marker_id": "RP-MKR-DEEP-TIME-AWE-0008",
        "definition": "Deep-time Awe: Demut/Staunen über Zeit-Tiefe, Alter, Monumentalität.",
    },
    {
        "marker_id": "RP-MKR-WOMB-UNDERWORLD-METAPHOR-0009",
        "definition": "Womb/Unterwelt-Metapher: Enge, Tiefe, 'Mutterleib', Rückkehr in die Erde.",
    },
    {
        "marker_id": "RP-MKR-LIGHT-QUALITY-MYSTIC-0010",
        "definition": "Lichtqualität als Atmosphärenmarker (mystisches Licht, Gold/Rosa, Kontur-Unschärfe).",
    },
    {
        "marker_id": "RP-MKR-MYTHIC-OVERLAY-DOCTRINAL-0011",
        "definition": "Mythischer/doctrinaler Overlay: Götter, Schlange, Shiva, Omphalos; Symbolik stabilisiert Ortssinn.",
    },
    {
        "marker_id": "RP-MKR-SELF-MIRROR-IDENTITY-0012",
        "definition": "Place-as-mirror: Selbstreflexion, Identitäts-/Ego-Thema, 'erkenne dich selbst'.",
    },
]


@dataclass
class ParsedSource:
    place_code: str
    ordinal: int
    title: str
    author: str
    date_or_year: str
    medium: str
    url: str
    quotes: List[str]
    summary_points: List[str]
    raw_snippets: List[str]
    source_ref_nums: List[int]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _ensure_dirs() -> None:
    OUT_BUNDLES.mkdir(parents=True, exist_ok=True)
    OUT_SYNTHESIS.mkdir(parents=True, exist_ok=True)
    OUT_SRC_META.mkdir(parents=True, exist_ok=True)
    OUT_SRC_RESONANCE.mkdir(parents=True, exist_ok=True)
    OUT_AGG.mkdir(parents=True, exist_ok=True)
    OUT_COMP.mkdir(parents=True, exist_ok=True)


def _cleanup_previous_outputs() -> None:
    # Only remove files that this builder generates.
    for path in OUT_BUNDLES.glob("BUNDLE-*-RESEARCH-*.md"):
        path.unlink(missing_ok=True)
    for path in OUT_SYNTHESIS.glob("SYNTHESIS-*-RESEARCH-*.md"):
        path.unlink(missing_ok=True)
    for path in OUT_SRC_META.glob("SRC-*.json"):
        path.unlink(missing_ok=True)
    for path in OUT_SRC_RESONANCE.glob("SRC-*_resonance.json"):
        path.unlink(missing_ok=True)
    for path in OUT_SRC_RESONANCE.glob("TZ-PLACE-*-FRANK-STONER-ENGELMAYER-0001_resonance.json"):
        path.unlink(missing_ok=True)
    for path in OUT_AGG.glob("TZ-PLACE-*-AGG-0001_resonance_aggregate.json"):
        path.unlink(missing_ok=True)
    for path in OUT_COMP.glob("COMP-RESONANCE-PLACES-0001_*"):
        path.unlink(missing_ok=True)


def _word_trim(text: str, max_words: int = 25) -> str:
    words = re.findall(r"\S+", text.strip())
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).rstrip(" ,.;:") + "…"


def _clean_quote_text(text: str) -> str:
    text = text.strip()
    text = text.strip("“”\"'")
    text = re.sub(r"\s*\[\d+(?:\s*,\s*\d+)*\]\s*$", "", text).strip()
    text = re.sub(r"\s+", " ", text).strip()
    return _word_trim(text, 25)


def _extract_citations(line: str) -> List[int]:
    # Matches [12], [13, 15] etc.
    citations: List[int] = []
    for m in re.finditer(r"\[(\d+(?:\s*,\s*\d+)*)\]", line):
        chunk = m.group(1)
        for part in chunk.split(","):
            part = part.strip()
            if part.isdigit():
                citations.append(int(part))
    return citations


def _infer_source_type(medium: str, url: str, author: str) -> str:
    medium_l = (medium or "").lower()
    url_l = (url or "").lower()
    author_l = (author or "").lower()

    if "youtube" in url_l or "video" in medium_l:
        return "video_report"

    if any(k in url_l for k in ["reddit.com", "quora.com"]) or "forum" in medium_l:
        return "forum_post"

    if "tripadvisor" in url_l or "viator" in url_l or "review" in medium_l:
        return "review_platform"

    if "wikipedia" in url_l or "wikipedia" in medium_l:
        return "encyclopedia"

    if any(k in url_l for k in ["whc.unesco.org", "heritagemalta.mt"]) or "unesco" in medium_l:
        return "official_site"

    if any(k in url_l for k in ["academic.oup.com", "cambridge.org"]) or any(
        k in medium_l for k in ["fachartikel", "paper", "preprint", "konferenz", "conference"]
    ):
        return "academic_paper"

    if any(k in medium_l for k in ["buch", "book", "fachliteratur", "excerpt", "auszug"]):
        return "book_excerpt"

    if "portal" in medium_l:
        return "portal"

    if any(k in medium_l for k in ["reiseführer", "guide", "travel guide", "reisetipp"]):
        return "travel_guide"

    # Heuristic: essays / travel reports are often first-person.
    if any(k in medium_l for k in ["essay", "reisebericht", "travel blog", "personal narrative"]):
        return "first_person_report"

    if "blog" in medium_l:
        # Unknown author blogs are treated as secondary_blog.
        return "secondary_blog"

    if author_l and author_l not in {"unbekannt", "anonymous"}:
        return "first_person_report"

    return "secondary_blog"


def _infer_reliability_tier(source_type: str, url: str, author: str, medium: str) -> str:
    url_l = (url or "").lower()
    author_l = (author or "").strip().lower()
    medium_l = (medium or "").lower()

    if any(k in url_l for k in ["whc.unesco.org", "heritagemalta.mt"]):
        return "A"
    if any(k in url_l for k in ["cambridge.org", "academic.oup.com"]):
        return "A"
    if "um.edu.mt" in url_l and source_type in {"academic_paper", "official_site"}:
        return "A"

    if any(k in url_l for k in ["dokumen.pub", "scribd.com", "historicmysteries.com"]):
        return "D"

    if source_type in {"forum_post", "review_platform"}:
        return "C"

    if author_l in {"unbekannt", "anonymous", ""} and source_type in {"secondary_blog", "portal"}:
        return "C"

    # Default: identifiable author + coherent medium.
    return "B"


def _classify_raw_vs_claim(excerpt: str, source_type: str) -> str:
    txt = excerpt.lower()
    claim_markers = [
        "energy",
        "energie",
        "chakra",
        "karma",
        "heals",
        "heilt",
        "spirit",
        "supreme",
        "gott",
        "god",
        "apollo",
        "gaia",
        "shiva",
        "lingam",
        "trance",
        "oracle",
        "orakel",
        "center of the world",
        "nabel der welt",
        "universe",
        "unendlichkeit",
        "matrix",
        "grid",
        "kills without killing",
        "burning of karma",
        "still the mind",
    ]
    if any(m in txt for m in claim_markers):
        return "interpretive_claim"

    if source_type in {"academic_paper", "official_site", "encyclopedia", "portal", "travel_guide", "secondary_blog"}:
        # Not necessarily first-person; treat as reported unless clearly raw.
        return "reported_effect"

    return "raw_perception"


def _infer_channels(excerpt: str) -> List[str]:
    txt = excerpt.lower()
    channels: List[str] = []

    body_k = ["sweat", "schweiß", "headache", "tummy", "belly", "heat", "hitze", "breath", "voice", "vibration", "bone", "tissue", "stairs", "stufen", "körper"]
    time_k = ["time", "zeit", "timeless", "ewigkeit", "phase", "before", "after", "zurück", "7000", "jahrtausend"]
    emotion_k = ["calm", "ruhe", "bliss", "seligkeit", "fear", "angst", "awe", "magical", "breathtaking", "sprachlos", "privileged", "peace", "serenity", "aggression", "trauma"]
    cognition_k = ["realize", "erkennt", "understanding", "fragen", "reflekt", "insight", "witness", "beobacht"]
    symbolic_k = ["oracle", "orakel", "omphalos", "nabel", "myth", "mythos", "apollo", "gaia", "python", "shiva", "lingam", "mother goddess", "mutter", "womb", "rebirth", "heilig", "sacred"]
    social_k = ["tourist", "tourbus", "unesco", "rules", "restrictive", "curated", "security", "crowd", "pilger", "million", "visitor", "tickets"]
    material_k = ["stone", "stein", "kalkstein", "blocks", "tonnen", "megalith", "portal", "trilith", "architecture", "ruins", "temple", "hypogeum", "cave", "felsen", "cliff", "stadium"]
    space_k = ["mountain", "berg", "hill", "site", "sanctuary", "valley", "sea", "theater", "stadium", "path", "sacred way", "serpentinen", "vertical"]

    def add(name: str) -> None:
        if name not in channels:
            channels.append(name)

    if any(k in txt for k in body_k):
        add("body")
    if any(k in txt for k in emotion_k):
        add("emotion")
    if any(k in txt for k in cognition_k):
        add("cognition")
    if any(k in txt for k in symbolic_k):
        add("symbolic")
    if any(k in txt for k in social_k):
        add("social")
    if any(k in txt for k in material_k):
        add("material")
    if any(k in txt for k in space_k):
        add("space")
    if any(k in txt for k in time_k):
        add("time")

    if not channels:
        add("cognition")
    return channels[:3]


def _infer_triggers(excerpt: str) -> List[str]:
    txt = excerpt.lower()
    triggers: List[str] = []

    def add(name: str) -> None:
        if name not in triggers:
            triggers.append(name)

    if any(k in txt for k in ["chant", "mantra", "circumamb", "girivalam", "ashram", "pilgr", "offerings", "ritual", "reinigung", "quelle", "kastalia"]):
        add("ritual_context")
    if any(k in txt for k in ["met", "encounter", "old man", "entered", "presence", "begegnung"]):
        add("encounter")
    if any(k in txt for k in ["light", "licht", "fire", "flame", "gold", "rose", "sunrise", "sunset"]):
        add("visual_form")
    if any(k in txt for k in ["incense", "smell", "geruch", "fumes", "dämpfe", "thyme", "oregano", "pinien"]):
        add("sensory_smell")
    if any(k in txt for k in ["silence", "stille", "quiet", "ruhig"]):
        add("silence")
    if any(k in txt for k in ["ton", "tonnen", "57", "2000", "blocks", "massive", "megalith", "kalkstein"]):
        add("material_mass")
    if any(k in txt for k in ["portal", "trilith", "hypogeum", "oracle room", "stadium", "theater", "serpent", "sacred way", "path", "cave", "ruins", "tholos"]):
        add("architectural_form")
    if any(k in txt for k in ["before pyramids", "stonehenge", "7000", "jahrtausend", "deep time", "time-depth", "zeit-tiefe"]):
        add("historical_depth")
    if any(k in txt for k in ["history", "histor", "plutarch"]):
        add("historical_context")
    if any(k in txt for k in ["apollo", "gaia", "python", "shiva", "lingam", "hymnus", "myth"]):
        add("mythic_context")
    if any(k in txt for k in ["guru", "oracle", "orakel", "chakra", "energy", "energie", "center of the world", "nabel der welt", "universe", "god"]):
        add("authority_projection")
    if any(k in txt for k in ["womb", "mother", "goddess", "rebirth", "geburts", "sleeping lady", "fat ladies"]):
        add("ritual_imagination")
    if (
        re.search(r"\bunesco\b", txt)
        or re.search(r"\bfence\b", txt)
        or re.search(r"\bzaun\b", txt)
        or re.search(r"\brestrictive\b", txt)
        or re.search(r"\brules\b", txt)
        or re.search(r"\bsecurity\b", txt)
        or re.search(r"\btickets\b", txt)
        or "over-curated" in txt
        or re.search(r"\bshelter\b", txt)
        or re.search(r"\bschutzdach\b", txt)
    ):
        add("social_control_barrier")
    if any(k in txt for k in ["omphalos", "navel", "nabel", "center of the world"]):
        add("place_center_symbol")

    if not triggers:
        add("other")
    return triggers[:3]


def _infer_layers(raw_vs_claim: str, channels: List[str], triggers: List[str]) -> List[str]:
    layers: List[str] = []

    def add(name: str) -> None:
        if name not in layers:
            layers.append(name)

    if any(c in channels for c in ["body", "material", "space", "time"]):
        add("R1")
    if "emotion" in channels:
        add("R2")
    if "cognition" in channels:
        add("R3")
    if "symbolic" in channels or any(t in triggers for t in ["mythic_context", "ritual_imagination", "place_center_symbol"]):
        add("R4")
    if raw_vs_claim == "interpretive_claim" or "authority_projection" in triggers:
        add("R5")
    return layers


def _infer_valence(excerpt: str) -> List[str]:
    txt = excerpt.lower()
    pos = ["calm", "ruhe", "bliss", "seligkeit", "magical", "breathtaking", "peace", "serenity", "privileged", "awe", "beautiful", "atemberaub"]
    neg = ["fear", "angst", "aggression", "sick", "headache", "restrictive", "chaotic", "disappoint", "bevormund", "violent"]
    p = any(k in txt for k in pos)
    n = any(k in txt for k in neg)
    if p and n:
        return ["mixed"]
    if p:
        return ["positive"]
    if n:
        return ["negative"]
    return ["unknown"]


def _infer_intensity(excerpt: str) -> int:
    txt = excerpt.lower()
    strong = ["life-changing", "blown me away", "bone", "beyond words", "terrifying", "profound", "ecstatic", "knochenmark", "speechless", "sprachlos"]
    medium = ["breathtaking", "magical", "privileged", "calm washes", "otherworldly", "atemberaub"]
    if any(k in txt for k in strong):
        return 5
    if any(k in txt for k in medium):
        return 4
    return 3


def _make_event(event_id: int, excerpt: str, source_type: str, note_prefix: str) -> Dict[str, Any]:
    excerpt = _clean_quote_text(excerpt)
    channels = _infer_channels(excerpt)
    triggers = _infer_triggers(excerpt)
    raw_vs_claim = _classify_raw_vs_claim(excerpt, source_type)
    layers = _infer_layers(raw_vs_claim, channels, triggers)

    return {
        "event_id": f"RE-{event_id:04d}",
        "excerpt": excerpt,
        "layer": layers,
        "channel": channels,
        "valence": _infer_valence(excerpt),
        "intensity_0_5": _infer_intensity(excerpt),
        "triggers": triggers,
        "raw_vs_claim": raw_vs_claim,
        "notes": note_prefix,
    }


def _build_resonance_for_source(source_id: str, place_code: str, place_focus: Dict[str, Any], meta: Dict[str, Any], candidates: List[Tuple[str, str]]) -> Dict[str, Any]:
    # candidates: list of (kind, text)
    source_type = meta["source_type"]

    events: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for kind, txt in candidates:
        cleaned = _clean_quote_text(txt)
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        note_prefix = f"{kind}; DP-002: treat as reported/subjective unless measured."
        events.append(_make_event(len(events) + 1, cleaned, source_type, note_prefix))
        if len(events) >= 12:
            break

    # Guarantee minimum number of events (5) by splitting longer summary lines if needed.
    if len(events) < 5:
        for kind, txt in candidates:
            parts = re.split(r"[.;]\s+|\s+—\s+|\s*/\s+|:\s+", txt.strip())
            for part in parts:
                cleaned = _clean_quote_text(part)
                if not cleaned:
                    continue
                key = cleaned.lower()
                if key in seen:
                    continue
                seen.add(key)
                note_prefix = f"{kind}; split; DP-002: treat as reported/subjective unless measured."
                events.append(_make_event(len(events) + 1, cleaned, source_type, note_prefix))
                if len(events) >= 5:
                    break
            if len(events) >= 5:
                break

    # Aggregate profile (lightweight)
    channel_counts: Dict[str, int] = {}
    trigger_counts: Dict[str, int] = {}
    for e in events:
        for c in e.get("channel", []):
            channel_counts[c] = channel_counts.get(c, 0) + 1
        for t in e.get("triggers", []):
            trigger_counts[t] = trigger_counts.get(t, 0) + 1

    dominant_channels = [k for k, _ in sorted(channel_counts.items(), key=lambda kv: (-kv[1], kv[0]))][:5]
    dominant_triggers = [k for k, _ in sorted(trigger_counts.items(), key=lambda kv: (-kv[1], kv[0]))][:7]

    return {
        "id": f"{source_id}-RESONANCE",
        "source_id": source_id,
        "place_focus": place_focus,
        "resonance_events": events,
        "aggregate_profile": {
            "dominant_channels": dominant_channels,
            "dominant_triggers": dominant_triggers,
            "stability_notes": "Auto-extracted from bundle: mix of quotes, summaries and (where needed) bundle-level synthesis lines; DP-002 applied.",
        },
    }


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _parse_arunachala(text: str) -> Tuple[str, List[ParsedSource]]:
    lines = text.splitlines()
    idx_catalog = next(
        (i for i, line in enumerate(lines) if "Systematic Documentation of Authentic Experience Reports" in line),
        None,
    )
    idx_post_synth = next(
        (i for i, line in enumerate(lines) if line.strip() == "Phenomenological Synthesis of Subjective Dynamics"),
        None,
    )
    idx_hr = next((i for i, line in enumerate(lines) if line.strip().startswith("---")), None)

    if idx_catalog is None or idx_hr is None:
        raise RuntimeError("Failed to locate Arunachala catalog split markers.")

    pre = "\n".join(lines[:idx_catalog]).strip()
    post = ""
    if idx_post_synth is not None:
        post = "\n".join(lines[idx_post_synth:idx_hr]).strip()
    synthesis = "\n\n".join([p for p in [pre, post] if p]).strip()

    catalog = "\n".join(lines[idx_catalog + 1 : idx_post_synth if idx_post_synth else idx_hr]).strip()

    # Split numbered entries: "1. ..."; keep only blocks that actually contain per-source fields.
    entries = [e.strip() for e in re.split(r"(?m)^\d+\.\s+", catalog) if e.strip()]

    sources: List[ParsedSource] = []
    for ordinal, block in enumerate(entries, start=1):
        if "• Title:" not in block and "• URL:" not in block:
            continue
        title = _extract_field(block, "Title")
        author = _extract_field(block, "Author")
        date = _extract_field(block, "Date")
        medium = _extract_field(block, "Medium")
        url = _extract_field(block, "URL")
        quotes, summary = _extract_quotes_and_summary(block, quotes_label="Relevant Quotes", summary_label="Inhaltszusammenfassung")
        raw_snippets: List[str] = []
        sources.append(
            ParsedSource(
                place_code="ARUNACHALA",
                ordinal=ordinal,
                title=title,
                author=author,
                date_or_year=date,
                medium=medium,
                url=url,
                quotes=quotes,
                summary_points=summary,
                raw_snippets=raw_snippets,
                source_ref_nums=[],
            )
        )
    return synthesis, sources


def _extract_field(block: str, label: str) -> str:
    # Matches "• Label: value"
    m = re.search(rf"(?m)^\s*•\s*{re.escape(label)}:\s*(.+)\s*$", block)
    return (m.group(1).strip() if m else "").strip()


def _extract_quotes_and_summary(block: str, *, quotes_label: str, summary_label: str) -> Tuple[List[str], List[str]]:
    quotes: List[str] = []
    summary: List[str] = []

    # Find section starts
    q_start = re.search(rf"(?m)^\s*•\s*{re.escape(quotes_label)}:\s*$", block)
    s_start = re.search(rf"(?m)^\s*•\s*{re.escape(summary_label)}:\s*$", block)

    q_idx = q_start.start() if q_start else None
    s_idx = s_start.start() if s_start else None

    if q_idx is not None and s_idx is not None:
        q_text = block[q_start.end() : s_start.start()]
        s_text = block[s_start.end() :]
        quotes = _extract_bullets(q_text)
        summary = _extract_bullets(s_text)
        return quotes, summary

    if q_idx is not None:
        q_text = block[q_start.end() :]
        quotes = _extract_bullets(q_text)
    if s_idx is not None:
        s_text = block[s_start.end() :]
        summary = _extract_bullets(s_text)
    return quotes, summary


def _extract_bullets(text: str) -> List[str]:
    out: List[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # "◦ " bullet or "1. " list item
        if line.startswith("◦ "):
            out.append(line[2:].strip())
        elif re.match(r"^\d+\.\s+", line):
            out.append(re.sub(r"^\d+\.\s+", "", line).strip())
    return out


def _parse_malta(text: str) -> Tuple[str, List[ParsedSource]]:
    lines = text.splitlines()
    idx_first_quelle = next((i for i, line in enumerate(lines) if line.startswith("Quelle 1:")), None)
    idx_synth = next((i for i, line in enumerate(lines) if line.strip() == "Synthese der subjektiven Wirkfaktoren"), None)
    idx_hr = next((i for i, line in enumerate(lines) if line.strip().startswith("---")), None)
    if idx_first_quelle is None or idx_synth is None or idx_hr is None:
        raise RuntimeError("Failed to locate Malta split markers.")

    pre = "\n".join(lines[:idx_first_quelle]).strip()
    post = "\n".join(lines[idx_synth:idx_hr]).strip()
    synthesis = "\n\n".join([p for p in [pre, post] if p]).strip()

    catalog = "\n".join(lines[idx_first_quelle:idx_synth]).strip()

    # Split by "Quelle N:"
    parts = re.split(r"(?m)^Quelle\s+(\d+):\s*", catalog)
    # parts = [before, num1, block1, num2, block2, ...]
    sources: List[ParsedSource] = []
    for i in range(1, len(parts), 2):
        num = int(parts[i])
        block = parts[i + 1].strip()
        title_line = block.splitlines()[0].strip()
        title = title_line
        author = _extract_field_de(block, "Autor")
        year = _extract_field_de(block, "Jahr")
        medium = _extract_field_de(block, "Medium")
        url = _extract_field_de(block, "URL")
        quotes, summary = _extract_quotes_and_summary(block, quotes_label="Zitate", summary_label="Zusammenfassung")
        raw_snippets: List[str] = []
        sources.append(
            ParsedSource(
                place_code="MALTA",
                ordinal=num,
                title=title,
                author=author,
                date_or_year=year,
                medium=medium,
                url=url,
                quotes=quotes,
                summary_points=summary,
                raw_snippets=raw_snippets,
                source_ref_nums=[],
            )
        )
    return synthesis, sources


def _extract_field_de(block: str, label: str) -> str:
    m = re.search(rf"(?m)^\s*•\s*{re.escape(label)}:\s*(.+)\s*$", block)
    return (m.group(1).strip() if m else "").strip()


def _parse_delphi(text: str) -> Tuple[str, List[ParsedSource]]:
    lines = text.splitlines()
    idx_sys = next((i for i, line in enumerate(lines) if line.strip().startswith("Systematische Quellendokumentation")), None)
    idx_detail = next((i for i, line in enumerate(lines) if line.strip().startswith("Detailanalyse der Erfahrungsberichte")), None)
    idx_hr = next((i for i, line in enumerate(lines) if line.strip().startswith("---")), None)
    if idx_sys is None or idx_detail is None or idx_hr is None:
        raise RuntimeError("Failed to locate Delphi split markers.")

    synthesis_pre = "\n".join(lines[:idx_sys]).strip()

    table_block = "\n".join(lines[idx_sys:idx_detail]).strip()
    table_sources = _parse_delphi_table(table_block)

    # Parse per-source detail blocks for Quelle 1..7 and 10 (as present)
    detail_block = "\n".join(lines[idx_detail:idx_hr]).strip()
    quelle_details = _parse_delphi_quelle_details(detail_block)

    # Parse source list after HR into ref->url/title
    source_list_block = "\n".join(lines[idx_hr + 1 :]).strip()
    ref_map = _parse_numbered_url_list(source_list_block)

    # Extract analysis snippets with citations from detail_block (excluding Quelle blocks)
    snippets_by_ref = _extract_snippets_by_ref(detail_block)

    table_by_ref = {row["ref_num"]: row for row in table_sources if row.get("ref_num", -1) != -1}
    table_by_nr = {row["nr"]: row for row in table_sources}

    # Map Quelle-details (keyed by table row number) to reference numbers.
    details_by_ref: Dict[int, Dict[str, Any]] = {}
    for quelle_nr, details in quelle_details.items():
        row = table_by_nr.get(quelle_nr)
        if not row:
            continue
        ref_num = int(row.get("ref_num", -1))
        if ref_num == -1:
            continue
        details_by_ref[ref_num] = details

    # Score refs by available snippet density; prefer refs that are actually cited in the bundle analysis.
    scores: Dict[int, int] = {}
    for ref_num in ref_map.keys():
        quotes = details_by_ref.get(ref_num, {}).get("quotes", [])
        summary = details_by_ref.get(ref_num, {}).get("summary", [])
        extra = snippets_by_ref.get(ref_num, [])
        scores[ref_num] = 3 * len(quotes) + 2 * len(summary) + len(extra)

    selected_refs: set[int] = set(details_by_ref.keys())
    refs_sorted = sorted(scores.keys(), key=lambda r: (-scores.get(r, 0), r))
    for ref_num in refs_sorted:
        if len(selected_refs) >= 20:
            break
        if scores.get(ref_num, 0) <= 0:
            continue
        selected_refs.add(ref_num)

    if len(selected_refs) < 20:
        # Fall back: include remaining refs even if not cited, to reach 20.
        for ref_num in refs_sorted:
            if len(selected_refs) >= 20:
                break
            selected_refs.add(ref_num)

    ordered_refs = sorted(
        selected_refs,
        key=lambda r: (0 if r in details_by_ref else 1, -scores.get(r, 0), r),
    )

    sources: List[ParsedSource] = []
    for idx, ref_num in enumerate(ordered_refs, start=1):
        row = table_by_ref.get(ref_num, {})
        ref_info = ref_map.get(ref_num, {})

        title = (row.get("title") or ref_info.get("title") or "").strip()
        author = (row.get("author") or "Unbekannt").strip()
        year = (row.get("year") or "k.A.").strip()
        medium = (row.get("medium") or "unknown").strip()
        url = (ref_info.get("url") or "").strip()

        details = details_by_ref.get(ref_num, {})
        quotes = details.get("quotes", [])
        summary = details.get("summary", [])
        extra_snips = snippets_by_ref.get(ref_num, [])

        sources.append(
            ParsedSource(
                place_code="DELPHI",
                ordinal=idx,
                title=title,
                author=author,
                date_or_year=year,
                medium=medium,
                url=url,
                quotes=quotes,
                summary_points=summary,
                raw_snippets=extra_snips,
                source_ref_nums=[ref_num],
            )
        )

    if len(sources) != 20:
        raise RuntimeError(f"Delphi selection failed: expected 20 sources, got {len(sources)}")

    # Synthesis for Delphi is: pre + analysis content in detail_block after Quelle section
    synthesis_post = _extract_delphi_post_synthesis(detail_block)
    synthesis = "\n\n".join([p for p in [synthesis_pre, synthesis_post] if p]).strip()

    return synthesis, sources


def _parse_delphi_table(table_block: str) -> List[Dict[str, Any]]:
    # Very lightweight parser: expects rows in pattern:
    # <nr>\n<title>\n<author>\n<year>\n<medium>\n[ref]
    lines = [ln.strip() for ln in table_block.splitlines() if ln.strip()]

    # Find the first numeric row after header "Nr."
    out: List[Dict[str, Any]] = []
    i = 0
    while i < len(lines):
        if lines[i].isdigit():
            nr = int(lines[i])
            if i + 5 >= len(lines):
                break
            title = lines[i + 1]
            author = lines[i + 2]
            year = lines[i + 3]
            medium = lines[i + 4]
            ref_raw = lines[i + 5]
            m = re.match(r"^\[(\d+)\]$", ref_raw)
            ref_num = int(m.group(1)) if m else -1
            out.append(
                {
                    "nr": nr,
                    "title": title,
                    "author": author,
                    "year": year,
                    "medium": medium,
                    "ref_num": ref_num,
                }
            )
            i += 6
        else:
            i += 1

    # Ensure ordering 1..20
    out.sort(key=lambda r: r["nr"])
    return out


def _parse_delphi_quelle_details(detail_block: str) -> Dict[int, Dict[str, Any]]:
    # Extract blocks starting with "Quelle N:"
    details: Dict[int, Dict[str, Any]] = {}
    for m in re.finditer(r"(?m)^Quelle\s+(\d+):\s+(.+?)\s*(?:\[[^\]]+\])?\s*$", detail_block):
        n = int(m.group(1))
        start = m.end()
        end = None
        m_next = re.search(r"(?m)^Quelle\s+\d+:\s+", detail_block[start:])
        if m_next:
            end = start + m_next.start()
        else:
            end = len(detail_block)
        block = detail_block[start:end].strip()
        # Extract quotes in a single line after "• Zitate:"
        q_line = _extract_line_after_label(block, "Zitate")
        quotes: List[str] = []
        if q_line:
            for part in q_line.split(" / "):
                part = part.strip()
                if part:
                    quotes.append(part.strip("„“"))
        summary_block = _extract_block_after_label(block, "Zusammenfassung")
        summary = _extract_bullets(summary_block) if summary_block else []
        details[n] = {"quotes": quotes, "summary": summary}
    return details


def _extract_line_after_label(block: str, label: str) -> str:
    m = re.search(rf"(?m)^\s*•\s*{re.escape(label)}:\s*(.+)\s*$", block)
    return m.group(1).strip() if m else ""


def _extract_block_after_label(block: str, label: str) -> str:
    m = re.search(rf"(?m)^\s*•\s*{re.escape(label)}:\s*$", block)
    if not m:
        return ""
    start = m.end()
    # until next "• " or next "Quelle " or EOF
    end = len(block)
    m2 = re.search(r"(?m)^(?:\s*•\s+|Quelle\s+\d+:\s+)", block[start:])
    if m2:
        end = start + m2.start()
    return block[start:end].strip()


def _parse_numbered_url_list(source_list_block: str) -> Dict[int, Dict[str, str]]:
    # Format: "1. Title, https://..."
    out: Dict[int, Dict[str, str]] = {}
    for line in source_list_block.splitlines():
        line = line.strip()
        m = re.match(r"^(\d+)\.\s+(.+?),\s+(https?://\S+)$", line)
        if not m:
            continue
        n = int(m.group(1))
        title = m.group(2).strip()
        url = m.group(3).strip()
        out[n] = {"title": title, "url": url}
    return out


def _extract_snippets_by_ref(detail_block: str) -> Dict[int, List[str]]:
    # Consider any non-empty line containing [n] citations as a "snippet".
    out: Dict[int, List[str]] = {}
    for line in detail_block.splitlines():
        line = line.strip()
        if not line:
            continue
        refs = _extract_citations(line)
        if not refs:
            continue
        # Skip the Quelle header lines themselves (those are handled separately).
        if line.startswith("Quelle "):
            continue
        for ref in refs:
            out.setdefault(ref, []).append(line)
    return out


def _extract_delphi_post_synthesis(detail_block: str) -> str:
    # Take everything after the last "Quelle" block (usually after Quelle 10).
    # Heuristic: find "Somatik des Aufstiegs" header.
    m = re.search(r"(?m)^Somatik des Aufstiegs:", detail_block)
    if not m:
        return ""
    return detail_block[m.start() :].strip()


def _dp002_rewrite_synthesis(place_code: str, raw_synthesis: str, sources: List[Dict[str, Any]]) -> str:
    # Minimal rewrite: keep structure, but add epistemic frame and avoid factual metaphysics.
    # We do not attempt to preserve the original prose verbatim.
    place = PLACE_CONFIG[place_code]["primary_place"]
    src_count = len(sources)
    tiers = {"A": 0, "B": 0, "C": 0, "D": 0}
    types: Dict[str, int] = {}
    for s in sources:
        tiers[s["reliability_tier"]] += 1
        types[s["source_type"]] = types.get(s["source_type"], 0) + 1

    type_lines = ", ".join(f"{k}={v}" for k, v in sorted(types.items(), key=lambda kv: (-kv[1], kv[0])))

    incoming_name = PLACE_CONFIG[place_code]["incoming"]
    return "\n".join(
        [
            f"# SYNTHESIS — {place} (Research) — {src_count} sources",
            "",
            f"- Created: {synthesis_date_from_sources(sources)}",
            "- Epistemic hygiene (DP-002): this synthesis describes *reported* perceptions/frames; metaphysical/causal claims are not treated as facts.",
            f"- Source tiers: A={tiers['A']}, B={tiers['B']}, C={tiers['C']}, D={tiers['D']}",
            f"- Source types: {type_lines}",
            "",
            "## Reported resonance patterns (comparability-focused)",
            "- Body/somatics: recurring references to heat, exertion, vibration, breath/voice, or embodied constraint (where present in sources).",
            "- Space/material: architecture/topography as a choreography (thresholds, enclosures, portals, cliffs, caves/underground, sea-horizon, stadium/theatre).",
            "- Time: deep-time awe + subjective time dilation/\"before-after\" framing (coded as perception/interpretation, not objective time shifts).",
            "- Symbolic/authority frames: place is often stabilized via mythic overlays or authority-transfer (coded as interpretive frames).",
            "- Social/museumization: access control, curation, crowding and rules can amplify or dampen reported intensity; treated as confounders, not essence.",
            "",
            "## Notes on limitations",
            "- Bundle text mixes direct quotes and higher-level paraphrase; per-source events in JSON mark `raw_vs_claim` and include DP-002 notes.",
            "- Non-first-person sources are modeled as described/reported properties only.",
            "",
            "## Source bundle",
            f"- Input file: `incoming/{incoming_name}` (kept in-repo; not copied verbatim here to keep DP-002 framing tight).",
            "",
        ]
    ).strip() + "\n"


def synthesis_date_from_sources(sources: List[Dict[str, Any]]) -> str:
    # All created_at values should be identical; pick the first.
    if not sources:
        return ""
    return sources[0].get("created_at", "")


def _bundle_markdown(place_code: str, sources: List[Dict[str, Any]], date_str: str) -> str:
    place = PLACE_CONFIG[place_code]["primary_place"]
    lines: List[str] = [
        f"# BUNDLE — {place} (Research) — {date_str}",
        "",
        "- DP-002: Quotes are truncated to <=25 words; metaphysical/causal claims are not treated as facts.",
        "",
        f"## Sources ({len(sources)})",
        "",
    ]
    for s in sources:
        lines.append(f"### {s['id']} — {s['title']}")
        lines.append(f"- Author: {s.get('author','') or 'unknown'}")
        lines.append(f"- Date/Year: {s.get('date_or_year','') or 'unknown'}")
        lines.append(f"- Medium: {s.get('medium','') or 'unknown'}")
        lines.append(f"- URL: {s.get('url','') or 'unknown'}")
        lines.append(f"- source_type: {s['source_type']}; reliability_tier: {s['reliability_tier']}")
        if s.get("quotes"):
            lines.append("- Quotes (<=25w):")
            for q in s["quotes"][:4]:
                lines.append(f"  - \"{_clean_quote_text(q)}\"")
        if s.get("summary_points"):
            lines.append("- Summary points (bundle-paraphrase):")
            for p in s["summary_points"][:6]:
                lines.append(f"  - {_word_trim(p, 25)}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _write_bundle_and_synthesis(place_code: str, date_str: str, raw_synthesis: str, sources_meta: List[Dict[str, Any]]) -> None:
    bundle_path = OUT_BUNDLES / f"BUNDLE-{place_code}-RESEARCH-{date_str}.md"
    synthesis_path = OUT_SYNTHESIS / f"SYNTHESIS-{place_code}-RESEARCH-{date_str}.md"

    bundle_md = _bundle_markdown(place_code, sources_meta, date_str)
    synthesis_md = _dp002_rewrite_synthesis(place_code, raw_synthesis, sources_meta)

    bundle_path.write_text(bundle_md, encoding="utf-8")
    synthesis_path.write_text(synthesis_md, encoding="utf-8")


def _build_sources_from_bundle(place_code: str, date_str: str) -> Tuple[str, List[ParsedSource]]:
    incoming_path = INCOMING_DIR / PLACE_CONFIG[place_code]["incoming"]
    if not incoming_path.exists():
        raise FileNotFoundError(str(incoming_path))
    text = _read_text(incoming_path)
    if place_code == "ARUNACHALA":
        return _parse_arunachala(text)
    if place_code == "MALTA":
        return _parse_malta(text)
    if place_code == "DELPHI":
        return _parse_delphi(text)
    raise ValueError(place_code)


def _place_focus_for(place_code: str) -> Dict[str, Any]:
    cfg = PLACE_CONFIG[place_code]
    return {
        "primary_place": cfg["primary_place"],
        "place_type": cfg["place_type"],
        "geo_hints": [],
        "cultural_matrix_mentions": [],
    }


def _write_research_sources(place_code: str, date_str: str, parsed_sources: List[ParsedSource]) -> List[Dict[str, Any]]:
    place_focus = _place_focus_for(place_code)
    out_meta: List[Dict[str, Any]] = []

    for idx, ps in enumerate(parsed_sources, start=1):
        source_id = f"SRC-{place_code}-{idx:04d}"
        source_type = _infer_source_type(ps.medium, ps.url, ps.author)
        reliability_tier = _infer_reliability_tier(source_type, ps.url, ps.author, ps.medium)

        if source_type not in ALLOWED_SOURCE_TYPES:
            raise RuntimeError(f"Invalid source_type inferred: {source_type} for {source_id}")
        if reliability_tier not in ALLOWED_RELIABILITY_TIERS:
            raise RuntimeError(f"Invalid reliability_tier inferred: {reliability_tier} for {source_id}")

        meta = {
            "id": source_id,
            "place_code": place_code,
            "created_at": date_str,
            "bundle_ref_nums": ps.source_ref_nums,
            "title": ps.title,
            "author": ps.author,
            "date_or_year": ps.date_or_year,
            "medium": ps.medium,
            "url": ps.url,
            "source_type": source_type,
            "reliability_tier": reliability_tier,
            "epistemic_notes": "DP-002: treat metaphysical/causal claims as claims; encode as frames, not facts.",
        }

        _write_json(OUT_SRC_META / f"{source_id}.json", meta)

        candidates: List[Tuple[str, str]] = []
        for q in ps.quotes:
            candidates.append(("quote", q))
        for p in ps.summary_points:
            candidates.append(("summary_point", p))
        for sn in ps.raw_snippets:
            candidates.append(("bundle_synthesis_line", sn))
        if ps.title:
            candidates.append(("title_frame", ps.title))
        if ps.medium:
            candidates.append(("medium_frame", ps.medium))

        resonance = _build_resonance_for_source(source_id, place_code, place_focus, meta, candidates)
        _write_json(OUT_SRC_RESONANCE / f"{source_id}_resonance.json", resonance)

        # Keep quotes/summary in bundle MD as well.
        meta["quotes"] = ps.quotes
        meta["summary_points"] = ps.summary_points
        out_meta.append(meta)

    return out_meta


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _rehoming_transcript_resonance(date_str: str) -> Dict[str, Dict[str, Any]]:
    # Returns transcript_meta dict per place code for later aggregation.
    transcript_inputs = {
        "ARUNACHALA": V0_TRANSCRIPT_RESONANCE_DIR / "TZ-PLACE-ARUNACHALA-FRANK-STONER-ENGELMAYER-0001_resonance.json",
        "MALTA": V0_TRANSCRIPT_RESONANCE_DIR / "TZ-PLACE-MALTA-0001_resonance.json",
        "DELPHI": V0_TRANSCRIPT_RESONANCE_DIR / "TZ-PLACE-DELPHI-0001_resonance.json",
    }

    out_meta: Dict[str, Dict[str, Any]] = {}
    for place_code, in_path in transcript_inputs.items():
        if not in_path.exists():
            raise FileNotFoundError(str(in_path))
        d = _load_json(in_path)

        canonical_source_id = f"TZ-PLACE-{place_code}-FRANK-STONER-ENGELMAYER-0001"
        out_path = OUT_SRC_RESONANCE / f"{canonical_source_id}_resonance.json"

        # Validation + enrichment
        _ensure_event_ids(d.get("resonance_events", []))
        for ev in d.get("resonance_events", []):
            if "raw_vs_claim" not in ev:
                layers = ev.get("layer", [])
                triggers = ev.get("triggers", [])
                if "R5" in layers or "authority_projection" in triggers or "mythic_context" in triggers:
                    ev["raw_vs_claim"] = "interpretive_claim"
                else:
                    ev["raw_vs_claim"] = "raw_perception"

        speaker_profile = _build_speaker_profile(canonical_source_id, d.get("resonance_events", []))

        out_obj = {
            "id": f"{canonical_source_id}-RESONANCE",
            "source_id": canonical_source_id,
            "created_at": date_str,
            "quality_flags": {"source_type": "first_person_report", "reliability_tier": "B"},
            "place_focus": d.get("place_focus", {}),
            "resonance_events": d.get("resonance_events", []),
            "aggregate_profile": d.get("aggregate_profile", {}),
            "speaker_profile": speaker_profile,
            "legacy": {
                "v0_path": str(in_path.relative_to(REPO_ROOT)),
                "v0_source_id": d.get("source_id", ""),
                "note": "v0 re-homed + enriched (raw_vs_claim, speaker_profile).",
            },
        }

        _write_json(out_path, out_obj)

        out_meta[place_code] = {
            "id": canonical_source_id,
            "created_at": date_str,
            "title": f"Frank 'Stoner' Engelmayer transcript — {PLACE_CONFIG[place_code]['primary_place']}",
            "author": "Frank Engelmayer (alias: Stoner)",
            "date_or_year": date_str,
            "medium": "transcript (first-person)",
            "url": "",
            "source_type": "first_person_report",
            "reliability_tier": "B",
        }

    return out_meta


def _ensure_event_ids(events: List[Dict[str, Any]]) -> None:
    used: set[str] = set()
    for ev in events:
        eid = ev.get("event_id")
        if isinstance(eid, str) and eid:
            used.add(eid)

    next_num = 1
    for ev in events:
        eid = ev.get("event_id")
        if isinstance(eid, str) and eid:
            continue
        while f"RE-{next_num:04d}" in used:
            next_num += 1
        ev["event_id"] = f"RE-{next_num:04d}"
        used.add(ev["event_id"])
        next_num += 1


def _build_speaker_profile(source_id: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Dominant motifs: simple counts over triggers/channels + projection risk notes.
    trigger_counts: Dict[str, int] = {}
    channel_counts: Dict[str, int] = {}
    for e in events:
        for t in e.get("triggers", []):
            trigger_counts[t] = trigger_counts.get(t, 0) + 1
        for c in e.get("channel", []):
            channel_counts[c] = channel_counts.get(c, 0) + 1

    dominant_triggers = [k for k, _ in sorted(trigger_counts.items(), key=lambda kv: (-kv[1], kv[0]))][:8]
    dominant_channels = [k for k, _ in sorted(channel_counts.items(), key=lambda kv: (-kv[1], kv[0]))][:6]

    def event_text(e: Dict[str, Any]) -> str:
        return f"{e.get('excerpt','')} {e.get('notes','')}".lower()

    def refs_where(pred, limit: int = 8) -> List[str]:
        out: List[str] = []
        for e in events:
            if pred(e):
                out.append(f"{source_id}:{e.get('event_id')}")
            if len(out) >= limit:
                break
        return out

    agent_terms = ["guru", "lektion", "lehr", "oracle", "orakel"]
    agent_verbs = ["genommen", "erteilt", "lehrt", "teach", "teaches", "guides"]
    place_tokens = ["berg", "mountain", "ort", "place", "arunachala", "delphi", "malta"]

    def is_entitization(e: Dict[str, Any]) -> bool:
        txt = event_text(e)
        return any(t in txt for t in agent_terms) or (any(p in txt for p in place_tokens) and any(v in txt for v in agent_verbs))

    def is_mirror_identity(e: Dict[str, Any]) -> bool:
        txt = event_text(e)
        return any(k in txt for k in ["spiegel", "mirror", "erkenne", "selbst", "identity", "ego", "selbsterkennt"])

    def is_museumization_tension(e: Dict[str, Any]) -> bool:
        return "social_control_barrier" in (e.get("triggers") or [])

    def is_ritual_amplification(e: Dict[str, Any]) -> bool:
        tr = set(e.get("triggers") or [])
        return "ritual_context" in tr or "ritual_imagination" in tr

    def is_sensory_anchor(e: Dict[str, Any]) -> bool:
        tr = set(e.get("triggers") or [])
        return any(t in tr for t in ["sensory_smell", "visual_form", "silence", "material_mass"])

    projection_refs = refs_where(is_entitization, limit=12)

    motifs = [
        {
            "motif_id": "SM-AUTHORITY-TRANSFER-PLACE",
            "label": "Authority transfer to place",
            "description": "Ort wird als Lehrinstanz/Orakel gerahmt; Autorität wird an Landschaft gebunden.",
            "evidence_refs": refs_where(is_entitization, limit=8),
        },
        {
            "motif_id": "SM-SELF-MIRROR-IDENTITY",
            "label": "Place-as-mirror / identity work",
            "description": "Selbsterkenntnis/Identität wird über Ortsbezug aktiviert ('Spiegel').",
            "evidence_refs": refs_where(is_mirror_identity, limit=8),
        },
        {
            "motif_id": "SM-MUSEUMIZATION-RESISTANCE",
            "label": "Museumization tension",
            "description": "Spannung zwischen 'lebendigem Ort' und Zäunen/Regeln/Inszenierung (falls vorhanden).",
            "evidence_refs": refs_where(is_museumization_tension, limit=6),
        },
        {
            "motif_id": "SM-RITUAL-AMPLIFICATION",
            "label": "Ritual amplification",
            "description": "Ritualkontexte (Pilgerweg, Reinigung, Gesang) als Intensitätsverstärker.",
            "evidence_refs": refs_where(is_ritual_amplification, limit=6),
        },
        {
            "motif_id": "SM-SENSORY-ANCHORS",
            "label": "Sensory anchors",
            "description": "Geruch, Licht, Hitze, Klang als Anker, an denen Deutungskaskaden hängen.",
            "evidence_refs": refs_where(is_sensory_anchor, limit=6),
        },
    ]

    return {
        "speaker_id": "FRANK-STONER-ENGELMAYER",
        "dominant_channels": dominant_channels,
        "dominant_triggers": dominant_triggers,
        "dominant_motifs": motifs,
        "projection_risk_notes": [
            {
                "risk_id": "PR-ENTITIZATION-PLACE",
                "description": "Interpretive/ontological framing where the place is treated as an agent/teacher; keep as frame, not fact.",
                "evidence_refs": projection_refs,
            }
        ],
    }


def _marker_match(marker_id: str, event: Dict[str, Any]) -> bool:
    ex = (event.get("excerpt") or "").lower()
    notes = (event.get("notes") or "").lower()
    text = f"{ex} {notes}"
    triggers = set(event.get("triggers", []))
    channels = set(event.get("channel", []))
    layers = set(event.get("layer", []))

    if marker_id == "RP-MKR-PLACE-AS-AGENT-GURU-0001":
        agent_terms = ["guru", "lektion", "lehr", "lesson", "teacher", "oracle", "orakel"]
        agent_verbs = ["genommen", "erteilt", "lehrt", "teach", "teaches", "guides"]
        place_tokens = ["berg", "mountain", "arunachala", "delphi", "malta", "tempel", "temple", "ort", "place"]
        return any(t in text for t in agent_terms) or (any(p in text for p in place_tokens) and any(v in text for v in agent_verbs))
    if marker_id == "RP-MKR-ACOUSTIC-REVERBERATION-0002":
        return any(k in ex for k in ["acoustic", "akust", "echo", "reverber", "110 hz", "114 hz", "bell", "glocke"])
    if marker_id == "RP-MKR-VERTICAL-ASCENT-CHOREOGRAPHY-0003":
        return any(k in ex for k in ["uphill", "aufstieg", "stairs", "stufen", "serpent", "sacred way", "serpentinen"])
    if marker_id == "RP-MKR-CROWD-RITUAL-MASS-0004":
        return "ritual_context" in triggers and any(k in ex for k in ["million", "crowd", "pilger", "pilgr"])
    if marker_id == "RP-MKR-TIME-DENSITY-THINNING-0005":
        return "time" in channels and any(k in ex for k in ["timeless", "ewigkeit", "phases", "before", "after", "zurück"])
    if marker_id == "RP-MKR-SENSORY-SMELL-FUMES-0006":
        return "sensory_smell" in triggers
    if marker_id == "RP-MKR-ACCESS-CONTROL-MUSEUMIZATION-0007":
        return "social_control_barrier" in triggers
    if marker_id == "RP-MKR-DEEP-TIME-AWE-0008":
        return "historical_depth" in triggers or any(k in ex for k in ["before the pyramids", "stonehenge", "7000", "jahrtausend", "zeit-tiefe"])
    if marker_id == "RP-MKR-WOMB-UNDERWORLD-METAPHOR-0009":
        return any(k in ex for k in ["womb", "mutterleib", "unterwelt", "geburts"])
    if marker_id == "RP-MKR-LIGHT-QUALITY-MYSTIC-0010":
        return "visual_form" in triggers and any(k in ex for k in ["light", "licht", "gold", "rose", "myst"])
    if marker_id == "RP-MKR-MYTHIC-OVERLAY-DOCTRINAL-0011":
        return "mythic_context" in triggers or any(k in ex for k in ["apollo", "gaia", "python", "shiva", "lingam", "omphalos"])
    if marker_id == "RP-MKR-SELF-MIRROR-IDENTITY-0012":
        return any(k in ex for k in ["mirror", "spiegel", "erkenne", "selbst", "identity", "ego"])
    return False


def _collect_all_events_for_place(place_code: str) -> List[Tuple[str, Dict[str, Any]]]:
    # Returns list of (source_id, event)
    events: List[Tuple[str, Dict[str, Any]]] = []
    for path in OUT_SRC_RESONANCE.glob(f"*{place_code}*resonance.json"):
        obj = _load_json(path)
        sid = obj.get("source_id", path.stem.replace("_resonance", ""))
        for e in obj.get("resonance_events", []):
            events.append((sid, e))
    return events


def _build_place_aggregate(place_code: str, date_str: str, sources_meta: List[Dict[str, Any]], transcript_meta: Dict[str, Any]) -> Dict[str, Any]:
    place_focus = _place_focus_for(place_code)

    tiers = {"A": 0, "B": 0, "C": 0, "D": 0}
    for s in sources_meta:
        tiers[s["reliability_tier"]] += 1
    tiers[transcript_meta["reliability_tier"]] += 1

    events = _collect_all_events_for_place(place_code)
    channel_counts: Dict[str, int] = {}
    trigger_counts: Dict[str, int] = {}
    for _, e in events:
        for c in e.get("channel", []):
            channel_counts[c] = channel_counts.get(c, 0) + 1
        for t in e.get("triggers", []):
            trigger_counts[t] = trigger_counts.get(t, 0) + 1

    dominant_channels = [k for k, _ in sorted(channel_counts.items(), key=lambda kv: (-kv[1], kv[0]))][:6]
    dominant_triggers = [k for k, _ in sorted(trigger_counts.items(), key=lambda kv: (-kv[1], kv[0]))][:10]

    marker_candidates: List[Dict[str, Any]] = []
    museumization: List[Dict[str, Any]] = []

    for m in GLOBAL_MARKERS:
        marker_id = m["marker_id"]
        evidence_refs: List[str] = []
        for sid, ev in events:
            if _marker_match(marker_id, ev):
                evidence_refs.append(f"{sid}:{ev['event_id']}")
            if len(evidence_refs) >= 6:
                break
        if evidence_refs:
            risk = "DP-002: treat as pattern marker, not proof of metaphysical causality; consider genre + tourism curation confounds."
            marker_candidates.append(
                {
                    "marker_id": marker_id,
                    "definition": m["definition"],
                    "evidence_refs": evidence_refs[:5],
                    "risk_notes": risk,
                }
            )

        if marker_id == "RP-MKR-ACCESS-CONTROL-MUSEUMIZATION-0007" and evidence_refs:
            museumization.append(
                {
                    "overlay_id": "MUSEUMIZATION-ACCESS-CONTROL",
                    "description": "Reported/observed curation, rules, barriers or protective infrastructure shaping experience.",
                    "evidence_refs": evidence_refs[:6],
                    "notes": "Confounder: intensity may be amplified by restriction/rarity or reduced by staging.",
                }
            )

        if marker_id == "RP-MKR-CROWD-RITUAL-MASS-0004" and evidence_refs:
            museumization.append(
                {
                    "overlay_id": "RITUAL-CROWD-DENSITY",
                    "description": "Ritual/crowd density as an overlay shaping subjective intensity (synchronization, noise/heat load, expectation).",
                    "evidence_refs": evidence_refs[:6],
                    "notes": "Confounder: collective dynamics can be mistaken for place-intrinsic signature; treat as contextual overlay.",
                }
            )

    # Keep marker list within 8–15 markers (prefer those with most evidence)
    marker_candidates.sort(key=lambda mc: (-len(mc.get("evidence_refs", [])), mc["marker_id"]))
    marker_candidates = marker_candidates[:15]

    stability_notes = (
        "Dominant channels/triggers computed over all extracted events (research + Frank transcript). "
        "Interpretive claims are separated via `raw_vs_claim`."
    )

    return {
        "id": f"TZ-PLACE-{place_code}-AGG-0001-RESONANCE-AGGREGATE",
        "created_at": date_str,
        "place_focus": place_focus,
        "source_set": {
            "count": len(sources_meta) + 1,
            "tiers": tiers,
            "notes": "Includes 1 dense Frank transcript (tier B) + research bundle sources.",
        },
        "dominant_channels": dominant_channels,
        "dominant_triggers": dominant_triggers,
        "marker_candidates": marker_candidates,
        "stability_notes": stability_notes,
        "museumization_overlays": museumization,
    }


def _build_marker_matrix(date_str: str) -> Dict[str, Any]:
    places = ["ARUNACHALA", "MALTA", "DELPHI"]
    matrix: List[Dict[str, Any]] = []

    for m in GLOBAL_MARKERS:
        row = {"marker_id": m["marker_id"], "definition": m["definition"], "places": {}}
        for p in places:
            events = _collect_all_events_for_place(p)
            matching = [f"{sid}:{ev['event_id']}" for sid, ev in events if _marker_match(m["marker_id"], ev)]
            strength = 0
            if len(matching) >= 10:
                strength = 3
            elif len(matching) >= 5:
                strength = 2
            elif len(matching) >= 1:
                strength = 1
            row["places"][p] = {"present": strength > 0, "strength_0_3": strength, "evidence_refs": matching[:6]}
        matrix.append(row)

    return {
        "id": "COMP-RESONANCE-PLACES-0001-MARKER-MATRIX",
        "created_at": date_str,
        "places": places,
        "markers": matrix,
        "notes": "Strength is heuristic (event-count based). Use as comparative signal only, not as proof.",
    }


def _cross_place_report(date_str: str, marker_matrix: Dict[str, Any]) -> str:
    # Identify signatures based on strengths
    places = marker_matrix["places"]
    markers = marker_matrix["markers"]

    def strengths(marker_row: Dict[str, Any]) -> Dict[str, int]:
        return {p: int(marker_row["places"][p]["strength_0_3"]) for p in places}

    place_unique: Dict[str, List[str]] = {p: [] for p in places}
    generics: List[str] = []
    for row in markers:
        s = strengths(row)
        present_places = [p for p in places if s[p] > 0]
        if len(present_places) == 3:
            generics.append(row["marker_id"])
        if len(present_places) == 1:
            place_unique[present_places[0]].append(row["marker_id"])

    # Speaker-signature approximation: markers with stronger presence in transcripts than research are not computed here;
    # we instead flag likely ones.
    speaker_signature = ["RP-MKR-PLACE-AS-AGENT-GURU-0001", "RP-MKR-MYTHIC-OVERLAY-DOCTRINAL-0011"]
    genre_signature = ["RP-MKR-ACCESS-CONTROL-MUSEUMIZATION-0007", "RP-MKR-DEEP-TIME-AWE-0008"]

    lines: List[str] = [
        "# COMP-RESONANCE-PLACES-0001 — Cross-place report",
        "",
        f"- Created: {date_str}",
        "- DP-002: Report distinguishes raw perception vs interpretive claims; no metaphysical claims asserted as facts.",
        "",
        "## Marker matrix (strength 0–3)",
        "",
    ]

    # Simple table
    header = "| marker_id | Arunachala | Malta | Delphi |"
    sep = "|---|---:|---:|---:|"
    lines.extend([header, sep])
    for row in markers:
        a = row["places"]["ARUNACHALA"]["strength_0_3"]
        m = row["places"]["MALTA"]["strength_0_3"]
        d = row["places"]["DELPHI"]["strength_0_3"]
        lines.append(f"| {row['marker_id']} | {a} | {m} | {d} |")

    lines.extend(
        [
            "",
            "## Findings",
            "",
            "### Place-signatures (unique markers)",
            f"- Arunachala: {', '.join(place_unique['ARUNACHALA']) or 'none in current marker set'}",
            f"- Malta: {', '.join(place_unique['MALTA']) or 'none in current marker set'}",
            f"- Delphi: {', '.join(place_unique['DELPHI']) or 'none in current marker set'}",
            "",
            "### Sacred-frame generics (present everywhere)",
            f"- {', '.join(generics) or 'none'}",
            "",
            "### Speaker-signature (mostly Frank; heuristic)",
            f"- {', '.join(speaker_signature)}",
            "",
            "### Genre-signature (blogs/forums vs academic/official; heuristic)",
            f"- {', '.join(genre_signature)}",
            "",
            "## Next sources to add (to reduce bias; suggested types)",
            "",
            "### Arunachala",
            "- Tier-A: peer-reviewed pilgrimage/phenomenology study (avoid devotional-only selection).",
            "- Tier-A: official site/ashram visitor guidelines + crowd management documents (museumization/crowding confounds).",
            "- Tier-B: skeptical travel essay focusing on heat/crowd logistics (non-devotional voice).",
            "- Tier-C: forum threads with negative experiences (capture valence range).",
            "- Tier-A/B: local-language sources (Tamil) with translation notes (reduce English-only bias).",
            "",
            "### Malta",
            "- Tier-A: peer-reviewed archaeoacoustics replication/critique (measurement stability).",
            "- Tier-A: Heritage Malta / UNESCO documentation on shelters + visitor rules (curation confounds).",
            "- Tier-B: architecture/phenomenology essay not centered on 'mystery' framing.",
            "- Tier-C: visitor reviews focused on restrictions/flow (access-control effects).",
            "- Tier-A/B: archaeological synthesis on temple chronology/material sourcing (material-depth anchor).",
            "",
            "### Delphi",
            "- Tier-A: UNESCO WHC page + conservation/visitor management reports (museumization overlay ground truth).",
            "- Tier-A: peer-reviewed work on Delphic oracle/pneuma hypotheses (separate science vs myth frames).",
            "- Tier-B: off-season travel essay emphasizing silence/topography (less tour-bus bias).",
            "- Tier-C: contemporary forum discourse (gaming/Instagram) to capture modern re-mediation.",
            "- Tier-B: local Greek guide narratives (reduce Anglophone framing).",
            "",
        ]
    )

    return "\n".join(lines).strip() + "\n"


def _validate_outputs(place_sources: Dict[str, List[Dict[str, Any]]], transcripts_meta: Dict[str, Dict[str, Any]]) -> List[str]:
    problems: List[str] = []

    # Validate per-source metadata required fields
    for place_code, sources in place_sources.items():
        expected = len(sources)
        for s in sources:
            if s["source_type"] not in ALLOWED_SOURCE_TYPES:
                problems.append(f"{s['id']}: invalid source_type {s['source_type']}")
            if s["reliability_tier"] not in ALLOWED_RELIABILITY_TIERS:
                problems.append(f"{s['id']}: invalid reliability_tier {s['reliability_tier']}")
            if not s.get("url"):
                problems.append(f"{s['id']}: missing url")
        if expected == 0:
            problems.append(f"{place_code}: no sources parsed")

    # Validate resonance files have required fields
    for path in OUT_SRC_RESONANCE.glob("*_resonance.json"):
        obj = _load_json(path)
        for ev in obj.get("resonance_events", []):
            for req in ["excerpt", "layer", "channel", "valence", "intensity_0_5", "triggers", "raw_vs_claim", "notes", "event_id"]:
                if req not in ev:
                    problems.append(f"{path.name}:{ev.get('event_id','?')}: missing {req}")
    # Validate transcript meta presence for each place
    for place_code in PLACE_CONFIG.keys():
        if place_code not in transcripts_meta:
            problems.append(f"{place_code}: missing transcript meta (rehoming failed)")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Build resonance_places dataset from incoming bundles.")
    parser.add_argument("--date", default="2026-02-23", help="YYYY-MM-DD (used for output filenames and created_at)")
    args = parser.parse_args()

    date_str = args.date.strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        raise SystemExit("Invalid --date format; expected YYYY-MM-DD")

    _ensure_dirs()
    _cleanup_previous_outputs()

    # Parse and write research sources
    place_sources_meta: Dict[str, List[Dict[str, Any]]] = {}
    raw_synth: Dict[str, str] = {}

    for place_code in ["ARUNACHALA", "MALTA", "DELPHI"]:
        synthesis_text, parsed_sources = _build_sources_from_bundle(place_code, date_str)
        raw_synth[place_code] = synthesis_text
        sources_meta = _write_research_sources(place_code, date_str, parsed_sources)
        place_sources_meta[place_code] = sources_meta
        _write_bundle_and_synthesis(place_code, date_str, synthesis_text, sources_meta)

    # Re-home + enrich transcript resonance (v0)
    transcripts_meta = _rehoming_transcript_resonance(date_str)

    # Build per-place aggregates
    for place_code in ["ARUNACHALA", "MALTA", "DELPHI"]:
        agg = _build_place_aggregate(place_code, date_str, place_sources_meta[place_code], transcripts_meta[place_code])
        _write_json(OUT_AGG / f"TZ-PLACE-{place_code}-AGG-0001_resonance_aggregate.json", agg)

    # Comparative outputs
    marker_matrix = _build_marker_matrix(date_str)
    _write_json(OUT_COMP / "COMP-RESONANCE-PLACES-0001_marker_matrix.json", marker_matrix)
    report_md = _cross_place_report(date_str, marker_matrix)
    (OUT_COMP / "COMP-RESONANCE-PLACES-0001_cross_place_report.md").write_text(report_md, encoding="utf-8")

    problems = _validate_outputs(place_sources_meta, transcripts_meta)

    # Console summary
    print("=== RESONANCE PLACES DATASET BUILD SUMMARY ===")
    for place_code in ["ARUNACHALA", "MALTA", "DELPHI"]:
        sources_meta = place_sources_meta[place_code]
        tiers = {"A": 0, "B": 0, "C": 0, "D": 0}
        for s in sources_meta:
            tiers[s["reliability_tier"]] += 1
        tiers["B"] += 1  # transcript
        print(f"- {place_code}: sources processed (bundle) = {len(sources_meta)}; tiers = {tiers}")

        # Transcript events count
        transcript_path = OUT_SRC_RESONANCE / f"TZ-PLACE-{place_code}-FRANK-STONER-ENGELMAYER-0001_resonance.json"
        if transcript_path.exists():
            t_obj = _load_json(transcript_path)
            print(f"  - Transcript events extracted = {len(t_obj.get('resonance_events', []))}")

    print(f"- Output root: {OUT_ROOT.relative_to(REPO_ROOT)}")
    print(f"- Problems: {len(problems)}")
    for p in problems[:20]:
        print(f"  - {p}")

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
