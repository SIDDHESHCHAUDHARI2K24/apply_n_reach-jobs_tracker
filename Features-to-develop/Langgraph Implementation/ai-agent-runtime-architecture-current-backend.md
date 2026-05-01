# AI Agent Runtime Architecture (Current Backend)

Based on:
- `backend/app/features/job_tracker/agents/graph.py`
- `backend/app/features/job_tracker/agents/runner.py`
- `backend/app/features/job_tracker/agents/router.py`
- `backend/app/features/job_tracker/agents/mcp_server.py`
- `backend/app/features/job_tracker/opening_ingestion/router.py`
- `backend/app/features/job_tracker/opening_resume/latex_resume/router.py`
- `Features-to-develop/Langgraph Implementation/development-plan.md`

```mermaid
flowchart TD
  subgraph client [Client and Trigger]
    jobTrackerUI[JobTrackerUI]
    runAction[RunAIAgentAction]
    sseListener[SSEListener]
  end

  subgraph api [FastAPI Agent Endpoints]
    postRun["POST /job-openings/{opening_id}/agent/run"]
    getStream["GET /job-openings/{opening_id}/agent/stream"]
    getStatus["GET /job-openings/{opening_id}/agent/status"]
    getRuns["GET /job-openings/{opening_id}/agent/runs"]
  end

  subgraph runnerLayer [Agent Runner and State]
    backgroundTask[BackgroundTask_run_agent_background]
    runAgent[run_agent_stream]
    runTable[(job_opening_agent_runs)]
    openingsTable[(job_openings)]
  end

  subgraph graphLayer [LangGraph Execution]
    buildGraph[build_graph]
    nExtract[extract_node1]
    nSelect[select_template_node2]
    nSnapshot[snapshot_node3]
    nTriage[triage_node4]
    nExperience[experience_node5a]
    nProjects[projects_node5b]
    nSkills[skills_node5c]
    nPersonal[personal_node5d]
    nSkillsCerts[skills_certs_node6]
    nRender[render_node7]
    nOptimiser[optimiser_node8]
  end

  subgraph mcpLayer [InProcess MCP Style Tool Layer]
    agentContext[AgentContext_user_conn_opening]
    toolRegistry[get_agent_tools]
    toolUpdateState[tool_update_agent_state]
    toolResumeOps[tool_opening_resume_crud]
    toolExtracted[tool_get_extracted_details]
    toolRender[tool_render_resume_pdf]
    toolPdfMeta[tool_get_resume_pdf_count_pages]
  end

  subgraph dependencyApis [Related Supporting Endpoints]
    extractionRefresh["POST /job-openings/{opening_id}/extraction/refresh"]
    extractionLatest["GET /job-openings/{opening_id}/extracted-details/latest"]
    resumePdf["GET /job-openings/{opening_id}/resume/latex-resume/pdf"]
  end

  jobTrackerUI --> runAction
  runAction --> postRun
  runAction --> getStatus
  runAction --> getRuns
  runAction --> getStream
  getStream --> sseListener

  postRun --> backgroundTask
  backgroundTask --> runAgent

  runAgent --> runTable
  runAgent --> openingsTable
  runAgent --> buildGraph
  runAgent --> agentContext

  buildGraph --> nExtract
  nExtract --> nSelect
  nSelect --> nSnapshot
  nSnapshot --> nTriage
  nTriage --> nExperience
  nExperience --> nProjects
  nProjects --> nSkills
  nSkills --> nPersonal
  nPersonal --> nSkillsCerts
  nSkillsCerts --> nRender
  nRender --> nOptimiser
  nOptimiser -->|"if pages != 1 and iterations < 3"| nRender

  agentContext --> toolRegistry
  toolRegistry --> toolUpdateState
  toolRegistry --> toolResumeOps
  toolRegistry --> toolExtracted
  toolRegistry --> toolRender
  toolRegistry --> toolPdfMeta

  nExtract -->|"reads extracted details"| toolExtracted
  nSnapshot -->|"creates opening resume snapshot"| toolResumeOps
  nExperience -->|"updates experience rows"| toolResumeOps
  nProjects -->|"updates project rows"| toolResumeOps
  nSkills -->|"adds removes skill rows"| toolResumeOps
  nPersonal -->|"updates personal summary"| toolResumeOps
  nRender -->|"renders and inspects PDF"| toolRender
  nRender -->|"page count"| toolPdfMeta

  extractionRefresh --> extractionLatest
  extractionLatest --> nExtract
  nRender --> resumePdf
```

## Node Responsibilities

- `node1_extract`: loads latest extracted job details from ingestion snapshot.
- `node2_select_template`: picks best `job_profile` template (LLM-assisted if multiple).
- `node3_snapshot`: creates opening-resume snapshot from selected profile.
- `node4_triage`: analyzes which sections need adaptation.
- `node5a..5d`: rewrite experience/projects/skills/personal content.
- `node6_skills_certs`: alignment check for certifications and skills.
- `node7_render`: render LaTeX PDF and compute page count.
- `node8_optimiser`: trims and loops back to render until page target or max iterations.

## Endpoint Interaction Summary

- Primary agent API used by UI:
  - `/job-openings/{opening_id}/agent/run`
  - `/job-openings/{opening_id}/agent/stream`
  - `/job-openings/{opening_id}/agent/status`
  - `/job-openings/{opening_id}/agent/runs`
- Upstream data dependency:
  - `/job-openings/{opening_id}/extraction/refresh`
  - `/job-openings/{opening_id}/extracted-details/latest`
- Downstream artifact endpoint:
  - `/job-openings/{opening_id}/resume/latex-resume/pdf`

## MCP Connectivity Note

In current code, MCP is implemented as an in-process tool layer via `get_agent_tools()` and shared `AgentContext` (not an external MCP transport endpoint).
