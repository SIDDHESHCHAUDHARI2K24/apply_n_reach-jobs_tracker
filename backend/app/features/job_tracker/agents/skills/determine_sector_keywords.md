# Skill: Determine Sector Keywords

## Overview
Sector keywords are the industry, domain, and business-context terms that signal cultural fit and domain expertise. Unlike technical keywords (which are tool names), sector keywords describe the business world the role operates in — the industry, the type of customer, the regulatory environment, and the business challenges.

Sector keywords matter because:
- Recruiters and hiring managers use them to filter for domain experience
- They appear in ATS searches ("fintech experience", "healthcare background")
- They signal to the hiring team that you understand their world, not just the technology
- Some roles require specific domain knowledge (e.g., finance regulations, HIPAA compliance)

---

## What Counts as a Sector Keyword

A sector keyword is a term that describes **who the business serves, what problem it solves, or what regulatory/market context it operates in** — not a technology or methodology.

| Is a sector keyword | Is NOT a sector keyword |
|---|---|
| "Fintech", "Financial Services" | "Python" (technology) |
| "HIPAA compliance", "Healthcare IT" | "REST API" (technology) |
| "B2B SaaS", "Enterprise software" | "Agile" (methodology) |
| "E-commerce", "Retail", "D2C" | "Microservices" (architecture) |
| "Regulatory compliance", "AML/KYC" | "PostgreSQL" (tool) |
| "Supply chain optimization" | "Machine Learning" (technical domain) |
| "Series B startup", "growth-stage" | "CI/CD" (methodology) |

---

## Extraction Process

### Step 1 — Identify the industry vertical

Look for explicit or implicit industry signals:

**Explicit**: "We are a leading fintech company..." or "Our platform serves healthcare providers..."
**Implicit**: "HIPAA-compliant data pipelines" → Healthcare; "merchant payment processing" → Payments/Fintech; "SKU management" → Retail/E-commerce

**Top industry verticals to identify**:

| Vertical | Trigger phrases |
|---|---|
| **Fintech / Financial Services** | payments, banking, lending, insurance, trading, portfolio, AML/KYC, PCI-DSS, regulatory reporting |
| **Healthcare / Health Tech** | EHR, EMR, HIPAA, HL7, FHIR, clinical, pharma, drug discovery, patient data, medical devices |
| **E-commerce / Retail** | merchant, SKU, inventory, fulfillment, checkout, cart, pricing, catalog, DTC/D2C |
| **Enterprise SaaS / B2B** | enterprise customers, seat-based, SSO, SAML, multi-tenant, SLA, churn, ARR, NRR |
| **Consumer Tech / B2C** | DAU/MAU, user growth, engagement, retention, virality, app store, in-app purchase |
| **Cybersecurity** | threat detection, SOC, SIEM, zero-trust, pen testing, vulnerability management, compliance |
| **DevTools / Infrastructure** | developer experience (DX), SDK, CLI, open source, platform engineering, observability |
| **Data / Analytics** | BI, dashboards, data warehouse, data lakehouse, ETL/ELT, reporting, self-serve analytics |
| **AI / ML Platform** | model deployment, inference, MLOps, vector database, embeddings, LLMs, RAG |
| **Supply Chain / Logistics** | warehouse management, last-mile, routing, demand forecasting, procurement, inventory |
| **Real Estate / PropTech** | listings, MLS, lease management, property management, CRE, mortgage |
| **EdTech** | LMS, curriculum, learning outcomes, engagement, student data, FERPA |
| **Climate / GreenTech** | carbon accounting, emissions, sustainability, ESG, energy management |
| **Government / Public Sector** | FedRAMP, FISMA, clearance, procurement, public records, citizen services |

### Step 2 — Identify the customer type

| Customer type | Keywords |
|---|---|
| Enterprise / large companies | enterprise, Fortune 500, mid-market, B2B, SLA, procurement, MSA |
| SMBs | small business, SMB, self-serve, no-code, plug-and-play |
| Consumers | B2C, consumer, end-user, mobile-first, DAU, retention, engagement |
| Developers | developer-facing, API-first, DX, SDK, open source, developer community |
| Government / NGO | public sector, government, non-profit, grant-funded, compliance-first |

### Step 3 — Identify the business model / growth stage

| Signal | Keywords |
|---|---|
| Growth stage | Series A/B/C, growth-stage, scaling, hypergrowth, pre-IPO |
| Revenue model | subscription, SaaS, usage-based, marketplace, freemium, transactional |
| Business maturity | startup, early-stage, established, post-IPO, enterprise |
| Team context | fast-paced, cross-functional, full-stack ownership, zero-to-one |

### Step 4 — Identify regulatory and compliance context

Compliance requirements often indicate specific domain expertise requirements:

| Regulation/Standard | Domain |
|---|---|
| HIPAA, HITECH | Healthcare |
| PCI-DSS | Payments, Fintech |
| SOC 2 Type II | B2B SaaS, Cloud |
| GDPR, CCPA | Any (data privacy) |
| AML/KYC, BSA | Financial Services |
| FedRAMP, FISMA, ITAR | Government/Defense |
| FINRA, SEC | Securities, Investment |
| FDA 21 CFR Part 11 | Pharmaceuticals, Medical Devices |
| ISO 27001 | Security, Enterprise |
| FERPA | Education |

### Step 5 — Identify domain-specific terminology

Every domain has its own jargon. Surface these as sector keywords because they demonstrate industry fluency:

**Fintech**: chargeback rates, settlement, reconciliation, ledger, open banking, interchange, BIN sponsorship
**Healthcare**: care pathways, clinical decision support, interoperability, claims adjudication, prior auth
**E-commerce**: conversion rate, basket size, abandoned cart, fulfillment SLA, dropshipping, returns rate
**ML/AI**: inference latency, model drift, feature store, ground truth labels, human-in-the-loop
**B2B SaaS**: ARR, NRR, churn rate, product-led growth (PLG), time-to-value, onboarding friction

---

## Output Format

```json
{
  "sector_keywords": {
    "industry_verticals": ["Fintech", "Financial Services", "Payments"],
    "customer_type": ["Enterprise", "B2B"],
    "business_model": ["SaaS", "subscription"],
    "growth_stage": ["Series C", "growth-stage"],
    "regulatory_compliance": ["PCI-DSS", "SOC 2", "AML/KYC"],
    "domain_terminology": ["chargeback reconciliation", "open banking", "ledger design"]
  },
  "business_sectors": ["Fintech"],
  "sector_keyword_list": [
    "Fintech", "Financial Services", "B2B SaaS", "Enterprise",
    "PCI-DSS", "SOC 2", "AML/KYC", "payment processing",
    "chargeback reconciliation", "open banking"
  ]
}
```

---

## Prioritization

**Tier 1 — Directly stated**: Industry name, compliance standards, customer type explicitly mentioned
> "We are a healthcare SaaS company" → "healthcare", "SaaS" are Tier 1

**Tier 2 — Strongly implied**: Technical requirements or context that only exists in that domain
> "HIPAA-compliant pipelines" → "healthcare", "HIPAA compliance" are Tier 1; "Health Tech" is Tier 2

**Tier 3 — Loosely inferred**: Domain vocabulary mentioned incidentally
> "We serve enterprise clients in financial services" → "enterprise" and "financial services" are Tier 1; "fintech" may be Tier 3 if the company is more broadly B2B

---

## Common Pitfalls

- **Do not conflate vertical with technology**: "Data Science" is a discipline, not a sector. "Healthcare data" is a sector term.
- **Do not over-classify**: A company that happens to use cloud infrastructure is not necessarily in "cloud computing" as a sector.
- **Distinguish the employer's sector from the candidate's background**: Node 1 extracts the job's sector. The candidate's sector background is in their experience — tailoring aligns these.
- **Regulatory keywords are high-value**: If a job mentions HIPAA or SOC 2, and the candidate has experience with those frameworks, that must be surfaced prominently in the resume.
