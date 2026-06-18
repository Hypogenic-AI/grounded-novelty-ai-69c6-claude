# Planning — Scientific Idea Generation with Grounded Novelty

## Motivation & Novelty Assessment

### Why This Research Matters
LLM scientific ideation is now good enough that, in a 100+ expert study (Si et al., 2024), AI
ideas were judged *more novel* than expert humans — yet the field still distrusts LLM ideas,
because "novelty" is ill-defined and unguided LLMs swing between **incremental** rephrasings and
**implausible** over-reaches. If a cheap, model-agnostic *grounding scaffold* reliably moves ideas
toward the novel-and-plausible sweet spot, it directly improves automated discovery pipelines and
costs nothing to deploy (it is a prompting protocol, not a new model).

### Gap in Existing Work (from `literature_review.md`)
Every strong system champions **one** grounding mechanism on **its own** dataset and metric:
SciMON/CoI/Nova (literature comparison), MOOSE/causal-graph (induction), HypoGen (deduction, Bit→
Flip→Spark), Si-agent/VirSci (proposal writing), AutoDiscovery (outcome imagination / Bayesian
surprise), Deep-Ideation (critic feedback ≈ small experiments). **No paper compares the six
mechanisms head-to-head under one controlled protocol** — same backbone, same seed topics, same
metrics, same output format. The hypothesis is therefore essentially *untested as a controlled
ablation*. Two evaluation-skeptic papers (All-That-Glitters; RQ-Bench "novelty mirage") add that the
*evaluation* must itself be grounded — not a single LLM's novelty opinion.

### Our Novel Contribution
1. **A single controlled ablation** of the user's six grounding mechanisms + an unguided control,
   with a fixed backbone (gpt-4.1), the canonical 7 Si NLP topics, identical output schema, and N=5
   replicates/cell (245 ideas).
2. **Grounded evaluation**: an *objective* literature-grounded novelty metric (embedding distance to
   real prior-work abstracts retrieved from Semantic Scholar) that needs no LLM opinion, plus a
   2-judge ensemble (Claude-Sonnet-4.5 + Gemini-2.5-Flash, both off-family from the gpt-4.1 backbone
   to limit self-preference) cross-checked for inter-judge agreement and **convergent validity**
   against the objective metric — a direct test of the "novelty mirage."
3. **Set-level diversity** measurement to test whether grounding fixes Si's diversity-collapse.

### Experiment Justification
- **E1 — Generation ablation (245 ideas):** the core manipulation. Needed to produce comparable
  ideas that differ *only* in grounding scaffold.
- **E2 — Objective literature-grounded novelty + diversity:** bias-free test of "is the idea far
  from existing work?" and "does grounding broaden the idea set?". Needed because LLM novelty
  judgments are untrustworthy (RQ-Bench).
- **E3 — Judge-ensemble rubric (novelty/feasibility/effectiveness/overall) + pairwise win-rate vs
  the unguided control:** maps onto the human Si rubric so results are comparable to the literature;
  pairwise (both orderings, 2 judges) gives a position-bias-controlled "grounding > unguided" test.
- **E4 — Judge validation:** inter-judge agreement + convergent validity (judge novelty vs objective
  embedding novelty) to decide how much to trust E3. Needed because of the novelty-mirage risk.

---

## Research Question
Do LLMs generate **higher-quality scientific ideas** (more novel *and* still feasible) when the
abstract notion of novelty is **grounded** through deduction, induction, proposal writing, outcome
imagination, small experiments, or literature comparison — versus unguided generation — holding the
backbone model, seed topic, and output format fixed?

## Hypothesis Decomposition
- **H1 (objective novelty):** grounded conditions produce ideas with greater embedding distance to
  retrieved prior work than the unguided control.
- **H2 (judged quality):** grounded conditions score higher on the 1–10 novelty/overall rubric and
  win >50% of pairwise comparisons against matched unguided ideas.
- **H3 (no feasibility collapse):** grounding does not significantly *reduce* feasibility (the Si
  trade-off) — ideally the literature/induction/small-experiment arms keep or raise it.
- **H4 (diversity):** grounding increases set-level diversity (mitigates diversity collapse).
- **H5 (evaluation):** the LLM judge's novelty correlates with the *objective* metric (convergent
  validity); if not, that supports the novelty-mirage caution and we down-weight E3.

Independent variable = grounding condition (7 levels). Blocking variable = topic (7). Fixed =
backbone, sampling params, topic seed text, output schema. DV = the E2/E3 metrics above.

## Proposed Methodology

### Approach
One fully-crossed 7 (condition) × 7 (topic) design, 5 replicates/cell. **Critical control:** every
condition emits the *same* standardized idea JSON (title, problem, motivation, proposed method,
experiment plan); only the *reasoning scaffold preceding the idea* differs. This isolates grounding
from output-format/length confounds (Si's AI-ideas-are-longer confound). Idea length is logged and
used as a covariate.

### Conditions (scaffolds; identical final output schema)
1. **unguided** (control) — "propose a novel idea on TOPIC", single shot.
2. **deduction** — HypoGen Bit→Flip→Spark: state the prevailing assumption (Bit), invert it (Flip),
   derive the idea (Spark).
3. **induction** — present 4–6 concrete observations/findings on the topic, induce a general
   hypothesis, then the idea.
4. **proposal_writing** — draft a full mini-proposal incl. expected results, then distill the idea.
5. **outcome_imagination** — imagine the best plausible empirical outcome and the belief it would
   shift (Bayesian-surprise framing), then back out the idea that would produce it.
6. **literature_comparison** — retrieve nearest real prior papers (S2), explicitly contrast, and
   revise the idea until distinct (SciMON-style).
7. **small_experiment** — propose a tiny falsification test, predict its result, self-critique, and
   refine the idea using that feedback (MOOSE/Deep-Ideation critic operationalization).

### Backbone / Judges / Embeddings
- Backbone generator: **gpt-4.1**, temperature 0.8, top_p 1.0, per-idea integer seed.
- Judges: **anthropic/claude-sonnet-4.5** + **google/gemini-2.5-flash** (off-family → less
  self-preference), temperature 0.
- Embeddings: **sentence-transformers all-mpnet-base-v2** on GPU (RTX A6000).
- Prior-work corpus: ~150 recent abstracts/topic via Semantic Scholar API (S2_API_KEY).

### Baselines
`unguided` is the pre-registered control. Literature anchors: Si human rubric means
(AI novelty ≈ 5.6, feasibility ≈ 6.3) for distributional sanity; survey ranking GoAI 3.83 >
CoI 3.21 > vanilla 2.44 as the directional prior (grounding > unguided).

### Evaluation Metrics & why
- **Literature-Grounded Novelty (LGN)** = 1 − max cosine sim to nearest prior-work abstract
  (objective; All-That-Glitters recommendation). Primary.
- **Rubric 1–10** novelty/feasibility/effectiveness/overall (Si standard; comparable to literature).
- **Pairwise win-rate vs unguided** (position-controlled, 2 judges) — direct H2 test.
- **Set-level diversity** = mean pairwise embedding distance within a (condition×topic) cell.

### Statistical Analysis Plan
- Primary: linear mixed-effects `metric ~ C(condition) + (1|topic)`, unguided = reference; report
  coefficients, 95% CI, p. Robustness: add idea length as covariate.
- Pairwise: win-rate vs 0.5, bootstrap 95% CI + binomial test per condition.
- Effect sizes: Cohen's d vs unguided. Multiple comparisons: Holm across the 6 grounded conditions.
- Judge: Spearman inter-judge + Spearman(judge novelty, LGN) for convergent validity.
- Significance level α = 0.05. Seeds fixed (42). All LLM calls cached for exact reproduction.

## Expected Outcomes
Support: grounded conditions beat unguided on LGN and pairwise win-rate with no feasibility drop;
literature_comparison & deduction strongest on novelty; induction/small_experiment best on
feasibility. Refute: no condition separates from unguided, or grounding only inflates LLM-judged
(not objective) novelty (→ novelty mirage).

## Timeline & Milestones
Setup/corpus (done/0.5h) → generation harness + pilot 1 topic (0.75h) → full 245-idea generation
(0.75h) → metrics+judging (1h) → stats+figures (0.75h) → REPORT/README (0.5h). ~20–30% buffer.

## Potential Challenges
- API rate limits / cost → caching + retry/backoff; gpt-4.1 backbone, cheap judges. Est. cost <$15.
- Judge bias → off-family ensemble, pairwise both-orderings, convergent-validity check.
- Length confound → identical schema + length covariate.
- S2 retrieval gaps → cache corpus; fall back to local paper abstracts if API fails.
- No item-level human anchor (anonymized data lacks idea text) → validate judge via agreement +
  convergent validity instead; documented as a limitation.

## Success Criteria
A reproducible 245-idea controlled ablation with: (1) the objective LGN + diversity results, (2) the
judge-ensemble rubric + pairwise results with inter-judge agreement, (3) mixed-effects stats with
effect sizes and corrections, and (4) an honest verdict on H1–H5 — even if negative.
