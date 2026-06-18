"""Central configuration for the grounded-novelty ideation experiment.

All knobs (models, topics, conditions, sample sizes, paths) live here so every
script is reproducible from a single source of truth.
"""
import os

# ----------------------------------------------------------------------------
# Reproducibility
# ----------------------------------------------------------------------------
SEED = 42

# ----------------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------------
# Backbone idea generator (fixed across all conditions).
GEN_MODEL = "gpt-4.1"
GEN_TEMPERATURE = 0.8
GEN_TOP_P = 1.0
GEN_MAX_TOKENS = 1600

# Judge ensemble — deliberately OFF-FAMILY from the gpt-4.1 backbone to limit
# self-preference bias (a known LLM-as-judge failure mode).
JUDGE_MODELS = [
    ("anthropic/claude-sonnet-4.5", "openrouter"),
    ("google/gemini-2.5-flash", "openrouter"),
]
JUDGE_TEMPERATURE = 0.0
JUDGE_MAX_TOKENS = 900

# Embedding model for objective literature-grounded novelty + diversity.
EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"

# ----------------------------------------------------------------------------
# API routing
# ----------------------------------------------------------------------------
PROVIDERS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "key_env": "OPENAI_API_KEY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "key_env": "OPENROUTER_KEY",
    },
}
GEN_PROVIDER = "openai"

# ----------------------------------------------------------------------------
# Experimental design
# ----------------------------------------------------------------------------
# The canonical 7 NLP ideation topics from Si, Yang & Hashimoto (2024),
# phrased as standardized topic seeds. EVERY condition receives the identical
# seed; only the reasoning scaffold differs.
TOPICS = {
    "Bias": "novel prompting methods to reduce social biases and stereotypes of large language models",
    "Coding": "novel prompting methods to improve code generation performance of large language models",
    "Safety": "novel prompting methods to improve large language models' robustness against adversarial attacks or jailbreaks",
    "Multilingual": "novel prompting methods to improve large language models' performance on multilingual tasks or low-resource languages",
    "Factuality": "novel prompting methods to improve factuality and reduce hallucination of large language models",
    "Math": "novel prompting methods to improve mathematical problem solving of large language models",
    "Uncertainty": "novel prompting methods to better quantify uncertainty or calibrate the confidence of large language models",
}

# The 7 conditions: unguided control + one per grounding mechanism.
CONDITIONS = [
    "unguided",            # control
    "deduction",           # Bit -> Flip -> Spark (HypoGen)
    "induction",           # observations -> general hypothesis (MOOSE)
    "proposal_writing",    # full mini-proposal -> distilled idea (Si/VirSci)
    "outcome_imagination", # imagine best outcome / belief shift (AutoDiscovery)
    "literature_comparison",  # retrieve + contrast + revise (SciMON)
    "small_experiment",    # propose+predict tiny test, self-critique (Deep-Ideation)
]
GROUNDED_CONDITIONS = [c for c in CONDITIONS if c != "unguided"]

N_IDEAS_PER_CELL = 5      # replicates per (condition x topic)

# Number of real prior-work abstracts to retrieve per topic for the
# literature-grounded novelty corpus.
CORPUS_PER_TOPIC = 150

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
CACHE = os.path.join(RESULTS, "cache")
OUTPUTS = os.path.join(RESULTS, "model_outputs")
FIGURES = os.path.join(ROOT, "figures")
LOGS = os.path.join(ROOT, "logs")
for _d in (RESULTS, CACHE, OUTPUTS, FIGURES, LOGS):
    os.makedirs(_d, exist_ok=True)

IDEAS_FILE = os.path.join(OUTPUTS, "ideas.jsonl")
CORPUS_FILE = os.path.join(OUTPUTS, "prior_work_corpus.json")
LGN_FILE = os.path.join(RESULTS, "objective_metrics.json")
JUDGE_FILE = os.path.join(RESULTS, "judge_scores.jsonl")
PAIRWISE_FILE = os.path.join(RESULTS, "pairwise.jsonl")
