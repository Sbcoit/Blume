/agent-platform/
│
├── backend/                  # Backend services (Python + FastAPI)
│   ├── app/                  # Main application source code
│   │   ├── main.py           # FastAPI entry point; starts server and routes
│   │   ├── config/           # Configuration and environment variables
│   │   │   └── config.py     # Loads secrets (BlueBubbles API token, Supabase keys, Groq API key, etc.)
│   │   ├── routes/           # API endpoints and webhooks
│   │   │   ├── bluebubbles.py   # Webhook endpoint for incoming iMessages
│   │   │   ├── health.py        # Health check endpoint (for uptime monitoring)
│   │   │   └── users.py         # Optional: user management endpoints (create, update, roles)
│   │   ├── services/         # External integrations
│   │   │   ├── bluebubbles_api.py  # Outbound iMessage sending through BlueBubbles API
│   │   │   └── google_calendar.py  # Google Calendar API integration for scheduling workflow
│   │   ├── engine/           # Core agent engine
│   │   │   ├── intent_classifier.py   # Uses Groq LLM to classify incoming messages into intents
│   │   │   ├── argument_binder.py     # Extracts arguments from messages (date, time, event name)
│   │   │   ├── execution_planner.py   # Determines steps needed to complete workflow
│   │   │   ├── step_executor.py       # Executes primitives in order and handles confirmations
│   │   │   ├── primitives/    # Reusable, atomic actions
│   │   │   │   ├── event_ingestion.py  # Normalize and store incoming message events
│   │   │   │   ├── tool_invocation.py  # Call external tools (Calendar API)
│   │   │   │   ├── state_access.py     # Read/write workflow state in Supabase
│   │   │   │   └── audit_logger.py     # Log every action and step for traceability
│   │   │   └── workflows/    # Workflow definitions
│   │   │       ├── schedule_event.py  # Example workflow: schedule an event in Google Calendar
│   │   │       └── ...                 # Placeholder for future workflows
│   │   ├── models/           # Database models / Pydantic schemas
│   │   │   ├── workflow.py       # Workflow state & artifact schema
│   │   │   └── user.py           # User/organization schema
│   │   ├── db/               # Supabase database connection and repository layer
│   │   │   ├── base.py             # Base connection and helper functions
│   │   │   ├── workflow_repo.py    # Functions for saving/retrieving workflow state
│   │   │   └── audit_repo.py       # Functions for audit logging
│   │   └── utils/            # Helper functions
│   │       └── time_parsing.py     # Parse dates/times from natural language
│   │
│   ├── tests/                # Unit and integration tests for backend
│   │   ├── engine/           # Tests for agent engine (intent classifier, step executor)
│   │   ├── services/         # Tests for BlueBubbles and Google Calendar services
│   │   └── routes/           # Tests for API endpoints / webhooks
│   │
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # React + Next.js dashboard
│   ├── src/
│   │   ├── pages/
│   │   │   ├── index.js           # Dashboard / activity log overview
│   │   │   ├── agent.js           # Details about agent execution & stats
│   │   │   └── calendar.js        # Connected Google Calendar management
│   │   ├── components/            # Reusable UI components
│   │   │   ├── ActivityList.js        # List of all workflow executions
│   │   │   ├── ExecutionDetail.js     # Step-by-step execution details
│   │   │   └── ConfirmationToggle.js  # UI for confirming steps/actions
│   │   ├── services/
│   │   │   └── api.js             # Handles calls to backend endpoints (REST API)
│   │   └── styles/                # CSS / Tailwind styles
│   └── package.json
│
├── bluebubbles/               # Optional: local scripts/config for BlueBubbles server
│   ├── readme.md               # Setup instructions and API token notes
│   └── config.json             # BlueBubbles credentials / API tokens
│
├── docker/                     # Docker configs for dev/prod
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
│
├── scripts/                    # Deployment / utility scripts
│   ├── deploy.sh               # Deployment automation
│   └── migrate_db.sh           # Database migration scripts
│
├── docs/                       # Architecture diagrams, API docs, onboarding
├── tests/                      # End-to-end tests (frontend + backend)
└── README.md                   # Project overview and setup instructions
