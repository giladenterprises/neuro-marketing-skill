#!/usr/bin/env python3
"""Generate a compact human-readable map of the compressed corpus."""

from __future__ import annotations

import csv
import gzip
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "catalog.csv"
CORPUS = ROOT / "references" / "corpus.jsonl.gz"
OUTPUT = ROOT / "references" / "evidence-map.md"
CATEGORIES = {
    "Attention and salience": ["attention", "salience", "visual search", "gaze", "eye tracking"],
    "Brand and advertising": ["brand", "branding", "advertising", "advertisement", "logo"],
    "Emotion and arousal": ["emotion", "emotional", "affect", "arousal", "valence"],
    "Memory and learning": ["memory", "recall", "recognition", "learning", "encoding"],
    "Value, price, and reward": ["price", "pricing", "willingness to pay", "reward", "valuation"],
    "Persuasion and social influence": ["persuasion", "social influence", "trust", "scarcity", "framing"],
    "Sensory and packaging": ["sensory", "packaging", "olfactory", "haptic", "taste", "auditory"],
    "EEG and ERP": ["eeg", "event-related potential", "erp"],
    "fMRI and neuroimaging": ["fmri", "neuroimaging", "functional magnetic resonance"],
    "Consumer choice": ["consumer choice", "purchase", "decision making", "shopping", "customer"],
}


def main() -> int:
    with CATALOG.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    records = []
    with gzip.open(CORPUS, "rt", encoding="utf-8") as stream:
        for line in stream:
            records.append(json.loads(line))
    pages = sum(int(row["page_count"]) for row in rows)
    themes = Counter(row["theme"] for row in rows)
    licenses = Counter(row["license"] for row in rows)
    journal_names = {}
    journals = Counter()
    for row in rows:
        if row["journal"]:
            key = row["journal"].casefold()
            journal_names.setdefault(key, row["journal"])
            journals[key] += 1
    years = Counter(row["year"] for row in rows if row["year"])
    category_counts = Counter()
    for record in records:
        haystack = " ".join(
            [record.get("title", ""), record.get("abstract", ""), " ".join(record.get("keywords", []))]
        ).lower()
        for category, terms in CATEGORIES.items():
            if any(term in haystack for term in terms):
                category_counts[category] += 1
    lines = [
        "# Corpus evidence map",
        "",
        f"Verified scale: **{len(rows):,} papers and {pages:,} main-article PDF pages**.",
        f"Compressed full-text size: **{CORPUS.stat().st_size / 1024 / 1024:.1f} MiB**.",
        "",
        "Source: PubMed Central Open Access Subset. Retrieval uses NCBI-approved automated services and retains only commercial-use Creative Commons records that were not marked retracted at harvest time.",
        "",
        "## Search themes",
        "",
    ]
    lines.extend(f"- {name}: {count:,} papers" for name, count in themes.most_common())
    lines.extend(["", "## Topical coverage", ""])
    lines.extend(f"- {name}: {count:,} papers" for name, count in category_counts.most_common())
    lines.extend(["", "## Licenses", ""])
    lines.extend(
        f"- {name}: {count:,} {'paper' if count == 1 else 'papers'}"
        for name, count in licenses.most_common()
    )
    lines.extend(["", "## Most represented journals", ""])
    lines.extend(f"- {journal_names[key]}: {count:,}" for key, count in journals.most_common(15))
    if years:
        lines.extend([
            "", "## Publication range", "",
            f"Earliest recorded year: {min(years)}. Latest recorded year: {max(years)}.",
        ])
    lines.extend([
        "", "## Retrieval", "",
        "Use `python scripts/search_corpus.py \"query terms\" --top 12` from the skill directory.",
        "Use multiple mechanism-specific searches and assess the full study design before drawing consequential conclusions.",
        "",
    ])
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(rows)} papers, {pages} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
