# Experiments and measurement

## Choose the lightest valid design

- **Find the problem:** use task observation, accessible usability sessions, interviews, or funnel analysis to diagnose friction. Use the findings to generate hypotheses.
- **Estimate lift:** randomize eligible units to current experience and a clearly defined variant. Randomize at account, store, or market level where exposure spills over. Predefine the analysis unit and account for clustering. If randomization is unavailable, state the comparison assumptions and competing explanations.
- **Forecast:** use representative held-out outcomes, split at the deployment unit, and compare against simple behavioral or historical baselines.

## Write the decision rule before launch

1. Define the eligible population, exposure, primary behavior, denominator, and measurement window. Examples include completed qualified purchases per eligible visitor and correct shelf identification per task.
2. Set a minimum worthwhile change and maximum tolerable harm from business and consumer costs. Use baseline, traffic, variance, and allocation to plan the sample and duration. If those inputs are missing, ask for them or propose a pilot. Avoid estimating a sample or promising lift from thin air.
3. Predefine guardrails such as accessibility, comprehension, refunds, complaints, opt-outs, or retention. Verify instrumentation and assignment balance. Investigate unexplained imbalance before interpreting results. Use a fixed horizon or a valid sequential design. [Fabijan et al., 2019](https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/)
4. Report absolute changes and uncertainty, alongside relevant guardrails. Ship if the prespecified evidence and guardrails justify it. Iterate or keep the control if results are inconclusive. Roll back if a guardrail crosses its limit.

## Use diagnostics only when they can change the decision

| Measure | Question it can inform | Interpretation limit |
|---|---|---|
| Task completion, errors, recall | Was the intended action possible or the message retrievable? | The test setting and recall interval matter |
| Self-report | What did people report understanding or feeling? | Demand effects and intent–behavior gaps |
| Eye tracking | Where and when did participants look? | Fixation does not establish comprehension or preference |
| Electrodermal activity | When did physiological arousal vary? | Arousal does not identify emotional valence |
| EEG/ERP or fMRI | Did a predefined signal vary under a controlled contrast? | Artifacts and alternative processes can explain changes |

Specify the comparison, consent, data minimization, and retention before collecting sensitive measures. For each variant check understandable terms and exits, keyboard access, visible focus, legibility, and access to equivalent information without relying on color or motion. Check the applicable criteria in [WCAG 2.2](https://www.w3.org/TR/WCAG22/).
