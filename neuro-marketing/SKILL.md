---
name: neuro-marketing
description: Evidence-led neuromarketing, consumer neuroscience, and marketing psychology. Use to diagnose or design branding, ads, landing pages, pricing, packaging, sensory experiences, and customer journeys, or to assess persuasion claims, behavioral experiments, and biometric evidence.
---

# Neuro Marketing

## Start with the decision

Identify the audience, setting, current friction, desired voluntary behavior, and observable outcome. Use available data and state assumptions. Ask only when the missing answer would change the recommendation materially.

- **Critique or design:** inspect the actual asset when available. Locate the step where behavior breaks down and propose a concrete change.
- **Claim or research synthesis:** read [methodology](references/methodology.md). Frame the question around a population, intervention or exposure, comparison, and outcome. Report search scope, evidence selection, disagreements, and limits.
- **Experiment or measurement:** read [experiment design](references/experiments.md) for tests, decision rules, and biometric diagnostics. Use [worked examples](references/examples.md) for cross-channel applications.

## Diagnose and prioritize

Pick the smallest plausible mechanism and name a competing explanation. Check attention and comprehension before emotion or preference, then consider memory, trust, identity, sensory fit, value, and choice friction as relevant. Check mundane causes such as price, availability, accessibility, and audience mismatch before proposing a neural explanation.

For each ranked recommendation, connect **change → plausible mechanism → observable behavior → test**. Rank by directness of evidence, expected practical value, effort, and downside. Deliver usable copy, design changes, or a protocol when requested.

## Verify material claims

Use [methodology](references/methodology.md) for scientific claims that drive a decision. Search narrowly and inspect the strongest relevant full text before citing. The [evidence map](references/evidence-map.md) describes corpus scope.

```text
python scripts/search_corpus.py "packaging label search accuracy" --top 5
python scripts/search_corpus.py --pmcid PMC1234567 --full-text
```

Run from the skill directory or pass the script's absolute path. Replace the example PMCID with one from search. Use web research or user-supplied sources if shell, corpus, or relevant evidence is unavailable. With no verifiable sources, label mechanisms as hypotheses and offer a way to test them.

Separate convergent evidence, context-bound findings, and hypotheses. Match each citation to the population, comparison, and measured outcome. Give a source link and DOI or PMCID when available. Distinguish association, prediction, and causation. Gaze, arousal, and neural activity alone cannot establish intent, emotion, or purchase. Never invent citations, effects, or lift.

## Measure behavior and protect autonomy

Propose the cheapest credible comparison with a behavioral primary outcome, a decision threshold, and guardrails for harm. Keep competing exposures comparable across variants, such as shelf position or ad placement. Use self-report and biometric signals as diagnostics where they answer a specific question. Report uncertainty and missing inputs.

Keep prices, terms, sponsorship, and choices clear. Preserve accessible paths and meaningful refusal or exit. Decline deception, coercion, exploitation of vulnerability, and biometric collection without informed consent. Offer a transparent design that serves the same legitimate objective.
