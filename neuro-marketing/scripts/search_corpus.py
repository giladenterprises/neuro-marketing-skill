#!/usr/bin/env python3
"""Search the compressed Neuro Marketing research corpus without external services."""

from __future__ import annotations

import argparse
import gzip
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


CORPUS = Path(__file__).resolve().parents[1] / "references" / "corpus.jsonl.gz"
TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?", re.I)
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was",
    "what", "when", "which", "with",
}


def tokenize(value: str) -> list[str]:
    return [x.lower() for x in TOKEN_RE.findall(value) if x.lower() not in STOPWORDS and len(x) > 1]


def load_records(path: Path) -> list[dict[str, Any]]:
    records = []
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                records.append(json.loads(line))
    return records


def score_records(records: list[dict[str, Any]], query: str, theme: str | None) -> list[tuple[float, dict[str, Any]]]:
    query_tokens = tokenize(query)
    if not query_tokens:
        raise ValueError("Query has no searchable terms")
    docs = []
    doc_frequency: Counter[str] = Counter()
    for record in records:
        if theme and record.get("theme") != theme:
            continue
        title_tokens = tokenize(record.get("title", ""))
        abstract_tokens = tokenize(record.get("abstract", ""))
        keyword_tokens = tokenize(" ".join(record.get("keywords", [])))
        text_tokens = tokenize(record.get("text", ""))
        counts = Counter(text_tokens)
        weighted = Counter(counts)
        weighted.update({token: count * 8 for token, count in Counter(title_tokens).items()})
        weighted.update({token: count * 4 for token, count in Counter(abstract_tokens).items()})
        weighted.update({token: count * 5 for token, count in Counter(keyword_tokens).items()})
        docs.append((record, weighted, len(text_tokens) + 1))
        doc_frequency.update(set(weighted))
    total_docs = max(len(docs), 1)
    average_length = sum(length for _, _, length in docs) / total_docs
    scored = []
    lowered_query = query.lower().strip()
    for record, counts, doc_length in docs:
        score = 0.0
        for token in query_tokens:
            frequency = counts[token]
            if not frequency:
                continue
            inverse = math.log(1 + (total_docs - doc_frequency[token] + 0.5) / (doc_frequency[token] + 0.5))
            denominator = frequency + 1.2 * (0.25 + 0.75 * doc_length / average_length)
            score += inverse * frequency * 2.2 / denominator
        title = record.get("title", "").lower()
        abstract = record.get("abstract", "").lower()
        if lowered_query in title:
            score += 6
        elif lowered_query in abstract:
            score += 3
        coverage = sum(1 for token in set(query_tokens) if counts[token]) / len(set(query_tokens))
        score += coverage * 3
        if score > 0:
            scored.append((score, record))
    return sorted(scored, key=lambda item: (-item[0], -int(item[1].get("relevance_score", 0))))


def evidence_snippet(record: dict[str, Any], query: str, width: int = 420) -> str:
    text = record.get("abstract") or record.get("text") or ""
    terms = tokenize(query)
    lower = text.lower()
    positions = [lower.find(term) for term in terms if lower.find(term) >= 0]
    center = min(positions) if positions else 0
    start = max(0, center - width // 3)
    end = min(len(text), start + width)
    snippet = " ".join(text[start:end].split())
    if start:
        snippet = "..." + snippet
    if end < len(text):
        snippet += "..."
    return snippet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", help="Concepts or mechanisms to search")
    parser.add_argument("--pmcid", type=str.upper, help="Retrieve one exact PMC article")
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument("--theme", choices=[
        "consumer-neuroscience", "brand-ad-neuro", "consumer-decision",
        "persuasion-psychology", "sensory-marketing", "pricing-value",
    ])
    parser.add_argument("--corpus", type=Path, default=CORPUS)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--full-text", action="store_true")
    args = parser.parse_args()
    if (args.query is None) == (args.pmcid is None):
        parser.error("provide a query or --pmcid")
    if args.pmcid is not None:
        if not re.fullmatch(r"PMC[0-9]+", args.pmcid):
            parser.error("--pmcid must be a PMC article identifier, e.g. PMC1234567")
        if args.theme:
            parser.error("--theme applies only to query searches")
    elif not tokenize(args.query):
        parser.error("query has no searchable terms")
    if args.top < 0:
        parser.error("--top must be nonnegative")
    return args


def print_article(record: dict[str, Any], args: argparse.Namespace) -> None:
    if args.as_json:
        item = dict(record)
        if not args.full_text:
            item.pop("text", None)
        print(json.dumps([item], ensure_ascii=False, indent=2))
        return

    print(f"{record['title']} | {record['pmcid']}")
    if record.get("doi"):
        print(f"doi:{record['doi']}")
    print(record["source_url"])
    print(record.get("text", "") if args.full_text else record.get("abstract", ""))


def main() -> int:
    args = parse_args()
    if not args.corpus.exists():
        print(f"Corpus not found: {args.corpus}", file=sys.stderr)
        return 2
    records = load_records(args.corpus)
    if args.pmcid:
        record = next((item for item in records if item.get("pmcid") == args.pmcid), None)
        if record is None:
            print(f"Article not found: {args.pmcid}", file=sys.stderr)
            return 2
        print_article(record, args)
        return 0

    ranked = score_records(records, args.query, args.theme)[: args.top]
    if args.as_json:
        output = []
        for score, record in ranked:
            item = dict(record)
            item["search_score"] = round(score, 4)
            if not args.full_text:
                item.pop("text", None)
                item["evidence_snippet"] = evidence_snippet(record, args.query)
            output.append(item)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    print(f"Query: {args.query} | records: {len(records)} | matches: {len(ranked)}")
    for index, (score, record) in enumerate(ranked, 1):
        authors = ", ".join(record.get("authors", [])[:3])
        if len(record.get("authors", [])) > 3:
            authors += " et al."
        identifier = f"doi:{record['doi']}" if record.get("doi") else record["pmcid"]
        print(f"\n{index}. {record['title']} ({record.get('year') or 'n.d.'})")
        print(
            f"   {authors} | {record.get('journal', '')} | {record['theme']} | "
            f"{record['page_count']} pp | {record['license']} | score {score:.2f}"
        )
        print(f"   {identifier} | {record['source_url']}")
        print(record.get("text", "") if args.full_text else f"   {evidence_snippet(record, args.query)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
