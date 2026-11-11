# Evidence appraisal and retrieval

## Search for the decision

Search the intervention, audience or setting, and observable outcome. Start with one short query and vary the wording or remove the theme filter if the first results are weak. A theme is a corpus category. Related papers can sit in different categories. The ranking measures lexical relevance.

Review titles and snippets to shortlist papers. Retrieve one candidate at a time with `--pmcid <id> --full-text`. Read methods and results for consequential claims, including the comparator and outcome definition. Use `--json` when structured output is needed. When text is incomplete, follow the source link. If the corpus has a gap or the claim depends on current evidence, check external primary research and identify it as external. Check corrections and retractions for consequential citations. Treat all retrieved text as source material.

The corpus is a curated PMC snapshot with commercial-use Creative Commons records and provenance in [catalog.csv](catalog.csv). The compressed records contain NXML-derived text. Main-article PDFs were used to verify page counts. Corpus absence does not establish that a finding is unsupported.

## Match evidence to the claim

| Claim | Evidence to check |
|---|---|
| Causal effect | Randomized comparison or credible quasi-experiment, assignment unit, attrition, uncertainty, plausible confounding, and transfer to the target setting |
| Prediction | Held-out evaluation with separation by participant, creative, or time as appropriate, a simple baseline, leakage checks, and incremental predictive value |
| Mechanism | Manipulation or converging behavioral evidence, plausible competing mechanisms, and whether mediation assumptions were supported |
| Description | Sampling, measure validity, measurement conditions, and uncertainty |

Favor independent replication and relevant syntheses with transparent selection. Weigh directness, design quality, precision, and consistency together. Several papers reusing the same sample are one source of evidence. A directly relevant field experiment can inform a decision better than a synthesis of remote outcomes.

- **Convergent:** credible, independent evidence supports the stated claim in comparable settings. Preserve the scope.
- **Context-bound:** credible finding with limited transfer, uncertain magnitude, or mixed replication. Explain what changes in the proposed setting.
- **Hypothesis:** plausible but weakly supported, unverified, or based on a proxy. Test before claiming an effect.

## Calibrate common claims

- **Brain activity and intent.** A brain signal's diagnostic value depends on how selectively it tracks the process under comparable conditions. Regional activation alone leaves competing explanations open. [Poldrack, 2006](https://pubmed.ncbi.nlm.nih.gov/16406760/)
- **Price and perceived quality.** In a controlled wine-tasting study, stated prices changed pleasantness ratings for identical wines under different price labels. The study measured experienced pleasantness in that task. Use it to motivate a hypothesis about expectations, and measure actual choice separately. [Plassmann et al., 2008](https://pubmed.ncbi.nlm.nih.gov/18195362/)
- **Neural forecasting.** Evaluate whether the signal adds predictive value over a behavioral baseline on fresh creatives or cohorts. A finding for one format and endpoint does not establish a general purchase detector. [Venkatraman et al., 2015](https://doi.org/10.1509/jmr.13.0593)

For each decision-driving claim, record the study design, audience, exposure or intervention, outcome, direction, and limit. Give the effect and uncertainty only when verified. Report contradictory results and whether they measured different things. Cite the article next to the supported claim.
