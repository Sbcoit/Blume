from fastapi import FastAPI, APIRouter
from backend.app.models.agent import ConnectAgentRequest, ConnectAgentResponse


router = APIRouter()


@router.post("/connect")
def connect_agentInterface( user_config: ConnectAgentRequest):




    agent_res  = ConnectAgentResponse(success=True, message="Successfully Connected")

    return {"message" : "Connection Received" , "Agent Response" : agent_res}




