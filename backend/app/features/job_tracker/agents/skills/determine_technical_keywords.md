# Skill: Determine Technical Keywords

## Overview
Technical keywords are the specific tools, languages, frameworks, platforms, and methodologies that appear in a job posting. Identifying and categorizing them correctly is essential for:
- ATS (Applicant Tracking System) optimization — most ATS systems scan for exact keyword matches
- Skills section structuring — grouping related keywords into labeled categories
- Experience/project tailoring — knowing which terms to surface in bullet points

---

## What Counts as a Technical Keyword

A technical keyword is a **specific, named technology or methodology** — not a general concept.

| Is a technical keyword | Is NOT a technical keyword |
|---|---|
| "Python", "TypeScript", "Go" | "programming languages" |
| "React", "FastAPI", "PyTorch" | "modern frameworks" |
| "PostgreSQL", "Redis", "Snowflake" | "database experience" |
| "Kubernetes", "Terraform", "AWS Lambda" | "cloud infrastructure" |
| "dbt", "Apache Spark", "Airflow" | "data engineering tools" |
| "Agile/Scrum", "CI/CD", "TDD" | "software development practices" |
| "REST API design", "GraphQL", "gRPC" | "API knowledge" |

---

## Extraction Process

### Step 1 — Scan the full job posting
Read every section: title, responsibilities, required qualifications, preferred qualifications, and even the "about us" section. Technical keywords appear in all of these.

Common locations:
- Required qualifications: "3+ years of experience with **Python** and **SQL**"
- Responsibilities: "Design and maintain **Airflow** DAGs for our data pipeline"
- Preferred qualifications: "Familiarity with **dbt** or **Spark** is a plus"
- About section: "We run on **AWS** with a **Kubernetes**-based microservices architecture"

### Step 2 — Extract and normalize
- Normalize capitalization to the canonical form: "Python" not "python", "PostgreSQL" not "Postgresql"
- Normalize aliases: "k8s" → "Kubernetes", "Postgres" → "PostgreSQL", "JS" → "JavaScript"
- Expand abbreviations when well-known: "ML" → "Machine Learning", "NLP" → "Natural Language Processing"
- Keep abbreviated forms that are the standard: "SQL", "CI/CD", "REST", "gRPC", "ORM"

### Step 3 — Classify by category

#### Programming Languages
All named programming/scripting/query languages.

Examples: Python, TypeScript, JavaScript, Go, Rust, Java, C++, C#, Scala, R, SQL, Bash, Ruby, Swift, Kotlin, MATLAB, Julia

Detection signals:
- "experience with [X]"
- "proficiency in [X]"
- "[X] developer"
- "[X] codebase"

#### Frameworks & Libraries
Libraries, frameworks, and SDKs built on top of a language.

Examples: React, Vue, Angular, Next.js, FastAPI, Django, Flask, Express, Spring Boot, PyTorch, TensorFlow, Keras, Scikit-learn, Pandas, NumPy, LangChain, Hugging Face Transformers, dbt, Spark, Hadoop, Kafka

Detection signals:
- "built with [X]"
- "using [X] for [task]"
- "[X]-based [component]"

#### Cloud Platforms & Services
Cloud providers and their named services.

Examples: AWS (and specific services: EC2, S3, Lambda, RDS, SageMaker, ECS, EKS), Google Cloud (GCS, BigQuery, Vertex AI, Cloud Run), Azure (AKS, Azure Functions, Azure ML), Cloudflare, Vercel, Heroku

Note: Extract both the platform name ("AWS") and specific services ("AWS Lambda", "S3") as separate keywords when both are mentioned.

#### Infrastructure & DevOps Tools
Container orchestration, IaC, CI/CD, monitoring.

Examples: Docker, Kubernetes, Helm, Terraform, Ansible, Pulumi, Jenkins, GitHub Actions, GitLab CI, CircleCI, ArgoCD, Prometheus, Grafana, Datadog, PagerDuty, Vault

#### Databases & Data Stores
Relational, NoSQL, caching, search, and streaming stores.

Examples: PostgreSQL, MySQL, SQLite, MongoDB, DynamoDB, Cassandra, Redis, Memcached, Elasticsearch, OpenSearch, Pinecone, Neo4j, Snowflake, BigQuery, Redshift, Databricks, ClickHouse, Apache Kafka, RabbitMQ, Celery

#### AI/ML & Data Science Tools
Model training frameworks, MLOps platforms, experimentation tools.

Examples: PyTorch, TensorFlow, JAX, Scikit-learn, XGBoost, LightGBM, MLflow, Weights & Biases (W&B), Kubeflow, SageMaker, Vertex AI, Hugging Face, LangChain, OpenAI API, ONNX, TensorRT, Ray, Dask

#### APIs & Protocols
Specific API paradigms or communication protocols (not the concept, but named systems).

Examples: REST (RESTful APIs), GraphQL, gRPC, WebSockets, OAuth 2.0, OpenAPI/Swagger, Protocol Buffers, MQTT, AMQP

#### Methodologies & Practices
Named software engineering or organizational methodologies.

Examples: Agile, Scrum, Kanban, SAFe, CI/CD, TDD, BDD, DDD (Domain-Driven Design), Event-Driven Architecture, CQRS, Microservices, Serverless, DevSecOps, GitFlow, Pair Programming, Code Review

---

## Prioritization

Not all keywords carry equal weight. Classify extracted keywords by importance:

**Tier 1 — Explicitly required** (appear in "Required" section, or mentioned 2+ times):
> These must appear in the resume. Missing Tier 1 keywords will often result in ATS rejection.

**Tier 2 — Preferred / mentioned once** (appear in "Nice to have" or only in responsibilities):
> These should be added if the candidate genuinely knows them.

**Tier 3 — Context / inferred** (implied by the tech stack but not named):
> Add only if directly relevant; do not over-pad.

---

## Output Format

Return a structured list organized by category:

```json
{
  "technical_keywords": {
    "languages": ["Python", "SQL", "TypeScript"],
    "frameworks_libraries": ["FastAPI", "React", "Pandas", "dbt"],
    "cloud_services": ["AWS", "S3", "Lambda", "ECS"],
    "infrastructure_devops": ["Docker", "Kubernetes", "Terraform", "GitHub Actions"],
    "databases": ["PostgreSQL", "Redis", "Snowflake"],
    "ai_ml_tools": ["PyTorch", "MLflow", "Scikit-learn"],
    "apis_protocols": ["REST", "GraphQL"],
    "methodologies": ["Agile/Scrum", "CI/CD", "TDD"]
  },
  "tier_1_required": ["Python", "SQL", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
  "tier_2_preferred": ["dbt", "Snowflake", "MLflow"],
  "tier_3_inferred": ["Bash", "Git", "Linux"]
}
```

---

## Common Pitfalls to Avoid

- **Do not extract concepts as keywords**: "object-oriented programming" is not a keyword. "Python OOP" is not a keyword. "Python" is the keyword.
- **Do not duplicate across categories**: If "AWS Lambda" is listed under `cloud_services`, do not also list it under `frameworks_libraries`.
- **Respect canonical naming**: "Node.js" not "NodeJS", "TypeScript" not "Typescript", "Kubernetes" not "kubernetes".
- **Do not conflate related technologies**: "React" and "React Native" are different keywords; "PyTorch" and "TensorFlow" are different and should both be listed if both appear.
