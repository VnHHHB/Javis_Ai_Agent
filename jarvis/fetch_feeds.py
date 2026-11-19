"""Keo RSS/Atom bang requests + xml stdlib. Khong can feedparser.

Moi source loi thi bo qua source do, khong lam hong ca lan chay.
Dedupe theo link. Luu ra data/articles.json.
"""
import html
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import requests

HEADERS = {"User-Agent": "Jarvis-MVP/0.1 (personal feed reader)"}
TAG_RE = re.compile(r"<[^>]+>")


def clean(text: str) -> str:
    if not text:
        return ""
    text = TAG_RE.sub(" ", html.unescape(text))
    return re.sub(r"\s+", " ", text).strip()


def _text(el, names):
    for name in names:
        child = el.find(name)
        if child is not None and child.text:
            return child.text.strip()
    # Tim bat ky tag nao ket thuc bang /name (de xu ly namespace Atom/RSS)
    for child in el.iter():
        if child.tag.rsplit("}", 1)[-1] in names and child.text:
            return child.text.strip()
    return ""


def _link(el):
    # Atom: <link href="..."/>
    for child in el.iter():
        if child.tag.rsplit("}", 1)[-1] == "link":
            href = child.attrib.get("href")
            if href:
                return href
            if child.text:
                return child.text.strip()
    return _text(el, ["link", "guid", "id"])


def _date(el):
    raw = _text(el, ["pubDate", "published", "updated", "dc:date"])
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT",
                "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(raw, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except (ValueError, TypeError):
            continue
    return datetime.now(timezone.utc).isoformat()


def parse_feed(xml_bytes: bytes, source_name: str, kind: str):
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []
    items = []
    for el in root.iter():
        tag = el.tag.rsplit("}", 1)[-1]
        if tag not in ("item", "entry"):
            continue
        title = clean(_text(el, ["title"]))
        link = _link(el)
        summary = clean(_text(el, ["description", "summary", "content"]))
        if not title or not link:
            continue
        items.append({
            "title": title, "link": link, "summary": summary[:2000],
            "source": source_name, "kind": kind, "published": _date(el),
        })
    return items


def fetch_all(sources_path="sources.json", out_path="data/articles.json"):
    base = Path(__file__).resolve().parent.parent
    sources = json.loads((base / sources_path).read_text(encoding="utf-8"))["sources"]
    seen, articles, report = set(), [], {}
    for src in sources:
        try:
            r = requests.get(src["url"], headers=HEADERS, timeout=20)
            r.raise_for_status()
            found = parse_feed(r.content, src["name"], src.get("kind", "news"))
            new = 0
            for a in found:
                if a["link"] in seen:
                    continue
                seen.add(a["link"])
                articles.append(a)
                new += 1
            report[src["name"]] = f"OK, {new} bai moi / {len(found)} bai doc duoc"
        except Exception as e:  # noqa: BLE001 - moi source loi la binh thuong
            report[src["name"]] = f"LOI: {type(e).__name__}: {e}"
    # Giu lai bai cu neu co, dedupe theo link, moi nhat truoc
    out = base / out_path
    old = []
    if out.exists():
        try:
            old = json.loads(out.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            old = []
    merged = {a["link"]: a for a in old}
    merged.update({a["link"]: a for a in articles})
    all_articles = sorted(merged.values(), key=lambda a: a.get("published", ""), reverse=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(all_articles, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"total_stored": len(all_articles), "new_this_run": len(articles), "report": report}
