# 💼 AI Career & Skill Advisor Chatbot

An intelligent, conversational web application built with **Python Language**. The application develops with tech stack for instances, **LangChain**, **Flask**, **Flask-JWT-Extended**, **PostgreSQL**, **FAISS**, and **Google Gemini 2.5 Flash**. The application acts as an expert career consultant, analyzing user criteria to deliver tailored job recommendations, skill gap analyses, and actionable learning roadmaps.
---

## 🌟 Key Features

* **Intelligent Career Recommendations** : Leverages Google Gemini to suggest specific job roles and career paths based on user interests, background, and goals.

* **Deep Criteria Analysis** : Analyzes user-prompted criteria (such as current technical skills, educational background, and experience levels) to assess readiness for target roles.

* **Skill Summarization & Roadmaps** : Breaks down complex professional domains into digestible skill summaries and structured, step-by-step learning milestones.

* **Secure Authentication Gateway** : Uses a robust, server-side rendered Flask authentication gateway backed by a PostgreSQL user database and JWT generation.

* **Role-Based Rate Limiting** : Enforces strict limits in the Streamlit UI—allowing unauthenticated public visitors exactly 3 exploratory sandbox queries, while unlocking unlimited AI consultations for authenticated users.

* **Bi-Directional Function Calling** : Utilizes LangChain Tool-Calling agents to let Gemini dynamically fetch user profiles directly from the PostgreSQL database or run semantic queries against the ChromaDB vector repository.
---

## 🛠️ Tech Stack

Frontend UI & AI Sandbox: Streamlit (Chat Workspace Engine)

* **App Server & Client Auth** : Flask (Server-Side Rendered views with HTML templates)

* **Authentication Engine** : JWT (JSON Web Tokens via PyJWT/Flask-JWT-Extended)

* **Relational Database** : PostgreSQL (Stores secure user profiles, metadata, and history)

* **Vector Database** : pgvector/Faiss/ChromaDB (Stores career documents, curriculum frameworks, and job specs)

* **LLM Orchestration** : LangChain (LangChain Core & LangChain Google GenAI)

* **Foundation Model** : Google Gemini 2.5 Flash
*   **Language:** Python 3.13+
*   **LLM Orchestration:** LangChain (LangChain Core & LangChain Google GenAI)
*   **Foundation Model:** Google Gemini 2.5 Flash
*   **Frontend UI:** Streamlit
---

## 🏗️ Architectural Styles: Code Structure Breakdown
To provide optimal design flexibility and development agility, the repository can be organized into two distinct architectural styles. Both styles share the exact same logical code components but differ significantly in how the files are grouped.

### Style 1: The Domain-Driven Design (DDD) "Split-Ready" Layout
Best for: Rapid horizontal/vertical scaling, service isolation, and future migration to Microservices.

Files are sliced vertically by business domains (Bounded Contexts). Each folder acts as an independent application component that can eventually be broken off into separate hardware nodes.

```
alokoh.ai/
│
├── config/                           # System Core Bootstrapping
│   ├── settings.py                   # Environment variable parser (.env configurations)
│   └── database.py                   # Shared Connections (PostgreSQL & ChromaDB handles)
│
├── main.py                           # Application entry point (Launches the system)
│
└── app/
    ├── shared/                       # Shared application cross-cut concerns
    │   ├── middlewares.py            # JWT Validation & Public 3-query limit trackers
    │   └── templates/                # Global Jinja2 Base framework
    │       └── base.html             # Base HTML skin
    │
    └── modules/                      # VERTICAL FUNCTIONAL BUSINESS DOMAINS
        │
        ├── identity_access/          # --- DOMAIN A: USER PORTAL & AUTH ---
        │   ├── routes.py             # Flask Web Router (Renders login.html / register.html)
        │   ├── services.py           # Core Identity Logic (Bcrypt hashing, SQL validation)
        │   ├── models.py             # PostgreSQL user table schemas via SQLAlchemy
        │   └── templates/
        │       ├── login.html        # Simple Server-Side Rendered Login View
        │       └── register.html     # Simple Server-Side Rendered Registration View
        │
        ├── advisor_workspace/        # --- DOMAIN B: ADVISOR UI TERMINAL ---
        │   ├── dashboard.py          # Main Streamlit Chat Interface (The UI App)
        │   └── session_state.py      # Manages LangChain chat memory inside Streamlit
        │
        └── cognitive_engine/         # --- DOMAIN C: AI CORE COMPUTATION ---
            ├── agent_core.py         # LangChain Executor setup (Initializes Gemini 2.5 Flash)
            ├── tools.py              # Function Calling Tool definitions (Hooks to SQL / ChromaDB)
            ├── providers/
            │   └── gemini_client.py  # Native Google Gemini API adapter wrapper
            └── vector_memory/
                ├── embedding.py      # LangChain text embedding process pipelines
                └── memo_store.py   # ChromaDB collection setups for skills/roadmaps
```