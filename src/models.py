from pydantic import BaseModel, Field

class EnginePayload(BaseModel):
    event_type: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=1)