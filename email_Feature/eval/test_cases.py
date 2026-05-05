"""
eval/test_cases.py
-------------------
Evaluation test set for T1.5 — Prompt Evaluation Baseline.

Contains 10 JD + resume pairs designed to cover:
  - Varied industries and role types
  - Strong match (minimal skill gaps)
  - Partial match (some skill gaps)
  - Weak match (significant skill gaps)
  - All three recipient types

Each test case specifies which recipient_type to evaluate and includes
an optional linkedin_paste for team_member cases.
"""

from __future__ import annotations
from typing import TypedDict, Optional


class TestCase(TypedDict):
    id: str
    label: str                  # short description for reports
    recipient_type: str         # recruiter | team_member | hiring_manager
    match_level: str            # strong | partial | weak
    raw_jd: str
    raw_resume: str
    linkedin_paste: Optional[str]


TEST_CASES: list[TestCase] = [

    # ------------------------------------------------------------------
    # TC-01: Strong match — ML Engineer → Recruiter
    # ------------------------------------------------------------------
    {
        "id": "TC-01",
        "label": "Strong match — ML Engineer to Recruiter",
        "recipient_type": "recruiter",
        "match_level": "strong",
        "raw_jd": """
Senior Machine Learning Engineer — Stripe
San Francisco, CA (Remote-friendly)

Join our Risk & Fraud team to build production ML models processing
millions of transactions per day. You'll own models end-to-end —
from experimentation to monitoring in production.

Requirements:
- 4+ years ML engineering in production environments
- Python, PyTorch or TensorFlow
- Streaming pipelines (Kafka, Flink, or similar)
- Kubernetes and containerized workloads
- SQL / BigQuery
- Strong cross-functional communication skills
        """.strip(),
        "raw_resume": """
Alex Rivera — Senior ML Engineer | alex@email.com

EXPERIENCE
ML Engineer, DataCo (2021–present)
- Built real-time fraud detection pipeline processing 20M+ events/day
  using Python, Kafka, and BigQuery — reduced false positive rate by 34%
- Trained and deployed 6 production PyTorch models, improving F1 by 18%
- Led migration of ML jobs to Kubernetes, cutting inference latency 60%
- Mentored 3 junior engineers

Data Scientist, StartupX (2019–2021)
- Built recommendation engine in Python/scikit-learn (500K DAU)
- Designed A/B testing framework — reduced experiment cycle time 40%

SKILLS: Python, PyTorch, TensorFlow, Kafka, BigQuery, SQL, Kubernetes,
Docker, scikit-learn, MLflow, Airflow

EDUCATION: M.S. Computer Science (ML), Purdue University, 2019
        """.strip(),
        "linkedin_paste": None,
    },

    # ------------------------------------------------------------------
    # TC-02: Strong match — ML Engineer → Hiring Manager
    # ------------------------------------------------------------------
    {
        "id": "TC-02",
        "label": "Strong match — ML Engineer to Hiring Manager",
        "recipient_type": "hiring_manager",
        "match_level": "strong",
        "raw_jd": """
Senior Machine Learning Engineer — Stripe
San Francisco, CA (Remote-friendly)

Join our Risk & Fraud team to build production ML models processing
millions of transactions per day. You'll own models end-to-end —
from experimentation to monitoring in production.

Requirements:
- 4+ years ML engineering in production environments
- Python, PyTorch or TensorFlow
- Streaming pipelines (Kafka, Flink, or similar)
- Kubernetes and containerized workloads
- SQL / BigQuery
        """.strip(),
        "raw_resume": """
Alex Rivera — Senior ML Engineer | alex@email.com

EXPERIENCE
ML Engineer, DataCo (2021–present)
- Built real-time fraud detection pipeline processing 20M+ events/day
  using Python, Kafka, and BigQuery — reduced false positive rate by 34%
- Trained and deployed 6 production PyTorch models, improving F1 by 18%
- Led migration of ML jobs to Kubernetes, cutting inference latency 60%

Data Scientist, StartupX (2019–2021)
- Built recommendation engine in Python/scikit-learn (500K DAU)

SKILLS: Python, PyTorch, Kafka, BigQuery, SQL, Kubernetes, Docker

EDUCATION: M.S. Computer Science (ML), Purdue University, 2019
        """.strip(),
        "linkedin_paste": None,
    },

    # ------------------------------------------------------------------
    # TC-03: Strong match — ML Engineer → Team Member (with LinkedIn)
    # ------------------------------------------------------------------
    {
        "id": "TC-03",
        "label": "Strong match — ML Engineer to Team Member (LinkedIn provided)",
        "recipient_type": "team_member",
        "match_level": "strong",
        "raw_jd": """
Senior Machine Learning Engineer — Stripe
San Francisco, CA (Remote-friendly)

Join our Risk & Fraud team to build production ML models processing
millions of transactions per day.

Requirements: Python, PyTorch, Kafka, Kubernetes, SQL
        """.strip(),
        "raw_resume": """
Alex Rivera — Senior ML Engineer | alex@email.com

EXPERIENCE
ML Engineer, DataCo (2021–present)
- Built real-time fraud detection pipeline (20M+ events/day)
- Trained and deployed 6 production PyTorch models

SKILLS: Python, PyTorch, Kafka, BigQuery, SQL, Kubernetes
        """.strip(),
        "linkedin_paste": """
Jordan Lee — Staff ML Engineer at Stripe
Currently working on Stripe's real-time risk scoring infrastructure.
Recently posted about our team's work migrating from batch to streaming
feature pipelines using Flink — excited about the latency improvements
we're seeing. Previously at Google where I worked on ads ranking models.
Passionate about making ML systems reliable at scale.
        """.strip(),
    },

    # ------------------------------------------------------------------
    # TC-04: Partial match — Product Manager → Recruiter
    # ------------------------------------------------------------------
    {
        "id": "TC-04",
        "label": "Partial match — Product Manager to Recruiter",
        "recipient_type": "recruiter",
        "match_level": "partial",
        "raw_jd": """
Senior Product Manager — Notion
New York, NY

Lead product strategy for our collaboration features. Work closely
with engineering, design, and data teams to ship high-impact features
for 30M+ users.

Requirements:
- 5+ years PM experience at a B2C SaaS company
- Strong data analysis skills (SQL, Mixpanel, or similar)
- Experience with A/B testing and experimentation frameworks
- Excellent written and verbal communication
- Prior experience with collaboration or productivity tools preferred
- Mobile product experience a plus
        """.strip(),
        "raw_resume": """
Priya Patel — Product Manager | priya@email.com

EXPERIENCE
Product Manager, SaaSCo (2020–present)
- Led roadmap for core editor product (2M users)
- Ran 12 A/B experiments — drove 22% increase in day-30 retention
- Collaborated with 3 engineering teams and design across 2 time zones
- Wrote weekly product updates read by 200+ stakeholders

Associate PM, AgencyX (2018–2020)
- Supported launch of 4 client mobile apps
- Defined KPIs and built dashboards in Mixpanel

SKILLS: Product strategy, roadmapping, A/B testing, Mixpanel, Jira,
Figma, basic SQL

EDUCATION: B.S. Business, NYU Stern, 2018
        """.strip(),
        "linkedin_paste": None,
    },

    # ------------------------------------------------------------------
    # TC-05: Partial match — Product Manager → Hiring Manager
    # ------------------------------------------------------------------
    {
        "id": "TC-05",
        "label": "Partial match — Product Manager to Hiring Manager",
        "recipient_type": "hiring_manager",
        "match_level": "partial",
        "raw_jd": """
Senior Product Manager — Notion
New York, NY

Lead product strategy for our collaboration features.

Requirements:
- 5+ years PM at B2C SaaS
- Strong SQL and data analysis
- A/B testing experience
- Mobile product experience a plus
        """.strip(),
        "raw_resume": """
Priya Patel — Product Manager | priya@email.com

EXPERIENCE
Product Manager, SaaSCo (2020–present)
- Led roadmap for core editor product (2M users)
- Ran 12 A/B experiments — 22% increase in day-30 retention
- Supported 4 mobile app launches at prior role

SKILLS: Product strategy, A/B testing, Mixpanel, basic SQL

EDUCATION: B.S. Business, NYU Stern, 2018
        """.strip(),
        "linkedin_paste": None,
    },

    # ------------------------------------------------------------------
    # TC-06: Partial match — Data Analyst → Team Member (with LinkedIn)
    # ------------------------------------------------------------------
    {
        "id": "TC-06",
        "label": "Partial match — Data Analyst to Team Member (LinkedIn provided)",
        "recipient_type": "team_member",
        "match_level": "partial",
        "raw_jd": """
Senior Data Scientist — Airbnb
Remote

Build models that improve host and guest matching. Work with large
datasets, design experiments, and partner with product teams.

Requirements:
- Python or R, statistical modeling
- Causal inference and experimentation
- SQL at scale (Presto, Spark preferred)
- Strong communication with non-technical stakeholders
        """.strip(),
        "raw_resume": """
Sam Chen — Data Analyst | sam@email.com

EXPERIENCE
Data Analyst, TravelCo (2021–present)
- Built dashboards tracking booking funnel (Python, SQL, Tableau)
- Ran 5 pricing experiments using basic A/B testing
- Presented weekly insights to product and marketing teams

Junior Analyst, AgencyY (2019–2021)
- Cleaned and analyzed survey data in R and Excel

SKILLS: Python, SQL, R, Tableau, basic statistics, Excel

EDUCATION: B.S. Statistics, UC Davis, 2019
        """.strip(),
        "linkedin_paste": """
Morgan Zhang — Data Scientist at Airbnb
Working on the host supply team, focused on understanding why
hosts choose to list or delist. Recently wrote about our team's
approach to causal inference for policy decisions — got a lot of
great discussion going. Big believer in making data science
accessible to everyone on the product team.
        """.strip(),
    },

    # ------------------------------------------------------------------
    # TC-07: Weak match — Frontend Engineer → Recruiter
    # ------------------------------------------------------------------
    {
        "id": "TC-07",
        "label": "Weak match — Frontend Engineer applying for Backend role",
        "recipient_type": "recruiter",
        "match_level": "weak",
        "raw_jd": """
Backend Engineer — Cloudflare
Austin, TX (Remote)

Build and scale distributed systems serving 25M+ requests/second.
Deep work in Go, Rust, or C++. Systems programming, networking,
and performance optimization.

Requirements:
- 4+ years backend/systems engineering
- Go, Rust, or C++ (one required)
- Distributed systems design
- Linux internals, networking protocols (TCP/IP, DNS, HTTP)
- Experience with high-throughput, low-latency systems
        """.strip(),
        "raw_resume": """
Jamie Torres — Frontend Engineer | jamie@email.com

EXPERIENCE
Frontend Engineer, WebAgency (2020–present)
- Built React and TypeScript SPAs for 15+ clients
- Implemented WebSocket-based real-time features
- Improved page load times by 40% through code splitting

Junior Developer, StartupZ (2018–2020)
- Built UI components in Vue.js and vanilla JavaScript

SKILLS: React, TypeScript, Vue.js, JavaScript, HTML/CSS,
Node.js (basic), REST APIs, Git

EDUCATION: B.S. Computer Science, UT Austin, 2018
        """.strip(),
        "linkedin_paste": None,
    },

    # ------------------------------------------------------------------
    # TC-08: Weak match — Marketing Manager → Hiring Manager (tech role)
    # ------------------------------------------------------------------
    {
        "id": "TC-08",
        "label": "Weak match — Marketing Manager applying for growth engineering role",
        "recipient_type": "hiring_manager",
        "match_level": "weak",
        "raw_jd": """
Growth Engineer — Duolingo
Pittsburgh, PA

Own the full funnel from acquisition to activation. Build experiments,
analyze results, and ship features that improve key growth metrics.

Requirements:
- 3+ years software engineering (Python or JavaScript)
- Experience running A/B tests at scale
- SQL proficiency
- Understanding of growth funnels and product analytics
- Comfort working across eng, data, and product
        """.strip(),
        "raw_resume": """
Casey Morgan — Marketing Manager | casey@email.com

EXPERIENCE
Marketing Manager, EdTechCo (2021–present)
- Managed $2M paid acquisition budget across Google and Meta
- Ran campaign A/B tests — improved CAC by 18%
- Partnered with product team on onboarding flow copy

Content Strategist, AgencyA (2019–2021)
- Wrote SEO content for 10+ B2B SaaS clients
- Analyzed content performance in Google Analytics

SKILLS: Marketing strategy, paid ads, copywriting, Google Analytics,
HubSpot, basic Excel, Canva

EDUCATION: B.A. Communications, Penn State, 2019
        """.strip(),
        "linkedin_paste": None,
    },

    # ------------------------------------------------------------------
    # TC-09: Partial match — DevOps Engineer → Recruiter
    # ------------------------------------------------------------------
    {
        "id": "TC-09",
        "label": "Partial match — DevOps Engineer to Recruiter",
        "recipient_type": "recruiter",
        "match_level": "partial",
        "raw_jd": """
Site Reliability Engineer — GitHub
Remote

Ensure reliability, scalability, and performance of GitHub's
infrastructure serving 100M+ developers.

Requirements:
- 3+ years SRE or DevOps experience
- Kubernetes, Terraform, and cloud platforms (AWS or GCP)
- Incident management and on-call experience
- Observability tooling (Prometheus, Grafana, Datadog)
- Python or Go scripting
- Experience with large-scale distributed systems
        """.strip(),
        "raw_resume": """
Riley Kim — DevOps Engineer | riley@email.com

EXPERIENCE
DevOps Engineer, FinServe (2021–present)
- Managed Kubernetes clusters across 3 AWS regions (200+ microservices)
- Wrote Terraform modules for VPC, EKS, and RDS provisioning
- Built Grafana/Prometheus monitoring stack — reduced MTTR by 45%
- On-call rotation for critical payment infrastructure

Junior DevOps, CloudStartup (2019–2021)
- Maintained CI/CD pipelines in Jenkins and GitHub Actions
- Assisted with AWS cost optimization — saved $80K/year

SKILLS: Kubernetes, Terraform, AWS, Prometheus, Grafana, Python,
Bash, Docker, Jenkins, GitHub Actions

EDUCATION: B.S. Information Systems, Georgia Tech, 2019
        """.strip(),
        "linkedin_paste": None,
    },

    # ------------------------------------------------------------------
    # TC-10: Strong match — UX Designer → Team Member (with LinkedIn)
    # ------------------------------------------------------------------
    {
        "id": "TC-10",
        "label": "Strong match — UX Designer to Team Member (LinkedIn provided)",
        "recipient_type": "team_member",
        "match_level": "strong",
        "raw_jd": """
Senior UX Designer — Figma
San Francisco, CA

Shape the future of collaborative design tools. Work with product
and engineering to design intuitive experiences for millions of
designers worldwide.

Requirements:
- 5+ years UX/product design
- Strong portfolio demonstrating complex product design
- Experience with design systems
- Proficiency in Figma (naturally)
- User research and usability testing experience
- Ability to design for both web and mobile
        """.strip(),
        "raw_resume": """
Dana Walsh — Senior UX Designer | dana@email.com

EXPERIENCE
Senior UX Designer, DesignCo (2020–present)
- Led redesign of core editor experience (8M users) — NPS up 22 points
- Built and maintained company-wide design system (300+ components)
- Ran 20+ usability studies; synthesized findings into actionable insights
- Partnered with 4 engineering teams across web and iOS

UX Designer, AgencyB (2018–2020)
- Designed mobile apps for 6 enterprise clients
- Facilitated design sprints and stakeholder workshops

SKILLS: Figma, design systems, user research, usability testing,
prototyping, interaction design, mobile design, Sketch

EDUCATION: B.F.A. Interaction Design, RISD, 2018
        """.strip(),
        "linkedin_paste": """
Taylor Brooks — Product Designer at Figma
On the Figma editor team, currently working on multiplayer
annotation features. Just published a post about how we think
about designing for real-time collaboration — it's a genuinely
hard problem and I love the challenge. Previously at Dropbox
working on Paper. Always happy to chat about design systems
and the craft of product design.
        """.strip(),
    },
]
