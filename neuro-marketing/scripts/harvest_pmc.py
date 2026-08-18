#!/usr/bin/env python3
"""Build a licensed, compressed neuromarketing research corpus from PMC.

The script searches NCBI E-utilities, retrieves only PMC Open Access packages
with commercial-use Creative Commons licenses, counts the main article PDF
pages, extracts the accompanying NXML, and writes a gzip-compressed JSONL
corpus plus a CSV catalog and resumable state file.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import html
import io
import json
import os
import re
import sys
import tarfile
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCES = SKILL_ROOT / "references"
DEFAULT_CORPUS = REFERENCES / "corpus.jsonl.gz"
DEFAULT_CATALOG = REFERENCES / "catalog.csv"
DEFAULT_STATE = REFERENCES / "corpus-state.json"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
OA_API = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
USER_AGENT = "NeuroMarketingSkill/1.0"
ALLOWED_LICENSES = {"CC0", "CC BY", "CC BY-SA", "CC BY-ND"}

QUERY_THEMES = {
    "consumer-neuroscience": 'neuromarketing[All Fields] OR "consumer neuroscience"[All Fields]',
    "brand-ad-neuro": (
        '(advertising[All Fields] OR brand[All Fields] OR branding[All Fields] '
        'OR logo[All Fields] OR packaging[All Fields]) AND '
        '(neuroscience[All Fields] OR brain[All Fields] OR EEG[All Fields] '
        'OR ERP[All Fields] OR fMRI[All Fields] OR "eye tracking"[All Fields] '
        'OR neuroimaging[All Fields])'
    ),
    "consumer-decision": (
        '(consumer[All Fields] OR purchase[All Fields] OR shopping[All Fields] '
        'OR retail[All Fields] OR customer[All Fields]) AND '
        '("decision making"[All Fields] OR attention[All Fields] OR emotion[All Fields] '
        'OR memory[All Fields] OR reward[All Fields] OR perception[All Fields]) AND '
        '(marketing[All Fields] OR advertising[All Fields] OR product[All Fields] '
        'OR price[All Fields] OR brand[All Fields])'
    ),
    "persuasion-psychology": (
        '(persuasion[All Fields] OR framing[All Fields] OR scarcity[All Fields] '
        'OR "social proof"[All Fields] OR trust[All Fields] OR influence[All Fields]) AND '
        '(marketing[All Fields] OR advertising[All Fields] OR consumer[All Fields] '
        'OR brand[All Fields]) AND (psychology[All Fields] OR cognitive[All Fields] '
        'OR behavioral[All Fields] OR behavioural[All Fields] OR neuroscience[All Fields])'
    ),
    "sensory-marketing": (
        '"sensory marketing"[All Fields] OR (olfactory[All Fields] AND consumer[All Fields]) '
        'OR (auditory[All Fields] AND brand[All Fields]) '
        'OR (visual[All Fields] AND packaging[All Fields]) '
        'OR (haptic[All Fields] AND product[All Fields]) '
        'OR (taste[All Fields] AND marketing[All Fields])'
    ),
    "pricing-value": (
        '(pricing[All Fields] OR price[All Fields] OR "willingness to pay"[All Fields] '
        'OR valuation[All Fields]) AND (consumer[All Fields] OR purchase[All Fields] '
        'OR marketing[All Fields]) AND (psychology[All Fields] OR brain[All Fields] '
        'OR reward[All Fields] OR decision[All Fields])'
    ),
}

LICENSE_FILTER = (
    '(cc0_license[filter] OR cc_by_license[filter] OR cc_by-sa_license[filter] '
    'OR cc_by-nd_license[filter]) AND open_access[filter] AND has_pdf[filter]'
)

MARKETING_TERMS = {
    "advertising", "brand", "branding", "consumer", "customer", "marketing",
    "neuromarketing", "packaging", "price", "pricing", "product", "purchase",
    "retail", "sales", "shopping", "willingness to pay",
}
SCIENCE_TERMS = {
    "attention", "behavior", "behaviour", "brain", "cognition", "cognitive",
    "decision", "eeg", "emotion", "erp", "eye tracking", "fmri", "memory",
    "neural", "neuro", "neuroscience", "perception", "psychology", "reward",
    "sensory",
}
STRONG_MECHANISM_TERMS = {
    "attention", "brain", "cognition", "cognitive", "eeg", "emotion", "erp",
    "eye tracking", "fmri", "memory", "neural", "neuro", "neuroscience",
    "perception", "psychology", "reward", "sensory",
}
ALGORITHM_TERMS = {
    "algorithm", "artificial intelligence", "deep learning", "knn", "machine learning",
    "natural language processing", "neural network", "optimization",
}
CORE_TITLE_TERMS = {
    "advertising", "attention", "behavior", "behaviour", "brain", "brand", "choice",
    "cognitive", "consumer", "customer", "eeg", "emotion", "erp", "eye tracking",
    "fmri", "marketing", "memory", "neural", "neuro", "packaging", "perception",
    "persuasion", "psychology", "purchase", "reward", "sensory", "shopping", "trust",
    "willingness to pay",
}

_rate_lock = threading.Lock()
_last_ncbi_request = 0.0


def ncbi_request(url: str, timeout: int = 60, attempts: int = 4) -> bytes:
    """Fetch an NCBI endpoint while respecting the unauthenticated rate limit."""
    global _last_ncbi_request
    for attempt in range(attempts):
        try:
            with _rate_lock:
                wait = 0.36 - (time.monotonic() - _last_ncbi_request)
                if wait > 0:
                    time.sleep(wait)
                _last_ncbi_request = time.monotonic()
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            if attempt == attempts - 1:
                raise RuntimeError(f"Request failed after {attempts} attempts: {url}") from exc
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def search_theme(theme: str, query: str, retmax: int) -> list[str]:
    term = f"({query}) AND {LICENSE_FILTER}"
    params = urllib.parse.urlencode(
        {
            "db": "pmc",
            "term": term,
            "retmode": "json",
            "retmax": retmax,
            "sort": "relevance",
            "tool": "neuro_marketing_skill",
        }
    )
    payload = json.loads(ncbi_request(f"{EUTILS}?{params}").decode("utf-8"))
    result = payload["esearchresult"]
    ids = [f"PMC{x}" for x in result.get("idlist", [])]
    print(f"SEARCH theme={theme} available={result.get('count', '0')} selected={len(ids)}", flush=True)
    return ids


def interleave_unique(groups: list[tuple[str, list[str]]]) -> list[tuple[str, str]]:
    output: list[tuple[str, str]] = []
    seen: set[str] = set()
    longest = max((len(ids) for _, ids in groups), default=0)
    for index in range(longest):
        for theme, ids in groups:
            if index < len(ids) and ids[index] not in seen:
                seen.add(ids[index])
                output.append((ids[index], theme))
    return output


def oa_record(pmcid: str) -> dict[str, str]:
    params = urllib.parse.urlencode({"id": pmcid})
    root = ET.fromstring(ncbi_request(f"{OA_API}?{params}"))
    record = root.find(".//record")
    if record is None:
        error = root.find(".//error")
        raise RuntimeError(error.text if error is not None else "OA record unavailable")
    license_name = (record.get("license") or "").upper().replace("CC-BY", "CC BY")
    if license_name not in ALLOWED_LICENSES:
        raise RuntimeError(f"license excluded: {license_name or 'unknown'}")
    if (record.get("retracted") or "no").lower() == "yes":
        raise RuntimeError("retracted article")
    link = record.find("./link[@format='tgz']")
    if link is None or not link.get("href"):
        raise RuntimeError("OA package link unavailable")
    href = link.get("href", "").replace("ftp://", "https://")
    # NLM moved legacy packages under /deprecated/ during the 2026 S3 transition.
    if "/pub/pmc/oa_package/" in href:
        href = href.replace("/pub/pmc/oa_package/", "/pub/pmc/deprecated/oa_package/")
    return {
        "package_url": href,
        "license": license_name,
        "citation": record.get("citation") or "",
        "updated": link.get("updated") or "",
    }


def download(url: str, attempts: int = 4) -> bytes:
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=120) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            if attempt == attempts - 1:
                raise RuntimeError(f"Package download failed: {url}") from exc
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def safe_members(archive: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members = []
    for member in archive.getmembers():
        name = member.name.replace("\\", "/")
        if name.startswith("/") or "../" in name or not member.isfile():
            continue
        if name.lower().endswith((".pdf", ".nxml")):
            members.append(member)
    return members


def choose_main_pdf(files: dict[str, bytes], nxml_name: str) -> tuple[str, bytes]:
    pdfs = [(name, data) for name, data in files.items() if name.lower().endswith(".pdf")]
    if not pdfs:
        raise RuntimeError("package has no PDF")
    xml_stem = Path(nxml_name).stem.lower()
    exact = [(name, data) for name, data in pdfs if Path(name).stem.lower() == xml_stem]
    choices = exact or [
        (name, data) for name, data in pdfs
        if not re.search(r"supp|append|additional|mmc|esm", Path(name).stem, re.I)
    ] or pdfs
    return max(choices, key=lambda item: len(item[1]))


def pdf_page_count(pdf_bytes: bytes) -> int:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "pypdf is required. Run with the Codex bundled Python runtime or install pypdf."
        ) from exc
    reader = PdfReader(io.BytesIO(pdf_bytes), strict=False)
    return len(reader.pages)


def node_text(node: ET.Element | None) -> str:
    if node is None:
        return ""
    text = " ".join("".join(node.itertext()).split())
    return html.unescape(text)


def first(root: ET.Element, path: str) -> str:
    return node_text(root.find(path))


def extract_article(nxml: bytes, pmcid: str, theme: str, oa: dict[str, str], pages: int) -> dict[str, Any]:
    root = ET.fromstring(nxml)
    title = first(root, ".//article-meta/title-group/article-title")
    abstract = node_text(root.find(".//article-meta/abstract"))
    body = node_text(root.find(".//body"))
    journal = first(root, ".//journal-meta/journal-title-group/journal-title")
    doi = ""
    pmid = ""
    for article_id in root.findall(".//article-meta/article-id"):
        kind = (article_id.get("pub-id-type") or "").lower()
        if kind == "doi":
            doi = node_text(article_id)
        elif kind == "pmid":
            pmid = node_text(article_id)
    year = first(root, ".//article-meta/pub-date/year")
    keywords = [node_text(x) for x in root.findall(".//article-meta/kwd-group/kwd")]
    authors = []
    for contributor in root.findall(".//article-meta/contrib-group/contrib[@contrib-type='author']"):
        surname = first(contributor, "./name/surname")
        given = first(contributor, "./name/given-names")
        collective = first(contributor, "./collab")
        name = " ".join(x for x in (given, surname) if x) or collective
        if name:
            authors.append(name)
    license_statement = node_text(root.find(".//article-meta/permissions"))
    return {
        "pmcid": pmcid,
        "pmid": pmid,
        "doi": doi,
        "title": title,
        "authors": authors,
        "year": year,
        "journal": journal,
        "theme": theme,
        "keywords": keywords,
        "abstract": abstract,
        "text": body,
        "page_count": pages,
        "license": oa["license"],
        "license_statement": license_statement,
        "citation": oa["citation"],
        "source_url": f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/",
        "package_url": oa["package_url"],
        "source_updated": oa["updated"],
        "harvested_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def relevance_score(article: dict[str, Any]) -> int:
    title = article["title"].lower()
    abstract = article["abstract"].lower()
    score = 0
    if "neuromarketing" in title or "consumer neuroscience" in title:
        score += 12
    for term in MARKETING_TERMS:
        if term in title:
            score += 3
        elif term in abstract:
            score += 1
    for term in SCIENCE_TERMS:
        if term in title:
            score += 2
        elif term in abstract:
            score += 1
    return score


def process_candidate(pmcid: str, theme: str, minimum_score: int) -> dict[str, Any]:
    oa = oa_record(pmcid)
    package = download(oa["package_url"])
    with tarfile.open(fileobj=io.BytesIO(package), mode="r:gz") as archive:
        extracted: dict[str, bytes] = {}
        for member in safe_members(archive):
            stream = archive.extractfile(member)
            if stream is not None:
                extracted[member.name] = stream.read()
    nxmls = [(name, data) for name, data in extracted.items() if name.lower().endswith(".nxml")]
    if not nxmls:
        raise RuntimeError("package has no NXML")
    nxml_name, nxml = max(nxmls, key=lambda item: len(item[1]))
    pdf_name, pdf = choose_main_pdf(extracted, nxml_name)
    pages = pdf_page_count(pdf)
    article = extract_article(nxml, pmcid, theme, oa, pages)
    article["pdf_filename"] = Path(pdf_name).name
    article["relevance_score"] = relevance_score(article)
    title_abstract = f"{article['title']} {article['abstract']}".lower()
    if not any(term in title_abstract for term in MARKETING_TERMS):
        raise RuntimeError("no marketing bridge in title or abstract")
    if not any(term in title_abstract for term in SCIENCE_TERMS):
        raise RuntimeError("no psychology/neuroscience bridge in title or abstract")
    title = article["title"].lower()
    if not any(term in title for term in CORE_TITLE_TERMS):
        raise RuntimeError("title lacks a consumer, marketing, psychological, or neural focus")
    if any(term in title for term in ALGORITHM_TERMS) and not any(
        term in title_abstract for term in STRONG_MECHANISM_TERMS
    ):
        raise RuntimeError("algorithmic marketing without a human mechanism")
    if article["relevance_score"] < minimum_score:
        raise RuntimeError(f"low relevance score: {article['relevance_score']}")
    if not article["title"] or not article["text"]:
        raise RuntimeError("missing title or full text")
    return article


def load_existing(catalog_path: Path) -> tuple[set[str], int, int]:
    if not catalog_path.exists():
        return set(), 0, 0
    seen: set[str] = set()
    pages = 0
    with catalog_path.open("r", encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            seen.add(row["pmcid"])
            pages += int(row["page_count"])
    return seen, len(seen), pages


def append_article(corpus_path: Path, catalog_path: Path, article: dict[str, Any]) -> None:
    corpus_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(corpus_path, "at", encoding="utf-8", compresslevel=9) as stream:
        stream.write(json.dumps(article, ensure_ascii=False, separators=(",", ":")) + "\n")
    new_file = not catalog_path.exists()
    fields = [
        "pmcid", "pmid", "doi", "title", "year", "journal", "theme", "page_count",
        "license", "relevance_score", "source_url", "package_url", "source_updated",
    ]
    with catalog_path.open("a", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        if new_file:
            writer.writeheader()
        writer.writerow(article)


def write_state(path: Path, **values: Any) -> None:
    payload = {**values, "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(temp, path)


def verify(corpus_path: Path, catalog_path: Path, target_pages: int) -> dict[str, Any]:
    rows = []
    with catalog_path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    pmcids = [row["pmcid"] for row in rows]
    pages = sum(int(row["page_count"]) for row in rows)
    licenses = sorted({row["license"] for row in rows})
    corpus_ids = []
    with gzip.open(corpus_path, "rt", encoding="utf-8") as stream:
        for line in stream:
            corpus_ids.append(json.loads(line)["pmcid"])
    problems = []
    if len(pmcids) != len(set(pmcids)):
        problems.append("duplicate PMCID in catalog")
    if pmcids != corpus_ids:
        problems.append("catalog/corpus order mismatch")
    if not set(licenses).issubset(ALLOWED_LICENSES):
        problems.append("disallowed license present")
    if pages < target_pages:
        problems.append(f"page target not met: {pages} < {target_pages}")
    return {
        "papers": len(rows),
        "pages": pages,
        "licenses": licenses,
        "compressed_bytes": corpus_path.stat().st_size,
        "target_pages": target_pages,
        "ok": not problems,
        "problems": problems,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-pages", type=int, default=10100)
    parser.add_argument("--per-theme", type=int, default=900)
    parser.add_argument("--max-candidates", type=int, default=5000)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--minimum-score", type=int, default=6)
    parser.add_argument(
        "--themes",
        nargs="+",
        choices=sorted(QUERY_THEMES),
        help="Limit harvesting to selected query themes",
    )
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--verify-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.verify_only:
        report = verify(args.corpus, args.catalog, args.target_pages)
        print(json.dumps(report, indent=2))
        return 0 if report["ok"] else 1

    seen, paper_count, page_count = load_existing(args.catalog)
    if page_count >= args.target_pages:
        print(json.dumps(verify(args.corpus, args.catalog, args.target_pages), indent=2))
        return 0

    selected_themes = args.themes or list(QUERY_THEMES)
    groups = [
        (theme, search_theme(theme, QUERY_THEMES[theme], args.per_theme))
        for theme in selected_themes
    ]
    candidates = [item for item in interleave_unique(groups) if item[0] not in seen]
    candidates = candidates[: args.max_candidates]
    print(
        f"START existing_papers={paper_count} existing_pages={page_count} "
        f"candidates={len(candidates)} target_pages={args.target_pages}",
        flush=True,
    )
    failures: dict[str, int] = {}
    stop = False
    iterator = iter(candidates)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = {}
        for _ in range(min(args.workers * 2, len(candidates))):
            pmcid, theme = next(iterator, (None, None))
            if pmcid is not None:
                pending[pool.submit(process_candidate, pmcid, theme, args.minimum_score)] = (pmcid, theme)
        while pending and not stop:
            future = next(as_completed(pending))
            pmcid, theme = pending.pop(future)
            try:
                article = future.result()
                if article["pmcid"] not in seen:
                    append_article(args.corpus, args.catalog, article)
                    seen.add(article["pmcid"])
                    paper_count += 1
                    page_count += int(article["page_count"])
                    print(
                        f"ACCEPT papers={paper_count} pages={page_count} +{article['page_count']} "
                        f"theme={theme} pmcid={pmcid} title={article['title'][:90]}",
                        flush=True,
                    )
            except Exception as exc:
                key = str(exc).split(":", 1)[0][:80]
                failures[key] = failures.get(key, 0) + 1
                print(f"SKIP pmcid={pmcid} reason={exc}", flush=True)
            write_state(
                args.state,
                target_pages=args.target_pages,
                papers=paper_count,
                pages=page_count,
                candidates_remaining=len(pending),
                failures=failures,
            )
            if page_count >= args.target_pages:
                stop = True
                for queued in pending:
                    queued.cancel()
                break
            next_pmcid, next_theme = next(iterator, (None, None))
            if next_pmcid is not None:
                pending[pool.submit(process_candidate, next_pmcid, next_theme, args.minimum_score)] = (
                    next_pmcid,
                    next_theme,
                )

    report = verify(args.corpus, args.catalog, args.target_pages)
    write_state(args.state, **report, failures=failures)
    print("VERIFY " + json.dumps(report, separators=(",", ":")), flush=True)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
