"""
Main API router
"""
from fastapi import APIRouter
from app.api.v1 import auth, users, tasks, agent, integrations, documents
from app.api.v1.webhooks import bluebubbles, twilio

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(tasks.router)
api_router.include_router(agent.router)
api_router.include_router(integrations.router)
api_router.include_router(documents.router)
api_router.include_router(bluebubbles.router)
api_router.include_router(twilio.router)

