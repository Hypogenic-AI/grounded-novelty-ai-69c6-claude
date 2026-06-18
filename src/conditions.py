"""The seven experimental conditions (grounding scaffolds).

CRITICAL DESIGN CONTROL: every condition ends by emitting the *same* standardized
idea JSON. Only the reasoning scaffold that precedes the idea differs. This
isolates the grounding mechanism from output-format / length confounds.
"""

# Shared, verbatim across ALL conditions — the only thing the metrics see.
OUTPUT_SCHEMA = """
When you are done, output ONLY a JSON object (no prose outside it) with EXACTLY these keys:
{
  "title": "<concise paper title>",
  "problem": "<1-2 sentences: the specific problem>",
  "motivation": "<2-3 sentences: why it matters and why now>",
  "method": "<3-5 sentences: the concrete proposed prompting method>",
  "experiment_plan": "<2-4 sentences: datasets, baselines, and metrics to test it>"
}
Keep the total idea concise (target 150-250 words across all fields). Do not add commentary.
"""

SYSTEM = (
    "You are an expert NLP/ML researcher generating a research idea about new "
    "prompting methods for large language models. Be specific and technical."
)


def _topic_line(topic_desc):
    return f"Research topic: {topic_desc}."


def build_messages(condition, topic_desc, prior_work=None):
    """Return chat `messages` for one (condition, topic) generation call.

    prior_work: optional list of "Title — abstract" strings (literature_comparison).
    """
    t = _topic_line(topic_desc)

    if condition == "unguided":
        user = (
            f"{t}\n\nPropose ONE novel research idea on this topic.\n{OUTPUT_SCHEMA}"
        )

    elif condition == "deduction":
        user = (
            f"{t}\n\nGround your idea through DEDUCTION using the Bit-Flip-Spark schema:\n"
            "1. BIT: State the prevailing assumption or conventional wisdom underlying current "
            "work on this topic.\n"
            "2. FLIP: Identify a specific, defensible way to invert or challenge that assumption.\n"
            "3. SPARK: Deduce the concrete research idea that follows from the flip.\n"
            "Work through steps 1-3 explicitly, then derive the idea.\n" + OUTPUT_SCHEMA
        )

    elif condition == "induction":
        user = (
            f"{t}\n\nGround your idea through INDUCTION:\n"
            "1. List 4-6 concrete, specific empirical observations or known findings about LLM "
            "behavior relevant to this topic.\n"
            "2. Induce a general hypothesis that best explains these observations.\n"
            "3. From that hypothesis, derive a novel prompting-method idea.\n"
            "Work through steps 1-3 explicitly, then derive the idea.\n" + OUTPUT_SCHEMA
        )

    elif condition == "proposal_writing":
        user = (
            f"{t}\n\nGround your idea through PROPOSAL WRITING:\n"
            "First draft a brief but complete research proposal sketch (problem, the precise "
            "mechanism of the proposed method, the strongest baseline it must beat, and the single "
            "experiment that would most convincingly validate it). Pressure-test it for specificity "
            "and feasibility. Then distill it into the final idea.\n"
            "Work through the proposal explicitly, then output the idea.\n" + OUTPUT_SCHEMA
        )

    elif condition == "outcome_imagination":
        user = (
            f"{t}\n\nGround your idea through OUTCOME IMAGINATION:\n"
            "1. Imagine the single most exciting yet still-plausible empirical result a paper on "
            "this topic could report.\n"
            "2. State which widely-held belief that result would overturn (the 'surprise').\n"
            "3. Working backwards, derive the prompting-method idea whose success would produce "
            "exactly that surprising-but-plausible result.\n"
            "Work through steps 1-3 explicitly, then derive the idea.\n" + OUTPUT_SCHEMA
        )

    elif condition == "literature_comparison":
        refs = ""
        if prior_work:
            refs = "\n\nEXISTING PRIOR WORK on this topic (be meaningfully different from ALL of it):\n"
            for i, pw in enumerate(prior_work, 1):
                refs += f"[{i}] {pw}\n"
        user = (
            f"{t}{refs}\n\nGround your idea through LITERATURE COMPARISON:\n"
            "1. Draft a candidate idea.\n"
            "2. Explicitly compare it against each piece of prior work above; identify any overlap.\n"
            "3. Revise the idea until it is clearly distinct from all prior work while remaining "
            "feasible.\n"
            "Work through steps 1-3 explicitly, then output the final revised idea.\n" + OUTPUT_SCHEMA
        )

    elif condition == "small_experiment":
        user = (
            f"{t}\n\nGround your idea through a SMALL EXPERIMENT (thought experiment):\n"
            "1. Draft a candidate idea.\n"
            "2. Design the smallest decisive test that could falsify its core assumption, and "
            "predict the most likely outcome of that test based on what you know about LLMs.\n"
            "3. Critique the idea in light of that predicted outcome and revise it to be more "
            "robust and novel.\n"
            "Work through steps 1-3 explicitly, then output the final revised idea.\n" + OUTPUT_SCHEMA
        )
    else:
        raise ValueError(f"unknown condition {condition}")

    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
    ]
