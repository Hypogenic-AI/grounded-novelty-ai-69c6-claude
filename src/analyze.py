"""Phase 3/5: statistics, hypothesis tests, and figures.

Builds a per-idea table (objective LGN + judge rubric + diversity + pairwise),
fits mixed-effects models with topic as a random intercept, computes effect
sizes with Holm correction, validates the judge (inter-judge agreement +
convergent validity vs the objective metric), and renders all figures.
"""
import json
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

from config import (CONDITIONS, FIGURES, GROUNDED_CONDITIONS, JUDGE_FILE,
                    JUDGE_MODELS, LGN_FILE, PAIRWISE_FILE, RESULTS)

warnings.filterwarnings("ignore")
ORDER = CONDITIONS
COLORS = {c: ("#888888" if c == "unguided" else None) for c in CONDITIONS}


# --------------------------------------------------------------- load ------
def build_table():
    obj = json.load(open(LGN_FILE))
    per_idea = {r["id"]: r for r in obj["per_idea"]}
    rub = [json.loads(l) for l in open(JUDGE_FILE)]
    rows = []
    for r in rub:
        pi = per_idea[r["id"]]
        # average rubric across judges (skip errored judges)
        dims = {"novelty": [], "feasibility": [], "effectiveness": [], "overall": []}
        perjudge = {}
        for m, s in r["scores"].items():
            if "error" in s:
                continue
            for k in dims:
                dims[k].append(s[k])
            perjudge[m] = s
        row = {
            "id": r["id"], "topic": r["topic"], "condition": r["condition"],
            "rep": r["rep"], "n_words": pi["n_words"],
            "lgn": pi["lgn"], "lgn_top5": pi["lgn_top5"],
        }
        for k in dims:
            row["j_" + k] = np.mean(dims[k]) if dims[k] else np.nan
        # keep per-judge novelty for inter-judge agreement
        for i, (m, _) in enumerate(JUDGE_MODELS):
            row[f"nov_judge{i}"] = perjudge.get(m, {}).get("novelty", np.nan)
        rows.append(row)
    df = pd.DataFrame(rows)
    df["condition"] = pd.Categorical(df["condition"], categories=ORDER)
    return df, obj


# ---------------------------------------------------- mixed-effects test ---
def mixed_effects(df, metric, covariate=False):
    """metric ~ C(condition, ref=unguided) + (1|topic); return per-condition stats."""
    f = f"{metric} ~ C(condition, Treatment('unguided'))"
    if covariate:
        f += " + n_words"
    md = smf.mixedlm(f, df, groups=df["topic"])
    res = md.fit(reml=False)
    out = {}
    for cond in GROUNDED_CONDITIONS:
        name = f"C(condition, Treatment('unguided'))[T.{cond}]"
        if name in res.params.index:
            ci = res.conf_int().loc[name]
            out[cond] = {"coef": float(res.params[name]),
                         "ci_low": float(ci[0]), "ci_high": float(ci[1]),
                         "p": float(res.pvalues[name])}
    return out, res


def holm(pvals):
    """Holm-Bonferroni adjusted p-values for a dict {key: p}."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj, prev = {}, 0.0
    for i, (k, p) in enumerate(items):
        a = min(1.0, (m - i) * p)
        a = max(a, prev)
        adj[k], prev = a, a
    return adj


def cohens_d(a, b):
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1))
                 / (na + nb - 2))
    return (np.mean(a) - np.mean(b)) / sp if sp > 0 else 0.0


# ------------------------------------------------------------- pairwise ----
def pairwise_summary():
    pw = [json.loads(l) for l in open(PAIRWISE_FILE)]
    df = pd.DataFrame(pw)
    out = {}
    for cond in GROUNDED_CONDITIONS:
        sub = df[df["condition"] == cond]
        for metric in ["novelty_winrate", "overall_winrate"]:
            vals = sub[metric].dropna().values
            # bootstrap CI on the mean win-rate
            boot = [np.mean(np.random.choice(vals, len(vals), replace=True))
                    for _ in range(2000)]
            # one-sample t-test of the per-record win-rates against chance (0.5)
            p = float(stats.ttest_1samp(vals, 0.5).pvalue) if len(vals) > 1 else np.nan
            out[f"{cond}__{metric}"] = {
                "mean": float(np.mean(vals)),
                "ci_low": float(np.percentile(boot, 2.5)),
                "ci_high": float(np.percentile(boot, 97.5)),
                "p_vs_chance": p, "n": int(len(vals)),
            }
    return df, out


# ------------------------------------------------------------ figures ------
def bar(ax, means, errs, title, ylabel, ref_line=None):
    x = range(len(ORDER))
    colors = ["#999999" if c == "unguided" else "#3b78b5" for c in ORDER]
    ax.bar(x, [means[c] for c in ORDER],
           yerr=[errs[c] for c in ORDER], capsize=3, color=colors)
    ax.set_xticks(list(x))
    ax.set_xticklabels([c.replace("_", "\n") for c in ORDER], rotation=0, fontsize=7)
    ax.set_title(title, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=8)
    if ref_line is not None:
        ax.axhline(ref_line, ls="--", color="red", lw=1)


def make_figures(df, obj, pw_df):
    # Fig 1: objective LGN
    fig, ax = plt.subplots(figsize=(7, 3.5))
    means = df.groupby("condition")["lgn"].mean().to_dict()
    errs = (df.groupby("condition")["lgn"].sem() * 1.96).to_dict()
    bar(ax, means, errs, "Literature-Grounded Novelty (objective, embedding distance)",
        "1 - max cosine sim to prior work", ref_line=means["unguided"])
    fig.tight_layout(); fig.savefig(f"{FIGURES}/fig1_lgn.png", dpi=140); plt.close(fig)

    # Fig 2: judge novelty & feasibility
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
    for ax, m, lab in [(axes[0], "j_novelty", "Judge novelty (1-10)"),
                       (axes[1], "j_feasibility", "Judge feasibility (1-10)")]:
        mean = df.groupby("condition")[m].mean().to_dict()
        err = (df.groupby("condition")[m].sem() * 1.96).to_dict()
        bar(ax, mean, err, lab, lab, ref_line=mean["unguided"])
    fig.tight_layout(); fig.savefig(f"{FIGURES}/fig2_judge_rubric.png", dpi=140); plt.close(fig)

    # Fig 3: novelty-feasibility tradeoff (condition means)
    fig, ax = plt.subplots(figsize=(6, 5))
    for c in ORDER:
        sub = df[df["condition"] == c]
        ax.scatter(sub["j_feasibility"].mean(), sub["j_novelty"].mean(),
                   s=120, color=("#999999" if c == "unguided" else "#3b78b5"))
        ax.annotate(c, (sub["j_feasibility"].mean(), sub["j_novelty"].mean()),
                    fontsize=8, xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel("Feasibility (judge, 1-10)"); ax.set_ylabel("Novelty (judge, 1-10)")
    ax.set_title("Novelty-Feasibility trade-off by grounding")
    fig.tight_layout(); fig.savefig(f"{FIGURES}/fig3_tradeoff.png", dpi=140); plt.close(fig)

    # Fig 4: pairwise overall win-rate vs unguided
    fig, ax = plt.subplots(figsize=(7, 3.5))
    gm = pw_df.groupby("condition")["overall_winrate"].mean()
    ge = pw_df.groupby("condition")["overall_winrate"].sem() * 1.96
    conds = [c for c in GROUNDED_CONDITIONS]
    colors = ["#3b78b5"] * len(conds)
    ax.bar(range(len(conds)), [gm[c] for c in conds],
           yerr=[ge[c] for c in conds], capsize=3, color=colors)
    ax.axhline(0.5, ls="--", color="red", lw=1)
    ax.set_xticks(range(len(conds)))
    ax.set_xticklabels([c.replace("_", "\n") for c in conds], fontsize=7)
    ax.set_ylabel("P(grounded > unguided)"); ax.set_ylim(0, 1)
    ax.set_title("Pairwise overall win-rate vs unguided control (2 judges, both orders)")
    fig.tight_layout(); fig.savefig(f"{FIGURES}/fig4_pairwise.png", dpi=140); plt.close(fig)

    # Fig 5: set-level diversity
    fig, ax = plt.subplots(figsize=(7, 3.5))
    cd = obj["cond_diversity"]
    div = {c: cd[c]["mean_pairwise_distance"] for c in ORDER}
    bar(ax, div, {c: 0 for c in ORDER}, "Set-level diversity (mean pairwise distance)",
        "diversity", ref_line=div["unguided"])
    fig.tight_layout(); fig.savefig(f"{FIGURES}/fig5_diversity.png", dpi=140); plt.close(fig)

    # Fig 6: convergent validity (judge novelty vs objective LGN)
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ax.scatter(df["lgn"], df["j_novelty"], alpha=0.4, s=18)
    r, p = stats.spearmanr(df["lgn"], df["j_novelty"])
    ax.set_xlabel("Objective LGN (embedding distance)")
    ax.set_ylabel("Judge novelty (1-10)")
    ax.set_title(f"Convergent validity: Spearman r={r:.2f} (p={p:.1e})")
    fig.tight_layout(); fig.savefig(f"{FIGURES}/fig6_convergent.png", dpi=140); plt.close(fig)


# --------------------------------------------------------------- main ------
def main():
    df, obj = build_table()
    df.to_csv(f"{RESULTS}/per_idea_table.csv", index=False)
    summary = {"n_ideas": len(df), "metrics": {}}

    # Mixed-effects for each continuous metric
    for metric in ["lgn", "j_novelty", "j_feasibility", "j_effectiveness", "j_overall"]:
        res, _ = mixed_effects(df, metric)
        res_cov, _ = mixed_effects(df, metric, covariate=True)
        pvals = {c: res[c]["p"] for c in res}
        adj = holm(pvals)
        base = df[df["condition"] == "unguided"][metric].dropna().values
        for c in res:
            sub = df[df["condition"] == c][metric].dropna().values
            res[c]["holm_p"] = adj[c]
            res[c]["cohens_d"] = float(cohens_d(sub, base))
            res[c]["mean"] = float(np.mean(sub))
            res[c]["p_with_length_covariate"] = res_cov.get(c, {}).get("p", np.nan)
        summary["metrics"][metric] = {
            "unguided_mean": float(np.mean(base)),
            "conditions": res,
        }

    # Pairwise
    pw_df, pw = pairwise_summary()
    summary["pairwise"] = pw

    # Diversity
    summary["diversity"] = obj["cond_diversity"]

    # Judge validation
    ij = stats.spearmanr(df["nov_judge0"], df["nov_judge1"], nan_policy="omit")
    cv_lgn = stats.spearmanr(df["lgn"], df["j_novelty"], nan_policy="omit")
    cv_lgn5 = stats.spearmanr(df["lgn_top5"], df["j_novelty"], nan_policy="omit")
    summary["judge_validation"] = {
        "inter_judge_novelty_spearman": float(ij.statistic),
        "inter_judge_novelty_p": float(ij.pvalue),
        "convergent_validity_lgn_vs_judgenov_spearman": float(cv_lgn.statistic),
        "convergent_validity_p": float(cv_lgn.pvalue),
        "convergent_validity_lgntop5_spearman": float(cv_lgn5.statistic),
    }

    with open(f"{RESULTS}/analysis_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    make_figures(df, obj, pw_df)

    # ---- console report ----
    print(f"\n=== N={len(df)} ideas ===")
    for metric in ["lgn", "j_novelty", "j_feasibility", "j_overall"]:
        m = summary["metrics"][metric]
        print(f"\n{metric}  (unguided mean={m['unguided_mean']:.3f})")
        for c in GROUNDED_CONDITIONS:
            r = m["conditions"][c]
            sig = "*" if r["holm_p"] < 0.05 else " "
            print(f"  {c:22s} mean={r['mean']:.3f} d={r['cohens_d']:+.2f} "
                  f"coef={r['coef']:+.3f} p={r['p']:.3f} holm={r['holm_p']:.3f}{sig}")
    print("\nPairwise overall win-rate vs unguided:")
    for c in GROUNDED_CONDITIONS:
        r = pw[f"{c}__overall_winrate"]
        print(f"  {c:22s} {r['mean']:.2f} [{r['ci_low']:.2f},{r['ci_high']:.2f}] p={r['p_vs_chance']:.3f}")
    jv = summary["judge_validation"]
    print(f"\nInter-judge novelty Spearman: {jv['inter_judge_novelty_spearman']:.3f} "
          f"(p={jv['inter_judge_novelty_p']:.1e})")
    print(f"Convergent validity (LGN vs judge novelty) Spearman: "
          f"{jv['convergent_validity_lgn_vs_judgenov_spearman']:.3f} "
          f"(p={jv['convergent_validity_p']:.1e})")
    print(f"\nSaved analysis_summary.json + 6 figures")


if __name__ == "__main__":
    main()
