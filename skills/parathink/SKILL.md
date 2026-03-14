---
name: parathink
version: 1.0.0
description: "ParaThinker: Parallel reasoning strategy for complex problem solving."
metadata:
  openclaw:
    category: "reasoning"
---

# ParaThinker

A reasoning strategy that improves answer quality by generating multiple independent reasoning paths in parallel and synthesizing them into a final answer.

Instead of relying on a single chain-of-thought, ParaThinker explores diverse reasoning approaches simultaneously, reducing tunnel vision and improving robustness. This scales test-time compute **horizontally** (width) rather than only vertically (depth).

## When to Use

**Activate ParaThinker for:**
- Complex reasoning tasks
- Ambiguous questions
- Strategic planning
- Technical problem solving
- Coding architecture decisions
- Research analysis
- Multi-step math or logic
- Competing hypotheses

**Skip for:**
- Trivial questions
- Simple lookups
- Short factual answers

## Workflow

### Step 1 — Problem Framing

Clarify the task. Identify:
- **Objective** — what outcome is required
- **Constraints** — hard limits or boundaries
- **Known information** — available facts and context
- **Unknown variables** — gaps that must be reasoned through or assumed

### Step 2 — Parallel Reasoning Generation

Generate 3–5 independent reasoning paths. Each path must:
- Use a **different perspective** or strategy
- Apply **different assumptions** where applicable
- Remain **logically coherent** on its own

Example reasoning styles:

| Style | Description |
|-------|-------------|
| Analytical | Break the problem into components and reason from structure |
| Heuristic | Apply rules of thumb and pattern recognition |
| Probabilistic | Reason from likelihoods, base rates, and expected outcomes |
| First-principles | Derive conclusions from fundamental truths without analogy |
| Analogical | Map the problem onto a known domain and transfer insights |

> Each path must be generated **independently** to avoid anchoring bias.

### Step 3 — Evaluate Each Path

Assess every reasoning path against:
- Logical consistency
- Completeness
- Assumption validity
- Evidence strength
- Likelihood of correctness

Rank the paths by overall quality.

### Step 4 — Cross-Path Synthesis

- Combine the strongest ideas from the top-ranked paths.
- Resolve any conflicts between paths.
- Produce a unified reasoning model incorporating the most reliable components.

### Step 5 — Final Answer

Deliver:
- A **clear conclusion**
- A **concise explanation**
- A brief **reasoning summary**

Avoid exposing unnecessary internal reasoning unless the user explicitly requests it.

## Example

**Question:** "Should we migrate our monolith to microservices?"

| Path | Style | Summary |
|------|-------|---------|
| Path A | Analytical | Decompose coupling, team size, deployment needs |
| Path B | First-principles | What problem does the architecture actually solve? |
| Path C | Probabilistic | What is the historical success rate of migrations at this scale? |
| Path D | Analogical | What did similar companies do, and what were the outcomes? |

**Synthesis:** Paths A and B converge on team autonomy as the key driver. Path C flags high migration risk. Path D suggests a strangler-fig pattern as a lower-risk migration approach.

**Answer:** Migrate incrementally using the strangler-fig pattern, starting with the highest-friction service boundaries.
