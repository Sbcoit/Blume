from pydantic import BaseModel

class ConnectAgentRequest(BaseModel):
    agentName: str 
    phone: str


class ConnectAgentResponse(BaseModel):
    success: bool
    message: str