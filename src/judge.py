"""LLM-as-judge evaluation: absolute rubric + pairwise vs the unguided control.

Two OFF-FAMILY judges (Claude-Sonnet-4.5, Gemini-2.5-Flash) score every idea on
the Si et al. 1-10 rubric, and compare each grounded idea against its matched
unguided idea (both orderings, to control position bias).
"""
import json
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import (GROUNDED_CONDITIONS, JUDGE_FILE, JUDGE_MAX_TOKENS,
                    JUDGE_MODELS, JUDGE_TEMPERATURE, PAIRWISE_FILE, SEED, TOPICS)
from llm import chat, extract_json
from metrics import load_ideas

RUBRIC = """You are reviewing a research idea about new prompting methods for LLMs.
Score it 1-10 on each dimension (use the full range; 10 is exceptional):
- novelty: how creative and different from existing published work.
- feasibility: can a student execute it in 1-2 months with limited GPU/API access.
- effectiveness: likelihood it actually beats strong baselines empirically.
- overall: 10=seminal (top 5%); 8=top 50%, major-conference accept; 6=borderline;
  4=clear reject; 2=critically flawed/trivial.
Respond with ONLY a JSON object: {"novelty":int,"feasibility":int,"effectiveness":int,"overall":int}."""

PAIRWISE = """You are comparing two research ideas (A and B) on the SAME topic, about new
prompting methods for LLMs. Judge which is better.
Respond with ONLY a JSON object:
{"more_novel":"A"|"B","better_overall":"A"|"B"}."""


def _fmt(idea):
    return (f"Title: {idea['title']}\nProblem: {idea['problem']}\n"
            f"Motivation: {idea['motivation']}\nMethod: {idea['method']}\n"
            f"Experiment plan: {idea['experiment_plan']}")


# ---------------------------------------------------------------- rubric ----
def score_idea(rec):
    out = {}
    for model, provider in JUDGE_MODELS:
        msg = [{"role": "user",
                "content": RUBRIC + "\n\nIDEA:\n" + _fmt(rec["idea"])}]
        try:
            raw = chat(msg, model=model, provider=provider,
                       temperature=JUDGE_TEMPERATURE, max_tokens=JUDGE_MAX_TOKENS,
                       json_mode=("gemini" in model or "gpt" in model))
            s = extract_json(raw)
            out[model] = {k: float(s[k]) for k in
                          ["novelty", "feasibility", "effectiveness", "overall"]}
        except Exception as e:  # noqa: BLE001
            out[model] = {"error": str(e)[:100]}
    return {"id": rec["id"], "topic": rec["topic"],
            "condition": rec["condition"], "rep": rec["rep"], "scores": out}


# -------------------------------------------------------------- pairwise ----
def compare_pair(grounded, control, judge_model, provider, flip):
    """One pairwise comparison. flip=True puts the grounded idea as B."""
    a, b = (control, grounded) if flip else (grounded, control)
    msg = [{"role": "user", "content":
            PAIRWISE + f"\n\nIDEA A:\n{_fmt(a['idea'])}\n\nIDEA B:\n{_fmt(b['idea'])}"}]
    raw = chat(msg, model=judge_model, provider=provider,
               temperature=JUDGE_TEMPERATURE, max_tokens=200,
               json_mode=("gemini" in judge_model or "gpt" in judge_model))
    s = extract_json(raw)
    grounded_label = "B" if flip else "A"
    return (1 if s.get("more_novel") == grounded_label else 0,
            1 if s.get("better_overall") == grounded_label else 0)


def run_pairwise(ideas):
    by = {(r["topic"], r["condition"], r["rep"]): r for r in ideas}
    jobs = []
    for topic in TOPICS:
        for cond in GROUNDED_CONDITIONS:
            for rep in range(max(r["rep"] for r in ideas) + 1):
                g = by.get((topic, cond, rep))
                c = by.get((topic, "unguided", rep))
                if g and c:
                    jobs.append((g, c))

    def one(g, c):
        nov_wins, ov_wins, n = 0, 0, 0
        for model, provider in JUDGE_MODELS:
            for flip in (False, True):  # both orderings -> position-bias control
                try:
                    nw, ow = compare_pair(g, c, model, provider, flip)
                    nov_wins += nw; ov_wins += ow; n += 1
                except Exception:
                    pass
        return {"topic": g["topic"], "condition": g["condition"], "rep": g["rep"],
                "n_comparisons": n,
                "novelty_winrate": nov_wins / n if n else None,
                "overall_winrate": ov_wins / n if n else None}

    results = []
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = [ex.submit(one, g, c) for g, c in jobs]
        for i, fut in enumerate(as_completed(futs), 1):
            results.append(fut.result())
            if i % 25 == 0:
                print(f"  pairwise {i}/{len(jobs)}")
    with open(PAIRWISE_FILE, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"Saved {len(results)} pairwise records to {PAIRWISE_FILE}")
    return results


def run_rubric(ideas):
    results = []
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = [ex.submit(score_idea, r) for r in ideas]
        for i, fut in enumerate(as_completed(futs), 1):
            results.append(fut.result())
            if i % 25 == 0:
                print(f"  rubric {i}/{len(ideas)}")
    results.sort(key=lambda x: x["id"])
    with open(JUDGE_FILE, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"Saved {len(results)} rubric records to {JUDGE_FILE}")
    return results


def main():
    random.seed(SEED)
    ideas = load_ideas()
    print(f"Judging {len(ideas)} ideas with {len(JUDGE_MODELS)} judges")
    run_rubric(ideas)
    run_pairwise(ideas)


if __name__ == "__main__":
    main()
