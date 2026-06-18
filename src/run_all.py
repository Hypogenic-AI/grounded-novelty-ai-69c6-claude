"""One-command reproduction of the entire experiment.

    python src/run_all.py            # full run (N=5/cell, 245 ideas)
    python src/run_all.py --n 1      # quick pilot (49 ideas)

All LLM calls are cached to results/cache/, so a second run is free and exact.
"""
import argparse

import corpus
import generate
import judge
import metrics
import analyze
from llm import usage_summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5)
    args = ap.parse_args()

    print("[1/5] Building prior-work corpus (Semantic Scholar)...")
    corpus.build_corpus()
    print("[2/5] Generating ideas (7 conditions x 7 topics x N)...")
    generate.main(n_per_cell=args.n)
    print("[3/5] Computing objective metrics (embeddings on GPU)...")
    metrics.compute()
    print("[4/5] LLM-as-judge rubric + pairwise...")
    judge.main()
    print("[5/5] Statistics + figures...")
    analyze.main()
    print("\nDONE. Cumulative LLM usage:", usage_summary())


if __name__ == "__main__":
    main()
