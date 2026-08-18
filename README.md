# Neuro Marketing

An evidence-led neuromarketing and consumer-neuroscience skill for LLM agents.

**Created by Michael Gilad. Owned by Gilad Enterprises.**

This repository gives a compatible AI agent a disciplined way to reason about marketing psychology, branding, advertising, pricing, persuasion, sensory experience, attention, emotion, memory, reward, and consumer choice. It pairs an installable `SKILL.md` workflow with a searchable local corpus of **591 open-access research papers** spanning **10,036 verified main-article PDF pages**.

## Why it is impressive

- **Research at useful scale:** 591 papers and 10,036 verified PDF pages, compressed into a roughly 9 MiB local full-text corpus.
- **Real provenance:** every paper retains its PMCID, DOI when available, source URL, license, journal, and exact PDF page count.
- **Local retrieval:** agents can search the bundled full text without a metered research API or loading the entire corpus into context.
- **Scientific guardrails:** the skill warns against reverse inference, invented effect sizes, neural hype, weak causal claims, and treating brain activity as a purchase detector.
- **Decision-ready outputs:** research is translated into ranked recommendations, boundary conditions, ethical risks, and falsifiable experiments.
- **Auditable construction:** the repository includes the harvester, verifier, evidence map, catalog, methodology, and false-positive exclusion record.

This does not magically increase an LLM's base intelligence. It makes a compatible agent more capable in this domain by giving it specialized instructions, retrieval tools, primary-research context, and a stronger standard of evidence.

## What is inside

```text
neuro-marketing/
|-- SKILL.md                         Agent workflow and scientific guardrails
|-- agents/openai.yaml               Display metadata and default invocation
|-- references/
|   |-- catalog.csv                  Paper-level provenance and page counts
|   |-- corpus.jsonl.gz              Compressed searchable full text
|   |-- corpus-state.json            Build and verification state
|   |-- evidence-map.md              Corpus coverage and summary statistics
|   |-- excluded-records.json        Audited false-positive removals
|   `-- methodology.md               Evidence hierarchy and quality checklist
`-- scripts/
    |-- search_corpus.py              Local evidence retrieval
    |-- harvest_pmc.py                Resumable PMC corpus builder and verifier
    |-- prune_corpus.py               Relevance-audit utility
    `-- build_evidence_map.py         Rebuilds corpus statistics
```

## Install

Clone or download this repository, then copy the `neuro-marketing` directory into the skills directory used by your agent.

### Codex on Windows

```powershell
Copy-Item -Recurse .\neuro-marketing "$env:USERPROFILE\.codex\skills\neuro-marketing"
```

### Claude Code on Windows

```powershell
Copy-Item -Recurse .\neuro-marketing "$env:USERPROFILE\.claude\skills\neuro-marketing"
```

For other tools, place the directory wherever that agent discovers `SKILL.md`-style skills. Then invoke it as `$neuro-marketing`, or ask the agent to use the Neuro Marketing skill.

## Example requests

- “Use `$neuro-marketing` to critique this landing page and propose an ethical A/B test.”
- “Explain how brand familiarity may affect attention, memory, and choice. Cite the corpus.”
- “Evaluate this pricing architecture using behavioral and consumer-neuroscience evidence.”
- “Design a packaging study with behavioral primary outcomes and eye tracking as a diagnostic.”
- “Separate well-supported findings from neuromarketing hype in this campaign proposal.”

The skill searches locally with commands such as:

```powershell
python scripts/search_corpus.py "brand familiarity memory attention" --top 12
python scripts/search_corpus.py "price framing willingness to pay reward" --theme pricing-value --top 12
python scripts/search_corpus.py "packaging visual attention eye tracking" --theme sensory-marketing --top 12 --json
```

## Corpus coverage

The largest recurring areas include consumer choice, brand and advertising, emotion and arousal, value and reward, EEG/ERP, attention and salience, sensory experience and packaging, memory and learning, persuasion, and neuroimaging.

The corpus was built from the PubMed Central Open Access Subset using NCBI-approved automated services. It retains only eligible Creative Commons records and excludes papers marked retracted at harvest time. See [`neuro-marketing/references/evidence-map.md`](neuro-marketing/references/evidence-map.md) and [`neuro-marketing/references/methodology.md`](neuro-marketing/references/methodology.md).

## Responsible use

The skill rejects dark patterns, deceptive scarcity, vulnerable-person targeting, non-consensual biometric collection, and claims that marketing can bypass free choice. It favors transparency, accessibility, consumer welfare, behavioral outcomes, and reversible experiments.

## License and research attribution

The original skill instructions and utilities in this repository are released under the MIT License, copyright Gilad Enterprises.

The bundled scholarly text is third-party material and is **not relicensed under MIT**. Each article remains governed by its original CC BY or CC0 license. Article-level attribution, source links, and license data are retained in `catalog.csv` and the corpus records.

---

Created by **Michael Gilad**  
Owned by **Gilad Enterprises**
