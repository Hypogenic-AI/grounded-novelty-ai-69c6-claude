# Literature Review — Scientific Idea Generation with Grounded Novelty

**Hypothesis under study.** *LLMs generate higher-quality scientific ideas when the notion of
novelty is **grounded** through one of six mechanisms — deduction, induction, proposal writing,
outcome imagination, small experiments, or literature comparison — as opposed to unguided
generation.*

This review synthesizes 18 papers (downloaded to `papers/`, full structured notes in
`.neurico/paper_notes.json`) gathered via the paper-finder service (3 diligent searches → 150+
relevance-ranked hits; 49 at relevance 3). It is organized around the six grounding mechanisms
named in the hypothesis so that the experiment runner can directly map methods → conditions.

---

## 1. Research-Area Overview

LLM-based scientific ideation matured rapidly in 2023–2026. The pivotal empirical result is **Si
et al. (2024)**: in a controlled study with 100+ NLP researchers, an LLM ideation agent produced
ideas judged **more novel than human experts** (p<0.05) but slightly **less feasible**, while
exposing two systemic weaknesses — **unreliable LLM self-evaluation** and **low idea diversity**
(over-generating thousands of seeds yields only a few hundred unique ideas). Almost every
subsequent system can be read as an attempt to fix these weaknesses by **grounding** generation in
some external or structured signal rather than free-form prompting. The two recent surveys
(arXiv 2504.05496; 2511.07448) converge on the same taxonomy: methods differ mainly in *what they
ground novelty against* — prior literature, knowledge/concept graphs, learned critics, or actual
experimental feedback.

A cautionary counter-current matters for this project: **All That Glitters Is Not Novel** (2025)
shows 24% of "novel" AI research documents are smartly plagiarized and bypass detectors, and **On
the Limits of LLM-as-Judge** (2026) documents a **"novelty mirage"** — LLM judges rate
model-generated questions as highly novel while human experts prefer the real reference questions.
Together these imply that *grounding* is needed not only in **generation** but also in
**evaluation**, and that automated novelty metrics must be validated against human/literature
anchors.

---

## 2. Mapping the Literature onto the Six Grounding Mechanisms

| Mechanism (hypothesis) | Representative grounded methods | Core operationalization |
|---|---|---|
| **Literature comparison** | SciMON, Chain-of-Ideas, Nova, IdeaBench, Future-Idea (IAScore) | retrieve prior papers; iteratively compare candidate idea to them and revise until "novel enough"; score distance from existing work |
| **Induction** | MOOSE, psychology causal-graph (2402.14424) | from raw observations/corpus → general hypothesis; refine with feedback |
| **Deduction** | HypoGen (Bit→Flip→Spark), HypoSpace | derive a counterproposal/prediction from a stated assumption or theory |
| **Proposal writing** | Si et al. agent, Learning-to-Generate (SFT+RL), VirSci | force ideas into full standardized proposals/experiment plans, scored on novelty+feasibility+effectiveness |
| **Outcome imagination** | AutoDiscovery (Bayesian surprise), Dynamic-Control reward models | predict expected results / belief-shift before committing; reward surprising-but-plausible ideas |
| **Small experiments** | AutoDiscovery, MOOSE feedback, Deep-Ideation critic, NovelSeek (referenced) | run cheap experiments / learned reviewer-critic and feed empirical signal back into ideation |

Most strong systems combine 2–3 mechanisms; the **unguided** baseline (vanilla LLM prompting) is
the consistently weakest condition across every comparison (see §5).

---

## 3. Key Papers

### 3.1 Foundational / evaluation anchors

**Si, Yang, Hashimoto (2024) — Can LLMs Generate Novel Research Ideas?** (arXiv 2409.04109, 371 cit)
- *Method*: 49 expert writers + 79 reviewers (298 blind reviews), 7 NLP topics (Bias, Coding,
  Safety, Multilingual, Factuality, Math, Uncertainty). Conditions = Human / AI / AI+human-rerank.
  Agent = RAG (top-10 papers) → generate **4000 seeds/topic** → dedup at 0.8 cosine → rank via
  Claude-3.5-Sonnet pairwise Swiss tournament (ranker trained on 1,200 ICLR-2024 submissions) →
  expand to standardized proposals. Welch t-tests + Bonferroni over 3 designs.
- *Grounding*: literature_comparison + proposal_writing (no genuine induction/deduction/experiment grounding).
- *Results*: **Novelty AI 5.64 vs Human 4.84 (p<0.01)**; AI+Rerank 5.81 (p<0.001). Excitement AI 5.19
  vs 4.55 (p<0.05). **Feasibility AI 6.34 vs 6.61 (n.s., p=1.00)**. Two failure modes: **diversity
  collapse** — 4000 ideas/topic yield only ~200 unique (**95% duplication**); **unreliable
  self-eval** — LLM ranker 53.3% consistency vs human 56.1%, and manual human rerank beats the LLM
  ranker on 32/49 ideas. Confound: AI ideas longer (1186 vs 902 words).
- *Why central*: the canonical **baseline** and the **gold human-review dataset**
  (`code/AI-Researcher/reviews_ideation/data_points_all_anonymized.json`). 7-topic prompt set.
  Novelty/excitement drive overall score (r=0.73 / 0.85); feasibility barely correlates (r=0.10).

**On the Limits of LLM-as-Judge for Scientific Novelty Assessment (2026)** (arXiv 2606.12071)
- Introduces **RQ-Bench** (author-anchored research questions from recent arXiv). LLM judges show a
  **novelty mirage**; experts disagree. *Implication*: do **not** rely on a single LLM judge for the
  novelty metric — anchor to literature/human references and use comparative (pairwise) judging.

**All That Glitters Is Not Novel (2025)** (arXiv 2502.16487)
- 13 experts find **24%** of AI research docs paraphrased/borrowed; detectors fail. *Implication*:
  measure novelty as **distance to retrieved prior work**, not just LLM opinion.

### 3.2 Literature-comparison grounding

**SciMON (Wang et al., 2023)** (arXiv 2305.14259, 181 cit) — retrieve "inspirations" → generate →
**iteratively compare to prior papers and revise until novel enough**. Datasets: ACL Anthology
(67,408 papers), PubMed biochemical (5,708), gold subset (194). Code+data: `code/SciMON-clbd`.
The clearest direct implementation of the literature-comparison arm.

**Chain-of-Ideas (Li et al., 2024)** (arXiv 2410.13185, 90 cit) — organize literature into a
**chain** mirroring a field's progression; ships **Idea Arena** pairwise/Swiss evaluation; ~$0.50/idea.
Code: `code/CoI-Agent`.

**Nova (2024)** (arXiv 2410.14255) — iterative **planned retrieval** of external knowledge → 3.4×
more unique novel ideas, 2.5× more top-rated ideas vs SOTA over 170 seed papers (Swiss Tournament).

**Future-Idea-Generation / Kumar et al. (2024)** (arXiv 2409.06185) — source of two cheap automated
metrics: **IAScore** (alignment to authors' real future-work) and **Idea Distinctness Index**.
Dataset: S2ORC, 1,250 papers across 5 fields. Code: `code/Future-Idea-Generation`.

**IdeaBench (2024)** (arXiv 2411.02429) — benchmark: 2,374 influential papers + 29,408 references;
two-stage GPT-4o ranking → **Insight Score** for novelty/feasibility.

### 3.3 Induction grounding

**MOOSE / Yang et al. (2023)** (arXiv 2309.02726, 115 cit) — **hypothetical induction** from raw
corpus to novel+valid social-science hypotheses; **three feedback mechanisms** (past/present/future).
Dataset = **TOMATO** (50 recent social-science papers, 7 disciplines) + Reality-Checker eval. Code+data:
`code/MOOSE` (incl. `Data/*.xlsx`). Directly covers induction **and** small-experiments (feedback).

**Automating Psychological Hypothesis Generation (2024)** (arXiv 2402.14424, 46 cit) — build a
**causal knowledge graph** from 43,312 psychology articles + LLM; link-prediction → 130 hypotheses.
LLM+graph matches experts on novelty and **beats LLM-only** (t(59)=4.32, p<0.001). Grounding the LLM
in an inductive causal structure outperforms unguided LLM — a clean confirmation of the hypothesis.

### 3.4 Deduction grounding

**Sparks of Science / HypoGen (2025)** (arXiv 2504.12976) — **HypoGen** dataset (~5,478 train / 50
test) with **Bit→Flip→Spark** schema + explicit **Chain-of-Reasoning**. Fine-tuning on the
deductive Bit→Flip structure improves novelty, feasibility, overall quality. Downloaded to
`datasets/hypogen`. The best fit for the deduction arm.

**HypoSpace (2025)** (arXiv 2510.15614) — evaluates LLMs as **set-valued** hypothesis generators
under underdetermination; metrics **Validity Rate** and **Uniqueness/Novelty Rate** over controlled
tasks (causal inference from perturbations; 3D voxel reconstruction). Code: `github.com/CTT-Pavilion/_HypoSpace`.

### 3.5 Proposal-writing & learned-control grounding

**Learning to Generate Research Idea with Dynamic Control (2024)** (arXiv 2412.14626) — **SFT + RL**
with multi-dimensional reward models (novelty/feasibility/effectiveness) and inference-time
dimensional controllers. Data: ICLR 2023-24 (1,000 SFT), NeurIPS 2023-24 (3,271 RL). Defines the
standard 0–10 rubric used widely (feasibility = practical in 1–2 months, limited GPU, API access).

**VirSci / Many Heads (2024)** (arXiv 2410.09403) — **multi-agent** team generate→evaluate→refine;
outperforms SOTA on novelty. Code: `code/Virtual-Scientists`.

### 3.6 Outcome-imagination & small-experiments grounding

**AutoDiscovery (2025)** (arXiv 2507.00310) — open-ended discovery driven by **Bayesian surprise**
(epistemic shift prior→posterior **after running experiments**), MCTS w/ progressive widening,
surprisal reward. Metrics: Surprisal Count, Search Efficiency. Data: DiscoveryBench tasks.
Code: `code/AutoDiscovery` (+ `allenai/discoverybench`). The clearest outcome-imagination +
small-experiments implementation.

**Deep-Ideation (2025)** (arXiv 2511.02238) — explore-expand-evolve over a **scientific concept
network** with a **critic engine trained on real reviewer feedback**; +10.67% idea quality.
Code: `code/Deep-Ideation`.

### 3.7 Surveys

**A Survey on Hypothesis Generation … (2025)** (arXiv 2504.05496) and **LLMs for Scientific Idea
Generation: A Creativity-Centered Survey (2025)** (arXiv 2511.07448). The latter organizes methods
into 5 families (external-knowledge augmentation, prompt-based distributional steering,
inference-time scaling, multi-agent collaboration, parameter-level adaptation) and reports a useful
relative ranking: **GoAI (graph-grounded) novelty 3.83 > Chain-of-Ideas 3.21 > vanilla prompting
2.44** — i.e., grounding > unguided on novelty, the headline trend supporting the hypothesis.

---

## 4. Common Methodologies, Baselines, Metrics, Datasets

### 4.1 Common methodologies
- **RAG / retrieval grounding** (literature comparison): SciMON, CoI, Nova, Si et al., IdeaBench.
- **Knowledge / concept graphs** (induction/deduction): psychology causal graph, Deep-Ideation, SciMON-KG.
- **Iterative refine-against-prior-work loops**: SciMON (novelty until threshold), MOOSE (feedback), Deep-Ideation (critic).
- **Search over idea space**: MCTS (AutoDiscovery), Swiss-tournament ranking (Si, Nova, CoI Idea Arena).
- **Learned control**: SFT+RL reward models (Dynamic Control), reviewer-trained critics (Deep-Ideation).

### 4.2 Standard baselines (use these)
1. **Vanilla / unguided LLM prompting** — the control condition of the hypothesis (weakest everywhere).
2. **RAG-only ideation agent (Si et al.)** — literature-grounded but no iterative novelty optimization; the strongest *simple* baseline and the reference agent.
3. **Chain-of-Ideas** and **SciMON** — grounded baselines with released code.

### 4.3 Evaluation metrics (recommended stack)
- **Human-style rubric, 1–10**: Novelty, Feasibility, (Expected) Effectiveness, Excitement, Overall — the Si et al. / Dynamic-Control standard.
- **Reference-based novelty (literature-grounded)**: IAScore (alignment to real future work), Idea Distinctness Index, IdeaBench Insight Score, embedding distance to nearest retrieved paper.
- **Set-level**: Validity Rate + Uniqueness/Novelty Rate (HypoSpace); diversity/dedup counts (Si et al. diversity failure).
- **Comparative judging, not standalone** (RQ-Bench finding): use pairwise/Swiss tournaments and **validate the LLM judge against the Si et al. human scores** before trusting it.

### 4.4 Datasets in the literature (see `datasets/README.md`)
- **HypoGen** (HF, downloaded) — Bit-Flip-Spark; deduction arm.
- **Si et al. ideas+reviews** (in `code/AI-Researcher`) — gold human novelty/feasibility anchor.
- **MOOSE/TOMATO** (in `code/MOOSE/Data`) — open-domain induction.
- **SciMON/CLBD** (in `code/SciMON-clbd/data`) — literature-based discovery.
- **IdeaBench / S2ORC / DiscoveryBench / RQ-Bench** — referenced, fetch if needed.

---

## 5. Gaps and Opportunities (directly relevant to the hypothesis)

1. **No head-to-head comparison of the six grounding mechanisms under one protocol.** Existing
   papers each champion one mechanism with its own dataset/metric. The hypothesis is essentially
   untested as a *controlled ablation*: same backbone LLM, same seed topics, same metrics, six
   grounding conditions + an unguided control. **This is the clearest experimental contribution.**
2. **Self-evaluation is unreliable** (Si et al.) and **LLM-judge novelty is a mirage** (RQ-Bench) —
   so grounding the *evaluation* (literature distance, human-anchored comparative judging) is as
   important as grounding *generation*.
3. **Diversity collapse** (Si et al.): test whether grounding improves *set-level* novelty/coverage,
   not just single-idea scores (use HypoSpace metrics).
4. **Plagiarism risk** (All That Glitters): literature-comparison grounding should be evaluated for
   *reducing* inadvertent copying, an underexplored benefit.

---

## 6. Recommendations for Our Experiment

- **Design**: one controlled study — fixed backbone (e.g., GPT-4o / Claude / DeepSeek per
  Si/Dynamic-Control conventions), fixed seed topics (reuse Si et al.'s 7 NLP topics and/or HypoGen
  Bits), and **seven conditions**: `unguided` (control) + one per grounding mechanism
  (deduction=Bit→Flip; induction=corpus→hypothesis w/ feedback; literature_comparison=SciMON-style
  retrieve-and-revise; proposal_writing=full standardized proposal; outcome_imagination=predict
  results / Bayesian-surprise rerank; small_experiments=cheap empirical/critic feedback).
- **Datasets**: **HypoGen** (deduction; ready in `datasets/hypogen`), **MOOSE/TOMATO** (induction),
  **Si et al. ideas** (anchor + topics), **SciMON/CLBD** (literature comparison). All already local.
- **Baselines**: vanilla prompting (control), Si et al. RAG agent, Chain-of-Ideas, SciMON.
- **Metrics**: 1–10 novelty/feasibility/effectiveness rubric **+** a literature-grounded reference
  metric (IAScore / embedding distance / Insight Score) **+** set-level diversity (HypoSpace).
  Use **comparative** LLM judging validated against the Si et al. human scores; report agreement.
- **Methodological cautions**: avoid single-shot LLM self-judging of novelty; dedup before counting
  unique ideas; check generated ideas against retrieved prior work for plagiarism.
- **Reusable code**: SciMON (`code/SciMON-clbd`), MOOSE (`code/MOOSE`), AI-Researcher agent
  (`code/AI-Researcher`), Future-Idea metrics (`code/Future-Idea-Generation`), AutoDiscovery
  (`code/AutoDiscovery`). Read prompts/metrics directly; do **not** co-install their conflicting deps.
