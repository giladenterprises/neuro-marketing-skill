#!/usr/bin/env python3
"""Remove audited false positives and rebuild the corpus/catalog atomically."""

from __future__ import annotations

import csv
import gzip
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "references" / "corpus.jsonl.gz"
CATALOG = ROOT / "references" / "catalog.csv"
AUDIT = ROOT / "references" / "excluded-records.json"
EXCLUSIONS = {
    "PMC13020826": "platform operations model rather than consumer mechanism research",
    "PMC5559086": "clinical drug-market regulation rather than marketing psychology",
    "PMC12539743": "inventory and reinforcement-learning operations model",
    "PMC9847980": "retailer-led supply-chain game model",
    "PMC9388237": "KNN targeting algorithm without consumer mechanism evidence",
    "PMC8956418": "price-discrimination operations game",
    "PMC11299829": "supply-chain differential game",
    "PMC13033737": "emissions-costing policy model rather than consumer research",
    "PMC4748126": "antimalarial market-price surveillance",
    "PMC9070910": "retail inventory operations model",
    "PMC13004530": "inventory preservation operations model",
    "PMC5615627": "production and pricing operations model",
    "PMC6667132": "clinical drug price review",
    "PMC7349401": "hospital pricing and quality analysis",
    "PMC10442351": "supply-chain operations model",
    "PMC7038382": "price-competition operations model",
    "PMC9603462": "dual-channel supply-chain pricing game",
    "PMC9992377": "generic emotion-recognition algorithm without marketing application",
    "PMC5995966": "generic spiking-network architecture without marketing application",
    "PMC3893564": "organizational research-process paper",
    "PMC5001212": "general computational-neuroscience conference proceedings",
    "PMC11168648": "cooperative-advertising supply-chain optimization",
    "PMC8718387": "competitive supply-chain optimization",
    "PMC6696156": "low-carbon supply-chain complexity model",
    "PMC6603963": "closed-loop supply-chain price game",
    "PMC8910743": "supply-chain contract model",
    "PMC10414650": "remanufacturing supply-chain network model",
    "PMC7402509": "sustainable supply-chain pricing model",
    "PMC11086857": "discount-pricing platform operations model",
    "PMC10977684": "presale-channel operations model",
    "PMC10541849": "price-search competition model without a consumer mechanism test",
}


def main() -> int:
    records = []
    with gzip.open(CORPUS, "rt", encoding="utf-8") as stream:
        records = [json.loads(line) for line in stream if line.strip()]
    removed = [record for record in records if record["pmcid"] in EXCLUSIONS]
    kept = [record for record in records if record["pmcid"] not in EXCLUSIONS]
    prior_records = []
    if AUDIT.exists():
        prior_records = json.loads(AUDIT.read_text(encoding="utf-8")).get("records", [])
    prior_ids = {record["pmcid"] for record in prior_records}
    missing = sorted(set(EXCLUSIONS) - {record["pmcid"] for record in removed} - prior_ids)
    if missing:
        raise RuntimeError(f"Expected exclusions are missing from corpus: {missing}")

    corpus_temp = CORPUS.with_suffix(CORPUS.suffix + ".tmp")
    with gzip.open(corpus_temp, "wt", encoding="utf-8", compresslevel=9) as stream:
        for record in kept:
            stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    fields = [
        "pmcid", "pmid", "doi", "title", "year", "journal", "theme", "page_count",
        "license", "relevance_score", "source_url", "package_url", "source_updated",
    ]
    catalog_temp = CATALOG.with_suffix(CATALOG.suffix + ".tmp")
    with catalog_temp.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(kept)

    new_audit_records = [
        {
            "pmcid": record["pmcid"],
            "title": record["title"],
            "page_count": record["page_count"],
            "reason": EXCLUSIONS[record["pmcid"]],
        }
        for record in removed
    ]
    all_audit_records = prior_records + [
        record for record in new_audit_records if record["pmcid"] not in prior_ids
    ]
    audit = {
        "removed_papers": len(all_audit_records),
        "removed_pages": sum(int(record["page_count"]) for record in all_audit_records),
        "remaining_papers": len(kept),
        "remaining_pages": sum(int(record["page_count"]) for record in kept),
        "records": all_audit_records,
    }
    audit_temp = AUDIT.with_suffix(AUDIT.suffix + ".tmp")
    audit_temp.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    os.replace(corpus_temp, CORPUS)
    os.replace(catalog_temp, CATALOG)
    os.replace(audit_temp, AUDIT)
    print(json.dumps({key: value for key, value in audit.items() if key != "records"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
