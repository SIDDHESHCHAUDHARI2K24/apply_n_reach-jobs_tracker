# Node 3: Resume Snapshot

## Role
Create a working copy of the resume for this job application by snapshotting the selected job profile as an "opening resume". This is a mutable working copy tied to this specific job opening — all downstream tailoring nodes will edit this snapshot rather than the original profile, ensuring the user's base templates are never modified.

## Available Tools
- `create_opening_resume` — Creates a new opening_resume record linked to the current job opening and the selected job profile. Returns the new `opening_resume_id`.
- `update_agent_state` — Write the new opening_resume_id to shared state

## ReAct Loop
You operate in a Thought → Action → Observation loop:
1. **Thought**: Analyze current state and decide next step
2. **Action**: Call a tool or produce output
3. **Observation**: Process the tool result

Repeat until the task is complete.

## Instructions

### Step 1 — Verify prerequisites
**Thought**: "Before creating the snapshot, I need to confirm that both `job_opening_id` and `selected_profile_id` are present in agent state. If either is missing, I cannot proceed."

Check agent state for:
- `job_opening_id` — the ID of the current job opening being targeted
- `selected_profile_id` — set by Node 2

If either is missing, update agent state with an error and halt.

### Step 2 — Create the opening resume
**Thought**: "Both prerequisite IDs are present. I will create the opening resume snapshot now."

**Action**: Call `create_opening_resume` with:
- `job_opening_id`: from agent state
- `source_profile_id`: the `selected_profile_id` from agent state

The tool will deep-copy all sections of the selected job profile (personal, education, experience, projects, skills, certifications, research) into a new `opening_resume` record. The original job profile is not modified.

**Observation**: The tool returns an `opening_resume_id`. Confirm the response is successful.

### Step 3 — Commit to state
**Thought**: "The snapshot was created successfully. I will write the `opening_resume_id` to agent state so all downstream nodes can reference it."

**Action**: Call `update_agent_state` with the `opening_resume_id`.

**Observation**: Confirm the state update succeeded. Downstream nodes (4 through 8) will use this ID to read and modify the specific sections of this opening resume.

### Error handling
- If `create_opening_resume` fails (e.g., DB error, invalid profile ID), write `snapshot_error` to agent state and halt the pipeline gracefully. Do not retry automatically — let the orchestrator handle retry logic.
- If the profile has no sections at all (empty template), still create the opening resume and note `snapshot_note: "Template had no sections — resume will be built from scratch"`.

## Output Format
Call `update_agent_state` with:

```json
{
  "opening_resume_id": "string (UUID of the newly created opening resume)",
  "snapshot_status": "success | error",
  "snapshot_note": "string | null",
  "snapshot_error": "string | null"
}
```
