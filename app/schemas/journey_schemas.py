from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from app.models.journey import (
    Location, 
    JourneyState,
    JourneyPlan,
    JourneyProgress,
    ActiveAlert,
    JourneyMetadata,
    TransportMode
)

class JourneyCreate(BaseModel):
    source: str
    destination: str
    preferences: Optional[List[str]] = None

class RouteOption(BaseModel):
    id: str
    name: str
    distance: float
    estimated_duration: float
    safety_score: int
    color: str
    geometry: Any
    is_recommended: bool
    warnings: List[str]

class AIRecommendation(BaseModel):
    title: str
    summary: str
    confidence: int
    reasoning: str
    warnings: List[str]
    suggested_actions: List[str]

class SessionInfo(BaseModel):
    created_at: str
    status: str

class JourneyInformation(BaseModel):
    source: str
    destination: str
    distance: float
    estimated_duration: float

class WeatherSummary(BaseModel):
    condition: str
    temperature: int
    hazards: List[str]

class CommunitySummary(BaseModel):
    reports_along_route: int
    severity_level: str

class JourneyPlanResponse(BaseModel):
    journey_id: str
    session_info: SessionInfo
    journey_information: JourneyInformation
    route_options: List[RouteOption]
    recommended_route: RouteOption
    weather_summary: WeatherSummary
    community_summary: CommunitySummary
    alerts: List[str]
    safety_score: int
    ai_recommendation: AIRecommendation

class JourneyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: str = Field(default="")
    user_id: str = Field(default="")
    source: Location
    destination: Location
    created_timestamp: datetime
    started_timestamp: Optional[datetime] = None
    completed_timestamp: Optional[datetime] = None
    
    plan: Optional[JourneyPlan] = None
    state: JourneyState
    progress: Optional[JourneyProgress] = None
    alerts: List[ActiveAlert] = []
    metadata: JourneyMetadata
    
    from pydantic import model_validator
    
    @model_validator(mode="before")
    @classmethod
    def coerce_objectids(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "_id" in values and "id" not in values:
                values["id"] = values["_id"]
            for key in ("id", "user_id", "_id"):
                if key in values and values[key] is not None:
                    values[key] = str(values[key])
        return values

class LocationUpdate(BaseModel):
    location: Location
