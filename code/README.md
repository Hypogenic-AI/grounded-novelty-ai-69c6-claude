# Cloned Repositories

Code repositories relevant to **Scientific Idea Generation with Grounded Novelty**.
The cloned working trees are git-ignored (see root `.gitignore`); `.git` dirs were
stripped to save space. Re-clone with the commands listed per repo.

Each repo is mapped to one or more **grounding mechanisms** from the hypothesis
(deduction · induction · proposal writing · outcome imagination · small experiments · literature comparison).

---

## 1. AI-Researcher (Si et al., 2024) — `code/AI-Researcher/`
- **URL**: https://github.com/NoviScl/AI-Researcher  ·  `git clone https://github.com/NoviScl/AI-Researcher`
- **Paper**: "Can LLMs Generate Novel Research Ideas?" (arXiv 2409.04109)
- **Why it matters**: The canonical **ideation-agent baseline** and the gold reference for
  experimental design (human study with 100+ NLP researchers, blind novelty/feasibility review).
- **Grounding**: literature_comparison (RAG over Semantic Scholar), proposal_writing (full idea templates).
- **Key contents**:
  - `ai_researcher/` — the ideation agent (RAG + over-generate + LLM rerank).
  - `reviews_ideation/data_points_all_anonymized.json` — **human review scores** for LLM vs human ideas (novelty/feasibility/excitement). Reusable dataset (see `datasets/README.md`).
  - `reviews_ideation/`, `reviews_execution/` — analysis scripts (`stats_*.py`).
  - `requirements.txt` — dependencies.

## 2. SciMON / CLBD (Wang et al., 2023) — `code/SciMON-clbd/`
- **URL**: https://github.com/eaglew/clbd  ·  `git clone https://github.com/eaglew/clbd`
- **Paper**: "SciMON: Scientific Inspiration Machines Optimized for Novelty" (arXiv 2305.14259)
- **Why it matters**: Reference implementation of **iterative novelty grounding via literature comparison** — retrieve "inspirations", generate, then iteratively compare to prior papers and revise until novel enough.
- **Grounding**: literature_comparison (core), induction.
- **Key contents**:
  - `models/`, `biomedical_models/` — generation models.
  - `data/*.zip` — datasets (see `datasets/README.md`); `evaluation/` — novelty metrics.
  - `preprocess/` — IE / KG / citation-network construction.

## 3. MOOSE (Yang et al., 2023) — `code/MOOSE/`
- **URL**: https://github.com/ZonglinY/MOOSE  ·  `git clone https://github.com/ZonglinY/MOOSE`
- **Paper**: "LLMs for Automated Open-domain Scientific Hypotheses Discovery" (arXiv 2309.02726)
- **Why it matters**: Multi-module **hypothetical induction** framework with **three feedback mechanisms** (present/past/future feedback) that refine hypotheses — a concrete "small experiments / feedback" grounding.
- **Grounding**: induction (core), small_experiments (feedback loops), deduction.
- **Key contents**:
  - `main.py`, `main.sh` — generation pipeline; `evaluate_main.py`, `evaluator.py` — eval.
  - `Data/` — **social-science hypotheses dataset** (business_research.xlsx, summary*.xlsx) — reusable.
  - `consistency_between_expert_gpt4.py` — GPT-4-vs-expert agreement analysis.

## 4. Chain-of-Ideas / CoI-Agent (Li et al., 2024) — `code/CoI-Agent/`
- **URL**: https://github.com/DAMO-NLP-SG/CoI-Agent  ·  `git clone https://github.com/DAMO-NLP-SG/CoI-Agent`
- **Paper**: "Chain of Ideas" (arXiv 2410.13185)
- **Why it matters**: Organizes literature into a **chain** mirroring a field's progression, then ideates; ships **Idea Arena** evaluation protocol (pairwise/Swiss). Cheap (~$0.50/idea).
- **Grounding**: literature_comparison, proposal_writing.

## 5. Virtual-Scientists / VirSci (Su et al., 2024) — `code/Virtual-Scientists/`
- **URL**: https://github.com/open-sciencelab/Virtual-Scientists  ·  `git clone https://github.com/open-sciencelab/Virtual-Scientists`
- **Paper**: "Many Heads Are Better Than One" (arXiv 2410.09403)
- **Why it matters**: **Multi-agent** team that generates → evaluates → refines ideas; built on AgentScope. Uses an OAG-based scientific corpus (`preprocess_data/`).
- **Grounding**: literature_comparison, proposal_writing, small_experiments (agent critique loops).
- **Key contents**: `sci_platform/` (system), `agentscope-main/` (framework), `requirements.txt`.

## 6. AutoDiscovery (2025) — `code/AutoDiscovery/`
- **URL**: https://github.com/allenai/autodiscovery  ·  `git clone https://github.com/allenai/autodiscovery`
- **Paper**: "AutoDiscovery: Open-ended Scientific Discovery via Bayesian Surprise" (arXiv 2507.00310)
- **Why it matters**: Drives exploration by **Bayesian surprise** (prior→posterior shift after running experiments) with MCTS — the clearest implementation of **outcome imagination + small experiments** as a novelty signal. Evaluated on 21 real datasets.
- **Grounding**: outcome_imagination (core), small_experiments (core).
- **Key contents**: `src/`, `environment.yml`, `pyproject.toml`, `artifacts/`.

## 7. Future-Idea-Generation (Kumar et al., 2024) — `code/Future-Idea-Generation/`
- **URL**: https://github.com/sandeep82945/Future-Idea-Generation  ·  `git clone https://github.com/sandeep82945/Future-Idea-Generation`
- **Paper**: "Can LLMs Unlock Novel Scientific Research Ideas?" (arXiv 2409.06185)
- **Why it matters**: Source of two **automated novelty metrics** — **Idea Alignment Score (IAScore)** and **Idea Distinctness Index** — usable as cheap eval signals.
- **Grounding**: literature_comparison (metrics), proposal_writing.

## 8. Deep-Ideation (Zhao et al., 2025) — `code/Deep-Ideation/`
- **URL**: https://github.com/kyZhao-1/Deep-Ideation  ·  `git clone https://github.com/kyZhao-1/Deep-Ideation`
- **Paper**: "Deep Ideation" (arXiv 2511.02238)
- **Why it matters**: explore-expand-evolve over a **scientific concept network** with a **critic engine trained on real reviewer feedback** (a learned novelty/feasibility grounding signal).
- **Grounding**: literature_comparison, small_experiments (critic feedback).
- **Note**: At clone time the repo contained mainly a README (code release may be pending) — re-pull before relying on it.

---

## Not cloned (referenced only)
- **The AI Scientist** (Sakana AI) — https://github.com/SakanaAI/AI-Scientist — end-to-end autonomous research (idea→experiment→paper); heavy. Relevant as a full closed-loop system if `small_experiments` grounding is explored.
- **IdeaBench** — benchmark + Insight Score eval (arXiv 2411.02429); dataset distributed via the paper's repo/HF when available.

## Dependency note for the experiment runner
These repos pin conflicting deps (different `transformers`, `openai`, `agentscope` versions).
Do **not** install them all into the shared workspace `.venv`. Install per-repo in a throwaway
env only if you need to *run* one; for most experiments you only need their **data**, **prompts**,
and **metric definitions**, which can be read directly from the source files above.
