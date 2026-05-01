# Skill: Refine Bullet Point (XYZ Format)

## Overview
The XYZ bullet point framework, popularized by Laszlo Bock (former SVP of People Operations at Google) and the Harvard Business School career guides, structures every resume bullet around three components:

> **Accomplished [X] as measured by [Y], by doing [Z].**

- **X** — What you accomplished (the outcome or deliverable)
- **Y** — How you measure it (the metric that proves impact)
- **Z** — How you did it (the method, tool, or approach)

A resume bullet written without all three components is weaker. Most raw resume bullets state only Z (what they did) with no X or Y.

---

## The Three Components

### X — The Accomplishment
The outcome, deliverable, or result. This should be stated from the employer's perspective — what did they gain?

Weak X: "Worked on the backend API"
Strong X: "Reduced API response time by 60%"

Ask yourself: What changed because of my work? What was better after I did this?

### Y — The Measurement
The quantification that makes X credible and concrete. Numbers are always better than adjectives.

| Weak (adjective) | Strong (metric) |
|---|---|
| "significantly faster" | "3× faster (150ms → 50ms)" |
| "large number of users" | "12,000+ daily active users" |
| "major cost savings" | "saved $180K/year in infrastructure costs" |
| "improved accuracy" | "increased model precision from 82% to 94%" |

If you do not have an exact metric, use:
- Ranges: "reduced by 30–40%"
- Approximate scales: "10,000+ records/day", "across 5 engineering teams"
- Placeholders for the agent: `[X%]`, `[N users]`, `[~$Xk savings]`

**Never invent specific numbers.** Use placeholders if the metric is unknown — a hiring manager who asks "what was that X?" needs a real answer.

### Z — The Method
The specific action, tool, technique, or approach you used. This is where technical keywords naturally appear.

Weak Z: "used better code"
Strong Z: "by migrating from a monolithic Django app to microservices on Kubernetes with Helm charts"

Z is also where you demonstrate depth: not just "used machine learning" but "using a gradient-boosted ensemble (XGBoost + LightGBM) with SHAP-based feature selection".

---

## Full Formula Examples

### Before → After: Software Engineering

**Before**: "Worked on improving the search feature."

**After**: "Reduced search latency by 65% (800ms → 280ms) for 50,000+ daily queries by replacing a full-table SQL scan with an Elasticsearch index and adding query-time caching via Redis."

---

**Before**: "Helped migrate the system to the cloud."

**After**: "Cut infrastructure costs by $240K/year by leading the migration of 14 microservices from on-premise bare metal to AWS ECS Fargate, reducing deployment time from 45 minutes to under 8 minutes."

---

**Before**: "Wrote unit tests for the codebase."

**After**: "Increased test coverage from 34% to 87% across 3 services by building a pytest fixture library and integrating coverage reporting into the CI/CD pipeline (GitHub Actions), reducing production bug rate by ~40%."

---

### Before → After: Data Science / ML

**Before**: "Built a recommendation model."

**After**: "Improved product recommendation click-through rate by 23% by training a two-tower neural collaborative filtering model in PyTorch on 18 months of user interaction data (2.4M records)."

---

**Before**: "Cleaned data and ran analysis."

**After**: "Reduced data preprocessing time by 70% (6 hours → 1.8 hours per weekly batch) by building a reusable dbt pipeline that replaced manual Pandas scripts, improving analyst productivity across 4 teams."

---

### Before → After: Product Management

**Before**: "Worked with engineers to ship features."

**After**: "Shipped 3 high-impact features in Q3 on schedule (100% sprint completion rate) by introducing a structured PRD template and weekly cross-functional sync, reducing scope-creep incidents by 60%."

---

**Before**: "Improved user onboarding."

**After**: "Increased Day-7 user retention by 18 percentage points (41% → 59%) by redesigning the onboarding flow based on 200+ user interviews and 6 rounds of A/B testing across 12,000 users."

---

## Strong Action Verb List

Lead every bullet with a strong past-tense action verb. Never start with "Helped", "Assisted", "Worked on", or "Was responsible for" — these are passive and weak.

### Leadership & Management
Directed, Spearheaded, Championed, Orchestrated, Established, Founded, Launched, Scaled, Mentored, Coached, Cultivated, Recruited, Supervised, Delegated, Streamlined, Transformed, Consolidated, Unified, Prioritized, Allocated

### Delivery & Execution
Delivered, Shipped, Built, Implemented, Deployed, Engineered, Developed, Architected, Designed, Constructed, Created, Produced, Executed, Completed, Released, Automated, Optimized, Accelerated, Reduced, Eliminated

### Analysis & Research
Analyzed, Investigated, Evaluated, Assessed, Modeled, Researched, Identified, Diagnosed, Discovered, Mapped, Measured, Quantified, Benchmarked, Audited, Monitored, Forecasted, Predicted, Synthesized

### Communication & Collaboration
Presented, Published, Authored, Documented, Trained, Facilitated, Coordinated, Negotiated, Influenced, Advocated, Partnered, Aligned, Briefed, Communicated, Translated (technical concepts)

### Technical (Software/Data)
Architected, Refactored, Migrated, Integrated, Containerized, Instrumented, Profiled, Parallelized, Indexed, Abstracted, Modularized, Serialized, Orchestrated (pipelines), Trained (models), Fine-tuned, Productionized, Versioned

### Problem Solving & Improvement
Resolved, Debugged, Troubleshot, Diagnosed, Remediated, Patched, Fixed, Hardened, Secured, Mitigated, Prevented, Eliminated, Reduced (error rate / latency / cost)

---

## Bullet Point Quality Checklist

Before finalizing each bullet, verify:

- [ ] Starts with a strong past-tense action verb
- [ ] States the accomplishment (X), not just the task
- [ ] Includes a metric or quantified outcome (Y), or a clear placeholder
- [ ] Mentions the method, tool, or approach (Z)
- [ ] Does not start with "I", "We", or a pronoun
- [ ] Does not use weak verbs: "helped", "assisted", "worked on", "participated in", "was responsible for"
- [ ] Does not use vague adjectives without support: "significantly", "greatly", "highly"
- [ ] Is 1–2 lines (not longer)
- [ ] Contains at least one relevant keyword for the target role (naturally integrated, not stuffed)

---

## Tips for Quantification

When metrics are hard to find, try these strategies:

1. **Scale of system**: "serving X users", "processing X records/day", "across X teams/regions"
2. **Time saved**: "reduced from X hours to Y hours", "automated X hours/week of manual work"
3. **Cost**: "reduced infrastructure cost by $X", "saved $X/year in licensing fees"
4. **Quality improvement**: "reduced bug rate by X%", "increased test coverage from X% to Y%"
5. **Speed**: "reduced latency from Xms to Yms", "cut deployment time from X minutes to Y minutes"
6. **Adoption**: "adopted by X teams", "used by X+ engineers across the organization"
7. **Revenue/growth proxy**: "contributed to X% revenue growth", "part of a product used by X paying customers"

If none of these apply, describe the scope of responsibility to give context even without a hard number:
> "Led the backend architecture for the company's highest-traffic service (peak: ~50K req/min)."
