---
name: neuro-marketing
description: Evidence-led neuromarketing, consumer neuroscience, marketing psychology, behavioral science, branding, advertising, pricing, persuasion, sensory marketing, attention, emotion, memory, reward, and customer decision analysis. Use when Codex must explain why marketing works, critique or design a brand/campaign/product/packaging/pricing experience, turn behavioral and neural research into ethical recommendations, or distinguish supported consumer-science claims from neuromarketing hype.
---

# Neuro Marketing

Ground marketing and branding decisions in the bundled open-access research corpus. Treat neural measures as evidence about mechanisms, not as a magical purchase detector.

## Evidence workflow

1. Translate the request into a consumer behavior, mechanism, context, and business outcome.
2. Read `references/methodology.md` before making scientific or commercial claims.
3. Search the corpus with 2-4 focused formulations rather than one broad query:

```powershell
python scripts/search_corpus.py "brand familiarity memory attention" --top 12
python scripts/search_corpus.py "price framing willingness to pay reward" --theme pricing-value --top 12
python scripts/search_corpus.py "packaging visual attention eye tracking" --theme sensory-marketing --top 12 --json
```

4. Triangulate important claims across at least three relevant papers when the corpus permits. Prefer reviews, meta-analyses, preregistered experiments, field studies, and adequately powered replications over a single small laboratory study.
5. Separate findings into established or convergent evidence, promising but context-bound evidence, and speculation or evidence gaps.
6. Convert evidence into a testable recommendation. State the intended mechanism, audience, context, expected observable outcome, and the cheapest valid experiment.
7. Cite DOI or PMCID beside each material claim. Link to the `source_url` returned by the search script.

## Diagnose the right layer

- **Attention:** salience, visual hierarchy, orienting, gaze, novelty, processing fluency.
- **Emotion:** valence, arousal, affective forecasting, empathy, avoidance, attachment.
- **Memory:** encoding, retrieval cues, distinctiveness, repetition, narrative, associative networks.
- **Value and choice:** reward, willingness to pay, reference points, framing, loss aversion, delay.
- **Brand:** familiarity, identity, trust, meaning, loyalty, social signaling, category cues.
- **Sensory experience:** color, sound, touch, scent, taste, packaging, crossmodal correspondence.
- **Persuasion:** credibility, social influence, norms, scarcity, defaults, reactance, disclosure.
- **Measurement:** behavioral outcomes first; then eye tracking, psychophysiology, EEG/ERP, fMRI, or implicit measures only when they answer a defined question.

## Apply scientific discipline

- Do not equate brain activation with preference, intent, or causality.
- Do not reverse-infer a mental state from one region or signal without converging evidence.
- Distinguish statistical significance from practical lift and out-of-sample prediction.
- Check sample size, controls, multiple comparisons, ecological validity, population, product category, and whether the outcome was observed behavior or self-report.
- Treat EEG, fMRI, biometrics, facial coding, and eye tracking as complementary measurements with different temporal, spatial, and interpretive limits.
- Never invent effect sizes. If the paper extract does not provide one, say so.
- Distinguish correlation, mediation, prediction, and causal intervention explicitly.
- Treat abstracts as orientation; use the bundled full text for consequential claims.

## Produce useful outputs

For a campaign, brand, page, package, price, or product critique, return:

1. the consumer problem and desired behavior;
2. the most likely mechanisms;
3. research-backed design recommendations, ranked by evidence and expected impact;
4. risks, boundary conditions, and ethical concerns;
5. a measurement plan with behavioral primary metrics and optional neural/biometric diagnostics;
6. citations and unresolved questions.

For research synthesis, include the search terms used, evidence-selection logic, recurring findings, disagreements, methodological weaknesses, and a calibrated conclusion.

## Ethical boundary

Reject dark patterns, covert exploitation, deceptive scarcity, vulnerable-person targeting, non-consensual biometric collection, and claims that a technique can bypass free choice. Favor transparency, informed consent, accessibility, consumer welfare, and reversible experimentation.

## Corpus resources

- `references/evidence-map.md`: corpus scale, coverage, themes, licenses, and retrieval notes.
- `references/catalog.csv`: one row per paper with provenance and exact PDF page count.
- `references/corpus.jsonl.gz`: compressed full-text records. Access it through `scripts/search_corpus.py` rather than loading it whole.
- `references/excluded-records.json`: auditable false-positive removals and reasons.
- `scripts/harvest_pmc.py`: resumable licensed-corpus builder and verifier.

When the installed corpus lacks the needed context, browse for current primary research, favor open-access sources, and keep new findings separate from bundled evidence unless the user asks to refresh the corpus.
