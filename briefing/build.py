"""Scarica i feed, seleziona le notizie e genera la pagina del briefing.

Uso:  python -m briefing.build [--out site] [--fixtures DIR]
Con --fixtures legge i feed da file locali (per i test) invece che dalla rete.
"""

import argparse
import html
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import classify
from .sources import FEEDS, OUTLETS

ROME = ZoneInfo("Europe/Rome")
FIRST_ISSUE = date(2026, 10, 12)
ROOT = Path(__file__).resolve().parent.parent
USER_AGENT = "Mozilla/5.0 (compatible; BriefingMattiniero/1.0; +https://github.com/eyecontrol/briefing-news)"
PER_SECTION = 10
COUNTRY_PER_SECTION = 6

GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]


# ---------------------------------------------------------------- lettura feed

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/xml, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _local(tag):
    return tag.rsplit("}", 1)[-1].lower()


def _child(el, *names):
    for c in el:
        if _local(c.tag) in names:
            return c
    return None


def _text(el, *names):
    c = _child(el, *names)
    return (c.text or "").strip() if c is not None and c.text else ""


def _link(el):
    for c in el:
        if _local(c.tag) == "link":
            if c.get("href") and c.get("rel", "alternate") == "alternate":
                return c.get("href")
            if c.text and c.text.strip():
                return c.text.strip()
    guid = _text(el, "guid")
    return guid if guid.startswith("http") else ""


def parse_date(value):
    if not value:
        return None
    try:
        d = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        d = None
    if d is None:
        try:
            d = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def clean(text, limit=None):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r" ([.,;:!?])", r"\1", text)
    if limit and len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0].rstrip(",;:.-") + "…"
    return text


# Righe di servizio che i feed aggiungono in fondo al testo.
BOILER = re.compile(
    r"^(continue reading|read more|leggi (anche|tutto|l'articolo)|the post .* appeared first on|"
    r"sign up|subscribe|iscriviti|related:|correlat|photo:|foto:|\(?(c|©) )", re.IGNORECASE)
BODY_LIMIT = 6000


def paragraphs(text):
    """Testo dell'articolo come lista di paragrafi puliti (solo quello che il feed pubblica)."""
    text = re.sub(r"(?is)<(script|style|figure|figcaption|iframe)\b.*?</\1>", " ", text or "")
    text = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h\d|blockquote)>", "\n\n", text)
    out, total = [], 0
    for chunk in re.split(r"\n\s*\n", text):
        para = clean(chunk)
        if len(para) < 2 or BOILER.search(para):
            continue
        if out and para == out[-1]:
            continue
        if total + len(para) > BODY_LIMIT:
            break
        out.append(para)
        total += len(para)
    return out


def _loose_items(raw):
    """Lettura di riserva per feed con XML non valido: estrae i campi con espressioni regolari."""
    text = raw.decode("utf-8", errors="replace")
    root = ET.Element("feed")
    for block in re.findall(r"<(?:item|entry)\b.*?</(?:item|entry)>", text, re.S | re.I):
        el = ET.SubElement(root, "item")
        for name in ("title", "link", "guid", "description", "summary", "content:encoded", "content", "pubDate", "published", "updated", "dc:date"):
            m = re.search(rf"<{name}\b([^>]*)>(.*?)</{name}>", block, re.S | re.I)
            href = re.search(rf"<{name}\b[^>]*href=\"([^\"]+)\"", block, re.I) if name == "link" else None
            if not m and not href:
                continue
            child = ET.SubElement(el, name.split(":")[-1])
            if m:
                child.text = re.sub(r"^\s*<!\[CDATA\[(.*?)\]\]>\s*$", r"\1", m.group(2), flags=re.S)
            if href:
                child.set("href", href.group(1))
    return list(root)


def parse_feed(raw):
    """Restituisce una lista di dict {title, url, summary, published} da RSS, RDF o Atom."""
    try:
        root = ET.fromstring(raw)
        items = [el for el in root.iter() if _local(el.tag) in ("item", "entry")]
    except ET.ParseError:
        items = _loose_items(raw)
    out = []
    for el in items:
        title = clean(_text(el, "title"))
        url = _link(el)
        if not title or not url:
            continue
        summary = _text(el, "description", "summary", "encoded", "content")
        full = max((_text(el, n) for n in ("description", "summary", "encoded", "content")), key=len)
        body = paragraphs(full)
        if body and clean(body[0]) == title:
            body = body[1:]
        published = parse_date(_text(el, "pubdate", "published", "updated", "date"))
        out.append({"title": title, "url": url, "summary": clean(summary, 320), "body": body,
                    "published": published})
    return out


# ---------------------------------------------------------------- selezione

STOP = set("""
the and for with from that this have after over into about than more will what when says said
della delle degli dello dalla dalle dagli nella nelle negli sulla sulle sugli alla alle agli
come anche sono stato stata essere dopo prima contro mentre perche questo questa quello quella
oggi ieri ecco tutti tutto molto loro nostro their there been were which while
""".split())


def tokens(title):
    """Parole significative del titolo, tagliate a 5 lettere per unire singolare e plurale."""
    words = re.findall(r"[a-z0-9]+", classify.normalize(title))
    return {w[:5] for w in words if len(w) >= 4 and w not in STOP}


def cluster(items):
    """Raggruppa titoli simili (stessa notizia da testate diverse)."""
    groups = []
    for it in items:
        tk = tokens(it["title"])
        it["_tk"] = tk
        best = None
        for g in groups:
            inter = len(tk & g["tk"])
            if inter >= 3 and inter / max(1, min(len(tk), len(g["tk"]))) >= 0.5:
                best = g
                break
        if best:
            best["items"].append(it)
            best["tk"] |= tk
        else:
            groups.append({"tk": set(tk), "items": [it]})
    return groups


def select(raw_items, now):
    kept = []
    seen_urls = set()
    for it in raw_items:
        if it["url"] in seen_urls:
            continue
        seen_urls.add(it["url"])
        pub = it["published"]
        if pub is None or pub > now + timedelta(hours=1) or now - pub > timedelta(hours=it["max_age_h"]):
            continue
        if classify.is_excluded(it["title"], it["summary"], it["url"]):
            continue
        section = classify.pick_section(it["default"], it["title"], it["summary"])
        if not section:
            continue
        it["section"] = section
        it["countries"] = classify.countries(it["feed_country"], it["title"], it["summary"])
        kept.append(it)

    stories = []
    for g in cluster(kept):
        members = sorted(g["items"], key=lambda x: x["published"], reverse=True)
        main = members[0]
        sources = []
        for m in members:
            if m["source"] not in sources:
                sources.append(m["source"])
        age_h = (now - main["published"]).total_seconds() / 3600
        main["score"] = round(len(sources) * 10 + max(0, 24 - age_h) / 4, 2)
        main["also"] = sources[1:]
        # Testo da leggere nel briefing: quello della notizia scelta o, se è solo un sommario,
        # il più lungo pubblicato da un'altra testata sulla stessa notizia.
        richest = max(members, key=lambda m: sum(map(len, m.get("body", []))))
        main["body_src"] = None
        if sum(map(len, main.get("body", []))) < 400 and sum(map(len, richest.get("body", []))) >= 400:
            main["body"], main["body_src"] = richest["body"], {"src": richest["source"], "url": richest["url"]}
        main["countries"] = sorted({c for m in members for c in m["countries"]})
        stories.append(main)

    stories.sort(key=lambda s: s["score"], reverse=True)
    picked = []
    for key in classify.SECTIONS:
        sec = [s for s in stories if s["section"] == key]
        top = sec[:PER_SECTION]
        for code in ("IT", "RS"):
            top += [s for s in sec if code in s["countries"] and s not in top][:COUNTRY_PER_SECTION]
        picked += top
    picked.sort(key=lambda s: s["score"], reverse=True)
    return picked


# ---------------------------------------------------------------- pagina

def italian_date(d):
    return f"{GIORNI[d.weekday()]} {d.day} {MESI[d.month - 1]} {d.year}"


def when(published, local_now):
    p = published.astimezone(ROME)
    if p.date() == local_now.date():
        return p.strftime("%H:%M")
    if p.date() == local_now.date() - timedelta(days=1):
        return "Ieri"
    return p.strftime("%d/%m")


def render(stories, now, sources_ok):
    local = now.astimezone(ROME)
    issue = (local.date() - FIRST_ISSUE).days + 1
    year = (local.date() - FIRST_ISSUE).days // 365 + 1
    data = [{
        "t": s["section"],
        "c": s["countries"],
        "src": s["source"],
        "lang": OUTLETS[s["source"]][2],
        "time": when(s["published"], local),
        "h": s["title"],
        "p": s["summary"],
        "url": s["url"],
        "also": s["also"],
        "b": s.get("body") or [],
        "bs": s.get("body_src"),
    } for s in stories]
    groups = {}
    for name, (founded, group, _lang) in OUTLETS.items():
        groups.setdefault(group, []).append((founded, name))
    colophon = "\n".join(
        f'      <div><h3>{html.escape(g)}</h3><ul>\n' + "\n".join(
            f'        <li><span>{html.escape(n)}</span><span>{y}</span></li>' for y, n in items) + "\n      </ul></div>"
        for g, items in groups.items())
    page = (ROOT / "template" / "index.html").read_text(encoding="utf-8")
    replacements = {
        "__DATA__": json.dumps(data, ensure_ascii=False).replace("</", "<\\/"),
        "__SECTIONS__": json.dumps(classify.SECTIONS, ensure_ascii=False),
        "__DATE__": italian_date(local),
        "__ISSUE__": f"Anno {roman(year)} · N. {issue}",
        "__TIME__": local.strftime("%H:%M"),
        "__NSOURCES__": str(len(sources_ok)),
        "__NOUTLETS__": str(len(OUTLETS)),
        "__COLOPHON__": colophon,
    }
    for k, v in replacements.items():
        page = page.replace(k, v)
    return page


def roman(n):
    vals = [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


# ---------------------------------------------------------------- main

def load(feed, fixtures):
    if fixtures:
        name = re.sub(r"[^a-z0-9]+", "_", feed["url"].lower()).strip("_") + ".xml"
        path = Path(fixtures) / name
        if not path.exists():
            raise FileNotFoundError(path.name)
        raw = path.read_bytes()
    else:
        raw = fetch(feed["url"])
    return parse_feed(raw)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="site")
    ap.add_argument("--fixtures")
    ap.add_argument("--now", help="data/ora UTC ISO per i test")
    args = ap.parse_args(argv)
    now = datetime.fromisoformat(args.now).astimezone(timezone.utc) if args.now else datetime.now(timezone.utc)

    def job(feed):
        try:
            return feed, load(feed, args.fixtures), None
        except Exception as e:  # un feed che non risponde non deve fermare il briefing
            return feed, [], f"{type(e).__name__}: {e}"

    raw_items, ok_sources, report = [], set(), []
    with ThreadPoolExecutor(max_workers=12) as pool:
        for feed, items, err in pool.map(job, FEEDS):
            report.append((feed, len(items), err))
            if items:
                ok_sources.add(feed["source"])
            for it in items:
                it.update(source=feed["source"], default=feed["section"], feed_country=feed["country"],
                          max_age_h=feed["max_age_h"])
                raw_items.append(it)

    for feed, n, err in report:
        print(f"{'OK ' if not err else 'ERR'} {n:3d}  {feed['source']:<36} {feed['url']}" + (f"  -> {err}" if err else ""))

    stories = select(raw_items, now)
    by_sec = {k: sum(1 for s in stories if s["section"] == k) for k in classify.SECTIONS}
    print("\nPrime notizie:")
    for s in stories[:40]:
        print(f"  {s['section']} {','.join(s['countries']):<5} {s['source'][:16]:<16} {s['score']:5.1f} +{len(s['also'])}  {s['title'][:100]}")
    print("\nTesto leggibile nel briefing (caratteri medi per notizia):")
    lengths = {}
    for it in raw_items:
        lengths.setdefault(it["source"], []).append(sum(map(len, it.get("body", []))))
    rows = [f"{src}: {sum(ls) // len(ls)} (max {max(ls)})"
            for src, ls in sorted(lengths.items(), key=lambda x: -sum(x[1]) / len(x[1]))]
    print("\n".join("  " + r for r in rows))
    if os.environ.get("GITHUB_ACTIONS"):
        print("::notice title=Testo per testata::" + "%0A".join(rows))
    print(f"\nNotizie scelte: {len(stories)}  per sezione: {by_sec}  testate attive: {len(ok_sources)}/{len(OUTLETS)}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(render(stories, now, ok_sources), encoding="utf-8")
    (out / "feeds-report.txt").write_text(
        "\n".join(f"{'OK' if not e else 'ERRORE'}\t{n}\t{f['source']}\t{f['url']}\t{e or ''}" for f, n, e in report),
        encoding="utf-8")
    if not stories:
        print("Nessuna notizia raccolta: controlla i feed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
