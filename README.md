# **Blume**

## Agentic iMessage Workflow Platform

---

## **Overview**

Blume is a **self-hosted, agentic assistant platform** that communicates through **iMessage (blue bubbles)** and executes explicit, user-requested workflows such as scheduling events in Google Calendar.

Blume is designed to act as a **separate entity**, not impersonating the user and never acting autonomously. It only performs actions when directly instructed via iMessage or through the web dashboard.

The platform is built as a **B2B-style SaaS system**, consisting of:

* A **macOS-hosted BlueBubbles server** for iMessage connectivity
* A **cloud backend** that interprets messages and executes workflows
* A **web dashboard** for visibility, monitoring, and future configuration
* A **workflow-first architecture** designed to scale to complex agent behaviors

---

## **Core Principles**

* **Explicit control** – the agent only acts when told
* **Agentic separation** – the agent is not “you”
* **Workflow-first** – every action is a workflow
* **Modular and extensible** – new workflows plug in cleanly
* **Blue-bubble native** – iMessage only (no SMS, no Twilio)

---

## **Key Features (MVP)**

### **iMessage Agent Interface**

* Users interact with Blume via **iMessage**
* Messages are sent and received as **blue bubbles**
* Powered by a self-hosted **BlueBubbles server** running on macOS

### **Workflow Execution**

* Incoming messages are interpreted as **explicit workflow triggers**
* Initial supported workflow:

  * **Schedule events in Google Calendar**
* Architecture supports:

  * Multi-step workflows
  * Confirmations and approvals
  * Auditing and traceability

### **Agent Engine**

* Uses **Groq LLM** for:

  * Intent classification
  * Argument extraction
* Executes workflows via a deterministic step executor
* No autonomous or background execution

### **Web Dashboard**

* View workflow executions in real time
* Inspect step-by-step execution details
* Monitor agent activity, failures, and logs
* Automatically supports new workflows without frontend rewrites

---

## **High-Level Architecture**

```
User (iMessage)
   ↓
BlueBubbles Server (macOS)
   ↓ Webhook
Backend API (FastAPI)
   ├─ Intent Classification (Groq)
   ├─ Argument Binding
   ├─ Workflow Planner
   ├─ Step Executor
   └─ Primitives
       ├─ Tool Invocation
       ├─ State Persistence
       └─ Audit Logging
   ↓
Supabase (PostgreSQL + Realtime)
   ↓
Web Dashboard (Next.js)
```

---

## **Technology Stack**

### Messaging

* **BlueBubbles Server**
* Apple ID (optionally with a verified phone number)

### Backend

* **Python**
* **FastAPI**
* **Groq LLM**
* **Supabase (PostgreSQL)**

### Frontend

* **Next.js**
* **React**
* **TailwindCSS**
* Supabase Realtime subscriptions

### Deployment

* Docker (backend & frontend)
* macOS machine (physical or hosted) for BlueBubbles

---

## **Project Structure**

```
blume/
├── backend/        # Agent engine, workflows, APIs
├── frontend/       # Dashboard UI
├── bluebubbles/    # BlueBubbles configuration and docs
├── docker/         # Dockerfiles
├── scripts/        # Deployment & migration scripts
├── docs/           # Architecture & diagrams
└── README.md
```

---

## **Agent Design Philosophy**

### What Blume Does

* Interprets explicit instructions
* Executes defined workflows
* Persists state and logs
* Reports outcomes clearly

### What Blume Does Not Do

* Auto-respond to messages
* Act without explicit commands
* Pretend to be the user
* Run silent background tasks

---

## **Workflows**

Workflows are the core abstraction in Blume.

Each workflow:

* Is triggered explicitly by a message
* Has a defined schema
* Executes through atomic primitives
* Persists state and audit logs

### **Example Workflow: Schedule Event**

```
User: “Schedule a meeting tomorrow at 3pm”
→ Intent: schedule_event
→ Arguments: { date, time, title }
→ Steps:
   1. Persist workflow state
   2. Call Google Calendar API
   3. Confirm completion
```

Adding a new workflow requires:

* Creating a new file in `engine/workflows/`
* No modification to the core engine

---

## **Why BlueBubbles (No Twilio)**

* iMessage provides a **native, trusted UX**
* Blue bubbles only
* No SMS fallback complexity
* The agent feels natural and first-class

---

## **Future Expansion**

* Multi-step and conditional workflows
* Task and reminder management
* Email, Slack, and third-party integrations
* Multi-tenant organizations
* Role-based permissions
* Multiple Apple IDs per deployment
* Advanced audit, replay, and observability tools

---

## **Development Status**

* Architecture defined
* Frontend scaffolded
* Backend engine designed
* MVP workflow: calendar scheduling

---

## **License**

MIT (or TBD)

---

## **Summary**

Blume is a **workflow-first, agentic assistant platform** built on iMessage.
It emphasizes **control, transparency, and extensibility**, serving as both a practical assistant and a foundation for advanced agent-driven SaaS products.

---

