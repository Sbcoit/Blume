# Blume Platform

A personal secretary agent platform accessible via iMessage (with blue bubbles), calls, and web interface. Users interact with an AI agent for scheduling, workflows, research, calls/texts, and document synthesis.

## Architecture

- **Frontend**: Next.js 14+ (App Router) with TypeScript
- **Backend**: FastAPI (Python) with async support
- **AI/LLM**: Groq API
- **iMessage Integration**: BlueBubbles Server (runs on Mac Mini)
- **Calls**: Twilio (for voice calls)
- **Database**: PostgreSQL with SQLAlchemy ORM

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- PostgreSQL database
- Mac Mini with macOS 10.12+ (for BlueBubbles server)

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Set up database:
   ```bash
   # Create database
   createdb blume

   # Run migrations
   alembic upgrade head
   ```

6. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your configuration
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

### BlueBubbles Server Setup (Mac Mini)

1. Download BlueBubbles server from [GitHub Releases](https://github.com/BlueBubblesApp/bluebubbles-server/releases)

2. Install the .dmg file on your Mac Mini

3. Grant required permissions:
   - **Full Disk Access**: Required to read iMessage database
   - **Accessibility**: For certain features (optional)

4. Configure the server:
   - Set a strong server password
   - Configure proxy service (Cloudflare recommended)
   - Set up Firebase for notifications

5. Ensure iMessage is activated with your phone number/email on Apple ID

6. Configure webhook:
   - Navigate to BlueBubbles server settings → "API & Webhooks"
   - Add webhook URL: `https://your-backend.com/api/v1/webhooks/bluebubbles`
   - Subscribe to events: "New Message", "Message Update", etc.

## Project Structure

```
assistantagent/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
└── README.md
```

## Features

- ✅ Authentication (signup/login)
- ✅ Dark-mode Apple-glass aesthetic UI
- ✅ Home tab with phone number setup
- ✅ Tasks tab with Luma Events-style presentation
- ✅ Settings tab with integrations
- ✅ iMessage integration via BlueBubbles (blue bubbles!)
- ✅ Modular, scalable architecture
- ✅ Agent system with Groq LLM
- ✅ Task management
- ✅ Document processing

## Development

The architecture is modular and follows SOLID principles:

- **Plugin/Interface Pattern**: All integrations implement base interfaces
- **Event-Driven Architecture**: Decoupled communication via event bus
- **Dependency Injection**: Services injected via FastAPI dependencies
- **Handler Pattern**: Modular agent handlers for different task types

## License

MIT

