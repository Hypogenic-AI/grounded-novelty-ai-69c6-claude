export const meta = {
  name: 'extract-paper-notes',
  description: 'Read each downloaded paper PDF and extract structured research notes for a literature review on grounded-novelty scientific idea generation',
  phases: [{ title: 'Read', detail: 'one agent per paper PDF' }],
}

const PAPERS = [
 {title:"Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers",file:"papers/2409.04109_can_llms_generate_novel_research_ideas_a_large-scale_hu.pdf",arxiv:"2409.04109v1",pages:94,deep:true,abstract:"Head-to-head comparison of 100+ expert NLP researchers vs an LLM ideation agent; blind reviews. LLM ideas judged more novel (p<0.05) but slightly weaker on feasibility. Identifies failures of LLM self-evaluation and lack of diversity in generation."},
 {title:"SciMON: Scientific Inspiration Machines Optimized for Novelty",file:"papers/2305.14259_scimon_scientific_inspiration_machines_optimized_for_no.pdf",arxiv:"2305.14259v7",pages:21,deep:true,abstract:"Retrieval of inspirations from past papers; explicitly optimizes novelty by ITERATIVELY COMPARING to prior papers and updating until novel enough. Background context -> natural language ideas grounded in literature. Datasets from ACL Anthology + biomedical (link prediction)."},
 {title:"Large Language Models for Automated Open-domain Scientific Hypotheses Discovery (MOOSE)",file:"papers/2309.02726_large_language_models_for_automated_open-domain_scienti.pdf",arxiv:"2309.02726v3",pages:21,deep:true,abstract:"Hypothetical INDUCTION from raw web corpus to novel+valid social science hypotheses. First dataset for social science academic hypotheses discovery. Multi-module framework with three feedback mechanisms (present/past/future feedback)."},
 {title:"Can Large Language Models Unlock Novel Scientific Research Ideas?",file:"papers/2409.06185_can_large_language_models_unlock_novel_scientific_resea.pdf",arxiv:"2409.06185v2",pages:25,deep:false,abstract:"Generates future research ideas from papers; proposes Idea Alignment Score (IAScore) and Idea Distinctness Index; human eval of novelty/relevance/feasibility; releases datasets and code."},
 {title:"IdeaBench: Benchmarking Large Language Models for Research Idea Generation",file:"papers/2411.02429_ideabench_benchmarking_large_language_models_for_resear.pdf",arxiv:"2411.02429v1",pages:44,deep:false,abstract:"Benchmark dataset (titles+abstracts of influential papers + references) and two-stage GPT-4o evaluation with Insight Score for novelty/feasibility. Profiles LLMs as domain researchers."},
 {title:"Learning to Generate Research Idea with Dynamic Control",file:"papers/2412.14626_learning_to_generate_research_idea_with_dynamic_control.pdf",arxiv:"2412.14626v2",pages:21,deep:false,abstract:"Two-stage SFT + controllable RL with multi-dimensional reward models (novelty, feasibility, effectiveness); dimensional controllers steer generation at inference; balances trade-offs."},
 {title:"AutoDiscovery: Open-ended Scientific Discovery via Bayesian Surprise",file:"papers/2507.00310_autodiscovery_open-ended_scientific_discovery_via_bayes.pdf",arxiv:"2507.00310v3",pages:37,deep:false,abstract:"Open-ended ASD driven by BAYESIAN SURPRISE (epistemic shift prior->posterior after running experiments); MCTS with progressive widening, surprisal reward; 21 real-world datasets across biology/economics/finance/behavioral science."},
 {title:"A Survey on Hypothesis Generation for Scientific Discovery in the Era of Large Language Models",file:"papers/2504.05496_a_survey_on_hypothesis_generation_for_scientific_discov.pdf",arxiv:"2504.05496v1",pages:11,deep:false,abstract:"Survey + taxonomy of LLM hypothesis-generation methods; novelty boosting, structured reasoning; evaluation strategies; challenges."},
 {title:"Large Language Models for Scientific Idea Generation: A Creativity-Centered Survey",file:"papers/2511.07448_large_language_models_for_scientific_idea_generation_a_.pdf",arxiv:"2511.07448v2",pages:75,deep:false,abstract:"Survey organizing methods into 5 families: external knowledge augmentation, prompt-based distributional steering, inference-time scaling, multi-agent collaboration, parameter-level adaptation; uses Boden + Rhodes 4Ps creativity frameworks; maps novelty vs validity trade-offs."},
 {title:"HypoSpace: Evaluating LLM Creativity as Set-Valued Hypothesis Generators under Underdetermination",file:"papers/2510.15614_hypospace_evaluating_llm_creativity_as_set-valued_hypot.pdf",arxiv:"2510.15614v3",pages:15,deep:false,abstract:"Evaluates LLMs as set-valued hypothesis generators under underdetermination; measures diversity/coverage/validity of hypothesis sets rather than single-shot novelty."},
 {title:"Automating psychological hypothesis generation with AI causal graph",file:"papers/2402.14424_automating_psychological_hypothesis_generation_with_ai_.pdf",arxiv:"2402.14424v3",pages:14,deep:false,abstract:"Causal knowledge graph from 43,312 psychology articles + LLM; link prediction generates 130 hypotheses on well-being; LLM+graph matches expert novelty, beats LLM-only (p<0.01)."},
 {title:"Chain of Ideas: Revolutionizing Research Via Novel Idea Development with LLM Agents",file:"papers/2410.13185_chain_of_ideas_revolutionizing_research_via_novel_idea_.pdf",arxiv:"2410.13185v5",pages:30,deep:false,abstract:"CoI agent organizes literature in a CHAIN structure mirroring progressive development of a domain; Idea Arena evaluation protocol; comparable to humans; ~$0.50/idea. Code available."},
 {title:"Many Heads Are Better Than One: Improved Scientific Idea Generation by A LLM-Based Multi-Agent System (VirSci)",file:"papers/2410.09403_many_heads_are_better_than_one_improved_scientific_idea.pdf",arxiv:"2410.09403v4",pages:40,deep:false,abstract:"VirSci multi-agent system mimicking research teams to generate/evaluate/refine ideas; outperforms SOTA on novelty; code at github.com/open-sciencelab/Virtual-Scientists."},
 {title:"Nova: An Iterative Planning and Search Approach to Enhance Novelty and Diversity of LLM Generated Ideas",file:"papers/2410.14255_nova_an_iterative_planning_and_search_approach_to_enhan.pdf",arxiv:"2410.14255v2",pages:44,deep:false,abstract:"Iterative PLANNED RETRIEVAL of external knowledge to enrich ideation; 3.4x more unique novel ideas; Swiss Tournament evaluation over 170 seed papers; 2.5x more top-rated ideas vs SOTA."},
 {title:"Sparks of Science: Hypothesis Generation Using Structured Paper Data (HypoGen)",file:"papers/2504.12976_sparks_of_science_hypothesis_generation_using_structure.pdf",arxiv:"2504.12976v1",pages:19,deep:false,abstract:"HypoGen dataset ~5500 problem-hypothesis pairs with Bit-Flip-Spark schema + explicit Chain-of-Reasoning; fine-tune on Bit-Flip-Spark improves novelty/feasibility. HF: huggingface.co/datasets/UniverseTBD/hypogen-dr1."},
 {title:"All That Glitters is Not Novel: Plagiarism in AI Generated Research",file:"papers/2502.16487_all_that_glitters_is_not_novel_plagiarism_in_ai_generat.pdf",arxiv:"2502.16487v3",pages:18,deep:false,abstract:"13 experts find 24% of 50 LLM-generated research docs paraphrased/borrowed; automated plagiarism detectors inadequate; strong caution on ungrounded novelty claims."},
 {title:"Deep Ideation: Designing LLM Agents to Generate Novel Research Ideas on Scientific Concept Network",file:"papers/2511.02238_deep_ideation_designing_llm_agents_to_generate_novel_re.pdf",arxiv:"2511.02238v1",pages:23,deep:false,abstract:"Scientific concept network (keyword co-occurrence + contextual relations); explore-expand-evolve workflow with Idea Stack; critic engine trained on real reviewer feedback; +10.67% idea quality. Code: github.com/kyZhao-1/Deep-Ideation."},
 {title:"On the Limits of LLM-as-Judge for Scientific Novelty Assessment",file:"papers/2606.12071_on_the_limits_of_llm-as-judge_for_scientific_novelty_as.pdf",arxiv:"2606.12071v1",pages:45,deep:false,abstract:"RQ-Bench from recent arXiv papers; author-anchored reference research questions; LLM judges show a NOVELTY MIRAGE (rate model RQs highly novel) while experts prefer reference RQs; warns LLM-as-judge unreliable for novelty assessment."},
]

const NOTE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['arxiv','one_liner','problem','method','grounding_mechanisms','grounding_notes','datasets','baselines','metrics','key_results','code_links','relevance_to_hypothesis','limitations'],
  properties: {
    arxiv: { type: 'string' },
    one_liner: { type: 'string' },
    problem: { type: 'string' },
    method: { type: 'string' },
    grounding_mechanisms: { type: 'array', items: { type: 'string', enum: ['deduction','induction','proposal_writing','outcome_imagination','small_experiments','literature_comparison','none_unguided','other'] } },
    grounding_notes: { type: 'string' },
    datasets: { type: 'array', items: { type: 'string' } },
    baselines: { type: 'array', items: { type: 'string' } },
    metrics: { type: 'array', items: { type: 'string' } },
    key_results: { type: 'string' },
    code_links: { type: 'array', items: { type: 'string' } },
    relevance_to_hypothesis: { type: 'string' },
    limitations: { type: 'string' },
  },
}

const HYP = 'HYPOTHESIS UNDER STUDY: LLMs generate higher quality scientific ideas when novelty is grounded through deduction, induction, proposal writing, outcome imagination, small experiments, or literature comparison, vs. unguided generation.'

const notes = await pipeline(
  PAPERS,
  (p) => {
    const readPlan = p.deep
      ? `This is a FOUNDATIONAL paper — read it deeply. The Read tool reads PDFs via a pages param (max 20 pages/request). Read pages 1-15 of "${p.file}", then continue into the methods and experiments/results sections (the paper has ${p.pages} pages). Capture exact dataset names/sizes, baseline names, metric definitions (especially how novelty is operationalized), and numeric results.`
      : `Read the PDF at "${p.file}" focusing on abstract, intro, method, and experiments/results. The Read tool reads PDFs via a pages param (max 20 pages/req); the paper has ${p.pages} pages. Read the first ~12 pages and skim the experiments/results section — you do NOT need every page.`
    return agent(
      `${HYP}\n\nExtract structured notes for a literature review. Paper: "${p.title}" (arXiv ${p.arxiv}).\nKnown summary: ${p.abstract}\n\n${readPlan}\n\nBe concrete and faithful: include exact dataset names+sizes, HuggingFace/GitHub links, baseline names, and metric definitions where stated. For grounding_mechanisms, map the paper's techniques onto the hypothesis vocabulary: retrieval + novelty-comparison-to-prior-papers => literature_comparison; running experiments / using empirical feedback => small_experiments; observations->hypothesis => induction; theory/assumptions->prediction (e.g. Bit-Flip) => deduction; writing full proposals/plans => proposal_writing; imagining outcomes / Bayesian surprise / predicting results => outcome_imagination; plain prompting with no grounding => none_unguided.`,
      { label: `read:${p.arxiv}`, phase: 'Read', schema: NOTE_SCHEMA, agentType: 'Explore' }
    ).then(n => ({ ...n, title: p.title, file: p.file, pages: p.pages, deep: p.deep }))
  }
)

return notes.filter(Boolean)
