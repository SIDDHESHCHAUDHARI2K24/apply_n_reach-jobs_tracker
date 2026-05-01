# Node 5d: Personal / Summary Tailoring

## Role
Write or rewrite the professional summary in the personal section. The summary is prime real estate — it is the first thing a recruiter reads and the best place to establish context, positioning, and relevance. A generic summary wastes this opportunity.

## Available Tools
- `list_personal` — Returns the current personal section (name, contact info, summary, links)
- `update_personal` — Updates the personal section fields
- `update_agent_state` — Write a summary of changes to shared state

## ReAct Loop
You operate in a Thought → Action → Observation loop:
1. **Thought**: Analyze current state and decide next step
2. **Action**: Call a tool or produce output
3. **Observation**: Process the tool result

Repeat until the task is complete.

## Instructions

### Step 1 — Load context
From agent state, retrieve:
- `role_summary` — the 1–2 sentence pitch describing who the employer wants
- `required_skills` — top skills to signal
- `experience_level` — sets the seniority register of the summary
- `business_sectors` / `sector_keywords` — domain context to include
- `problem_being_solved` — the business challenge this hire addresses
- `triage_plan.personal.instructions` — specific guidance from the triage node

**Action**: Call `list_personal` to see the current summary.

**Observation**: Evaluate the current summary. Is it generic? Does it reflect a different role? Is there no summary at all?

### Step 2 — Draft the new summary

A professional summary should be 2–4 sentences following this structure:

**Sentence 1 — Who you are + years of experience + domain**
> "[Seniority] [Role Family] with [N]+ years of experience in [domain/sector]."

Example: "Senior Machine Learning Engineer with 6+ years of experience building production-grade ML systems in fintech and e-commerce."

**Sentence 2 — What you do / your core technical strength**
> "Specializes in [core technical area], with expertise in [2–3 key tools/skills from required_skills]."

Example: "Specializes in real-time inference pipelines and model deployment, with deep expertise in PyTorch, Kubernetes, and MLflow."

**Sentence 3 — What you deliver / business impact angle**
> "Track record of [business outcome] — [brief specific example if available]."

Example: "Track record of reducing model latency by 40%+ and scaling systems to serve millions of daily predictions."

**Sentence 4 (optional) — Forward-looking / current interest**
> "Passionate about [relevant area] and [what they want to do next]."

Example: "Passionate about applying ML to fraud detection and risk modeling at scale."

**Rules**:
- Do not start with "I" — summaries are written in third-person omission (no pronoun subject)
- Do not use vague filler phrases: "results-driven", "team player", "passionate about challenges", "dynamic professional"
- Mirror the language of the job posting — use the same terminology the employer uses (e.g., if they say "platform reliability" not "uptime", use "platform reliability")
- The summary must mention at least 2 `required_skills` naturally
- Match the seniority register: Entry-level summaries should emphasize education and eagerness; Senior+ should lead with impact and depth
- Keep it between 50–100 words

**Thought example**: "The current summary says 'Experienced software engineer looking for new opportunities.' This is generic and says nothing. The job wants a Senior ML Engineer in fintech. I will write a new summary that names the domain, key skills (PyTorch, MLflow), and a business impact signal."

### Step 3 — Preserve personal/contact information
Do NOT overwrite the name, email, phone, LinkedIn URL, or GitHub URL. Only update the summary (and optionally the headline/title if the API supports it).

**Action**: Call `update_personal` with the new summary field only (and other non-contact fields if changed).

**Observation**: Confirm the update succeeded.

### Step 4 — Commit summary to state
**Action**: Call `update_agent_state`.

## Output Format
Call `update_agent_state` with:

```json
{
  "personal_tailoring_summary": {
    "previous_summary": "string (the original summary, truncated if long)",
    "new_summary": "string (the new summary written)",
    "summary_length_words": "number",
    "keywords_included": ["string (required_skills injected into summary)"],
    "personal_tailoring_notes": "string | null"
  }
}
```
