# Scientific Idea Generation with Grounded Novelty — Research Report

## 1. Executive Summary

**Research question (one sentence).** Do LLMs generate higher-quality scientific ideas when the
abstract notion of *novelty* is **grounded** — through deduction, induction, proposal writing,
outcome imagination, small experiments, or literature comparison — versus unguided generation,
holding the backbone model, seed topic, and output format fixed?

**Key finding (one sentence).** Grounding does **not** uniformly improve idea quality; instead each
mechanism **steers the novelty–feasibility trade-off in a specific, metric-dependent way**, and the
apparent novelty gains exist almost entirely in the *LLM judge's* eye — they vanish under an
objective, literature-anchored novelty measure with which judge novelty is **completely
uncorrelated** (Spearman ρ = 0.01).

We ran the first controlled head-to-head ablation of the user's six grounding mechanisms plus an
unguided control: one fixed backbone (`gpt-4.1`), the canonical 7 NLP ideation topics from Si et al.
(2024), an identical output schema across all conditions, and N = 5 replicates per cell (**245
ideas**). We evaluated with three independent lenses: an *objective* embedding metric (distance to
real prior-work abstracts), a 2-judge off-family LLM rubric (Claude-Sonnet-4.5 + Gemini-2.5-Flash),
and position-controlled pairwise comparisons against the control. The three lenses **disagree in a
revealing way**, which is itself the headline result and a concrete confirmation of the "novelty
mirage" warned about in the recent literature.

**Practical implication.** Treat single-number LLM-judged "novelty" of generated ideas with
skepticism. If you want ideas that are *judged* exciting and win head-to-head, use **literature
comparison** or **deduction (Bit→Flip→Spark)** grounding — but expect a feasibility cost and *no*
increase in genuine distance from prior work. Falsification-style "small experiment" grounding
actively **hurts** novelty by pulling ideas toward already-published, safe techniques.

---

## 2. Research Question & Motivation

LLM ideation is good enough that AI ideas were judged *more novel than expert humans* in a 100+
researcher study (Si et al., 2024), yet the field still distrusts them because "novelty" is
ill-defined: unguided LLMs oscillate between incremental rephrasings and implausible over-reaches.
The user's hypothesis is that **grounding** the notion of novelty — anchoring it in a concrete
reasoning process — moves ideas toward the novel-and-plausible sweet spot.

**Gap filled.** Every strong prior system champions *one* grounding mechanism on *its own* dataset
and metric (SciMON/CoI/Nova → literature comparison; MOOSE/causal-graph → induction; HypoGen →
deduction; Si-agent/VirSci → proposal writing; AutoDiscovery → outcome imagination; Deep-Ideation →
critic/small-experiment feedback). **No paper compares the six under one controlled protocol.** Two
evaluation-skeptic papers — *All That Glitters Is Not Novel* (2025) and the *novelty-mirage*
RQ-Bench study (2026) — further argue the *evaluation* must be grounded, not a single LLM's opinion.
This report supplies both: the controlled ablation **and** a grounded-evaluation cross-check.

---

## 3. Experimental Setup

- **Backbone generator (fixed across all conditions):** `gpt-4.1`, temperature 0.8, top_p 1.0,
  per-cell deterministic seed, max 1600 tokens.
- **Conditions (7):** `unguided` (control) + `deduction` (Bit→Flip→Spark), `induction`
  (observations→hypothesis), `proposal_writing` (mini-proposal→distilled idea), `outcome_imagination`
  (imagine best plausible result / belief-shift, then back out the idea), `literature_comparison`
  (retrieve 8 real prior papers, contrast, revise to be distinct), `small_experiment` (design a
  falsification test, predict its result, self-critique, revise).
- **Critical control:** every condition emits the *identical* idea JSON
  (`title, problem, motivation, method, experiment_plan`). Only the reasoning *scaffold* differs.
  Mean idea length is balanced (199–236 words), and all effects are **robust to a length covariate**
  (p-values essentially unchanged), so results are not a length/format artifact (the Si "AI ideas
  are longer" confound is eliminated by design).
- **Topics (7):** Bias, Coding, Safety, Multilingual, Factuality, Math, Uncertainty (Si et al. 2024
  topic set), phrased as identical standardized seeds.
- **Design:** 7 conditions × 7 topics × 5 replicates = **245 ideas**.
- **Judges (2, deliberately off-family from the backbone to limit self-preference):**
  `anthropic/claude-sonnet-4.5` and `google/gemini-2.5-flash`, temperature 0, scoring the Si 1–10
  rubric (novelty, feasibility, effectiveness, overall) and pairwise preference.
- **Objective metric:** Literature-Grounded Novelty (LGN) = 1 − max cosine similarity of an idea to
  the nearest of **150 real prior-work abstracts/topic** (1050 total) retrieved from Semantic
  Scholar, embedded with `all-mpnet-base-v2` on an RTX A6000. No LLM opinion involved.
- **Reproducibility:** seed 42; every LLM call cached on disk (re-running the full pipeline is exact
  and free — verified: a second generation pass produced 245/245 cache hits, 0 API calls). Hardware:
  4× RTX A6000 (only 1 used, for embeddings). Total cost ≈ **$3–4** of API usage; runtime ≈ 25 min.
- **Reproduce:** `python src/run_all.py` (or `--n 1` for a 49-idea pilot).

---

## 4. Results

### 4.1 Objective literature-grounded novelty (LGN) — no grounding helps

Mixed-effects model `lgn ~ C(condition, ref=unguided) + (1|topic)`, Holm-corrected across the 6
grounded conditions. **Higher = more distant from real prior work.**

| Condition | LGN mean | Cohen's d vs unguided | p | Holm p |
|---|---|---|---|---|
| unguided (control) | 0.188 | — | — | — |
| deduction | 0.190 | +0.09 | 0.678 | 1.000 |
| literature_comparison | 0.188 | +0.01 | 0.971 | 1.000 |
| small_experiment | 0.181 | −0.19 | 0.334 | 1.000 |
| outcome_imagination | 0.176 | −0.34 | 0.089 | 0.358 |
| induction | 0.174 | −0.40 | 0.044 | 0.219 |
| **proposal_writing** | **0.165** | **−0.66** | **0.001** | **0.007** ✓ |

**No grounding mechanism significantly increases objective novelty.** The only Holm-significant
effect is `proposal_writing` making ideas *more conventional* (closer to existing work). → **H1
refuted.**

### 4.2 Judge rubric (1–10) — the novelty–feasibility trade-off

| Condition | Novelty | Feasibility | Overall |
|---|---|---|---|
| unguided | 5.49 | 7.20 | 5.44 |
| **deduction** | **5.94** ✓ (d=+0.81) | 6.91 | 5.44 |
| literature_comparison | 5.80 (d=+0.57, p=.012) | 6.83 | 5.36 |
| outcome_imagination | 5.70 (d=+0.59) | 6.89 | 5.46 |
| induction | 5.49 | **7.69** (d=+0.59) | 5.47 |
| proposal_writing | 5.43 | **7.67** (d=+0.54) | 5.33 |
| **small_experiment** | **5.17** (d=−0.64) | **7.84** ✓ (d=+0.77) | **5.11** ✗ (d=−0.91) |

(✓ = Holm-significant gain, ✗ = Holm-significant loss vs control.)

Two clean clusters emerge:
- **"Generative" grounding** (deduction, literature_comparison, outcome_imagination) ↑ *judged
  novelty* but ↓ feasibility.
- **"Validation" grounding** (small_experiment, induction, proposal_writing) ↑ *feasibility* but
  ↓/flat novelty.
- **Overall** score: no condition beats the control; `small_experiment` is significantly *worse*.
  → **H2 partially supported (judged novelty only, for 2–3 mechanisms); H3's trade-off confirmed.**

### 4.3 Pairwise win-rate vs the unguided control (position-controlled, 2 judges × 2 orderings)

| Condition | P(grounded ≻ unguided) | 95% CI | t-test vs 0.5 |
|---|---|---|---|
| **literature_comparison** | **0.79** | [0.71, 0.87] | p < 0.001 ✓ |
| outcome_imagination | 0.65 | [0.54, 0.74] | p = 0.006 ✓ |
| deduction | 0.62 | [0.52, 0.71] | p = 0.033 ✓ |
| induction | 0.46 | [0.37, 0.56] | p = 0.468 |
| proposal_writing | 0.43 | [0.33, 0.53] | p = 0.177 |
| **small_experiment** | **0.33** | [0.21, 0.44] | p = 0.005 ✗ |

Pairwise judging is more sensitive than absolute scoring: `literature_comparison` is preferred 79% of
the time even though its *absolute* overall score was flat — a known absolute-vs-comparative judging
gap. `small_experiment` is reliably *dis-preferred*.

### 4.4 Set-level diversity (mitigating Si's "diversity collapse")

| Condition | Mean pairwise distance ↑ | Near-dup rate (cos≥0.8) ↓ |
|---|---|---|
| literature_comparison | **0.456** | **0.091** |
| small_experiment | 0.424 | 0.094 |
| unguided | 0.412 | 0.106 |
| outcome_imagination | 0.407 | 0.096 |
| deduction | 0.404 | 0.104 |
| proposal_writing | 0.397 | 0.109 |
| induction | 0.393 | 0.106 |

Only `literature_comparison` meaningfully increases diversity and lowers duplication — consistent
with its retrieve-and-differentiate mechanism. → **H4 supported only for literature comparison.**

### 4.5 Judge validation — the "novelty mirage", measured

- **Inter-judge agreement** (Claude vs Gemini novelty): Spearman ρ = **0.41** (p = 8×10⁻¹¹) —
  moderate and significant; the rubric is reliable enough to interpret.
- **Convergent validity** (objective LGN vs mean judge novelty): Spearman ρ = **0.012** (p = 0.85) —
  **essentially zero.** The LLM judge's novelty and literature-distance novelty are *unrelated
  constructs.* → **H5 refuted; direct empirical support for the novelty mirage.**

**Figures** (in `figures/`): `fig1_lgn.png`, `fig2_judge_rubric.png`, `fig3_tradeoff.png`,
`fig4_pairwise.png`, `fig5_diversity.png`, `fig6_convergent.png`.
Raw outputs: `results/model_outputs/ideas.jsonl`, `results/judge_scores.jsonl`,
`results/pairwise.jsonl`, `results/analysis_summary.json`, `results/per_idea_table.csv`.

---

## 5. Analysis & Discussion

**Why grounding reshapes rather than improves.** A representative case (topic = Factuality, same
seed): the `small_experiment` scaffold produced **"Chain-of-Verification"** — a *real, already
published* method — whereas `literature_comparison` and `deduction` produced more elaborated
"counterfactual chain-of-reasoning / counterfactual retrieval" variants. This illustrates the
mechanism: asking the model to *predict whether a small test would pass* optimizes for ideas that
*will* survive scrutiny, i.e. safe, known techniques → lower novelty, higher feasibility. Asking the
model to *flip an assumption* or *out-distance retrieved papers* optimizes for differentiation →
higher judged novelty, lower feasibility. Grounding is therefore best understood as a **steering
knob on the novelty–feasibility axis**, not a uniform quality lever.

**The mirage is the most important result.** Judge novelty rises for deduction/literature
comparison, yet objective distance-to-prior-work does **not** — and the two measures are
uncorrelated at the item level (ρ=0.01). The judges reward *rhetorical* novelty (framing, the word
"counterfactual," elaborate mechanism descriptions) that does not correspond to actually occupying
unexplored regions of the literature. This is a clean, controlled reproduction of RQ-Bench's
"novelty mirage" and operationalizes the *All That Glitters* warning: **measure novelty as distance
to retrieved prior work, not as an LLM's opinion.**

**Relation to prior work.** The survey's directional ranking (graph-grounded 3.83 > Chain-of-Ideas
3.21 > vanilla 2.44) suggested grounding > unguided on novelty; our judged-novelty results *partly*
agree (deduction/lit-comparison > unguided) but our objective metric and overall-quality scores do
**not** — a caution that the survey's gains may themselves be judge-inflated. Our control means
(judge novelty ≈ 5.5, feasibility ≈ 7.2) sit in a plausible band relative to Si's human AI-condition
means (novelty ≈ 5.6, feasibility ≈ 6.3).

**Error/■failure modes.** (1) Convergence on a topic-anchored motif ("counterfactual" dominated
Factuality across conditions) — grounding modulates elaboration around it rather than escaping it.
(2) `small_experiment` → rediscovery of named existing methods. (3) Absolute rubric compresses
ideas into 5–6; pairwise reveals preferences the absolute scale hides.

---

## 6. Limitations

1. **Single backbone (gpt-4.1).** Mechanism effects may differ for other model families; we fixed
   the backbone to isolate grounding, trading external validity for internal validity.
2. **No item-level human anchor.** The released Si review data is anonymized *without idea text*, so
   we could not correlate our judge against human scores item-by-item. We validated the judge via
   inter-judge agreement + convergent validity instead; the absent human anchor is a real gap.
3. **"Small experiment" is a thought-experiment, not a real run.** Generic scientific ideas cannot
   be cheaply executed in-loop; we operationalized it as predict-and-critique (as MOOSE/Deep-Ideation
   do). A domain where ideas *are* cheaply runnable (e.g., a fixed prompting benchmark) could test
   true experimental grounding.
4. **LGN is one embedding model's view** of novelty; cosine distance to abstracts is a proxy, not
   ground truth. It is, however, judge-independent — its disagreement with the judge is informative
   regardless of its absolute calibration.
5. **Scale.** N=5/cell (245 ideas) gives medium power; small effects (e.g., outcome_imagination
   novelty, p=0.09) are suggestive but under-powered. Single-condition scaffolds only — we did not
   test combinations (most strong systems combine 2–3 mechanisms).
6. **Topic/contamination.** Topics are public; gpt-4.1 has seen this literature, which may inflate
   the rediscovery-of-known-methods failure mode.

---

## 7. Conclusions & Next Steps

**Answer to the research question.** *Partially, and conditionally.* Grounding the notion of novelty
does **not** uniformly produce higher-quality ideas. It **steers** the novelty–feasibility
trade-off: deduction, literature comparison, and outcome imagination raise *judged* novelty and win
pairwise against unguided generation (literature comparison most strongly, 79%, and it is also the
only mechanism that improves idea-set diversity), while small experiments, induction, and proposal
writing raise feasibility at novelty's expense. Crucially, **none increases objective distance from
prior work, and LLM-judged novelty is uncorrelated with that objective measure** — so the
hypothesis's "better novelty" is real in human-style judgment but a *mirage* under a grounded metric.

**Recommendations.**
- For *judged* novelty + diversity + head-to-head wins: use **literature_comparison** grounding.
- For *feasibility*: use **induction** or **proposal_writing**; avoid `small_experiment` if novelty
  matters (it rediscovers known methods).
- For *evaluation*: never report single-LLM-judge novelty alone; pair it with a literature-distance
  metric and pairwise comparison — they can disagree completely.

**Follow-ups.** (1) Replicate across backbones (Claude, Gemini, DeepSeek) to test generality. (2)
Combine mechanisms (e.g., deduction → literature_comparison filtering) to seek novelty *and*
feasibility together. (3) Build the missing item-level human anchor on fresh, post-cutoff ideas to
calibrate which metric tracks expert judgment. (4) Test true small-experiment grounding in a
runnable prompting benchmark where ideas can be executed in-loop.

---

## References (key)
- Si, Yang, Hashimoto (2024). *Can LLMs Generate Novel Research Ideas?* arXiv:2409.04109 (topics, rubric, human anchor).
- *On the Limits of LLM-as-Judge for Scientific Novelty* / RQ-Bench (2026). arXiv:2606.12071 (novelty mirage).
- *All That Glitters Is Not Novel* (2025). arXiv:2502.16487 (novelty as distance to prior work).
- *Sparks of Science / HypoGen* (2025). arXiv:2504.12976 (Bit→Flip→Spark deduction schema).
- SciMON (2023, arXiv:2305.14259), MOOSE (2023, arXiv:2309.02726), AutoDiscovery (2025,
  arXiv:2507.00310), Deep-Ideation (2025, arXiv:2511.02238) — the six grounding mechanisms.
- Tools: OpenAI `gpt-4.1`; OpenRouter `claude-sonnet-4.5`, `gemini-2.5-flash`; sentence-transformers
  `all-mpnet-base-v2`; Semantic Scholar Graph API; statsmodels (MixedLM), scipy, scikit-learn.
