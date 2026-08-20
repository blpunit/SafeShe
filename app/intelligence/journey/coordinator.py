from typing import Dict, Any, Optional
from app.agents.workflow_manager import WorkflowManager
from app.ml.normalizer import DataNormalizer
from app.ml.features import FeatureEngineer
from app.ml.predictor import DummyMLPredictor
from app.intelligence.decision.engine import DecisionEngine
from app.tools.specialized.reasoning_tool import ReasoningTool
from app.intelligence.response.builder import ResponseBuilder

class JourneyIntelligenceCoordinator:
    """
    The exclusive public entry point into the Journey Intelligence Layer.
    Orchestrates the Agentic AI Pipeline without executing logic itself.
    """
    
    def __init__(self):
        self.workflow_manager = WorkflowManager()
        self.normalizer = DataNormalizer()
        self.feature_engineer = FeatureEngineer()
        self.ml_predictor = DummyMLPredictor()
        self.decision_engine = DecisionEngine()
        self.reasoning_tool = ReasoningTool()
        self.response_builder = ResponseBuilder()

    async def execute_pipeline(self, workflow_type: str, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the full intelligence pipeline.
        """
        # Step 1: Agent Execution via Workflow Manager (includes Agent Registry -> Tools -> Providers)
        agent_results = await self.workflow_manager.run_workflow(workflow_type, initial_context)
        
        # Step 2: Normalization
        normalized_data = self.normalizer.normalize(agent_results)
        
        # Step 3: Feature Engineering
        feature_vector = self.feature_engineer.engineer_features(normalized_data)
        
        # Step 4: ML Prediction
        ml_prediction = self.ml_predictor.predict(feature_vector)
        
        # Step 5: Decision Engine
        context_for_decision = {**normalized_data, **initial_context}
        decision = self.decision_engine.decide(ml_prediction, context_for_decision)
        
        # Step 6: LLM Reasoning
        llm_context = {
            "decision": decision,
            "ml_prediction": ml_prediction,
            "agent_results": agent_results
        }
        llm_reasoning = await self.reasoning_tool.execute({"context": llm_context})
        
        # Assemble Final Context for Response Builder
        final_context = {
            **agent_results,
            "NormalizedData": normalized_data,
            "MLPrediction": ml_prediction,
            "Decision": decision,
            "LLM": llm_reasoning
        }
        
        return final_context

    # --- Router Endpoints ---

    async def build_journey_plan_response(self, journey_id: str, request: Any) -> Any:
        from app.providers.location.provider import NominatimLocationProvider
        from app.providers.routing.provider import OSRMRoutingProvider
        from app.models.journey import Location
        from fastapi import HTTPException
        import logging
        
        logger = logging.getLogger(__name__)
        loc_provider = NominatimLocationProvider()
        route_provider = OSRMRoutingProvider()
        
        # Parse Source
        try:
            if "," in request.source:
                lat, lon = request.source.split(",")
                source_loc = Location(type="Point", coordinates=[float(lon.strip()), float(lat.strip())])
            elif "Detecting" in request.source or "Current" in request.source:
                source_loc = Location(type="Point", coordinates=[77.5946, 12.9716])
            else:
                source_loc = await loc_provider.forward_geocode(request.source)
        except Exception as e:
            logger.error(f"Geocoding source failed: {str(e)}")
            source_loc = Location(type="Point", coordinates=[77.5946, 12.9716])
            
        # Parse Destination
        try:
            if "," in request.destination:
                lat, lon = request.destination.split(",")
                dest_loc = Location(type="Point", coordinates=[float(lon.strip()), float(lat.strip())])
            else:
                dest_loc = await loc_provider.forward_geocode(request.destination)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not find destination: {str(e)}")
            
        # Get Routes
        try:
            candidates = await route_provider.get_routes(source_loc, dest_loc, mode="foot", alternatives=3)
            if not candidates:
                raise ValueError("No routes found")
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Routing service unavailable: {str(e)}")
            
        # Optional: reverse geocode for display names
        try:
            source_addr = await loc_provider.reverse_geocode(source_loc)
            source_name = source_addr.display_name.split(",")[0]
        except:
            source_name = "Current Location"
            
        try:
            dest_addr = await loc_provider.reverse_geocode(dest_loc)
            dest_name = dest_addr.display_name.split(",")[0]
        except:
            dest_name = request.destination

        user_id = getattr(request, 'user_id', "u_1")
        final_context = {
            "source_name": source_name,
            "dest_name": dest_name,
            "routes": candidates
        }
        return self.response_builder.build_journey_plan(final_context, user_id, journey_id)

    async def build_dashboard_overview(self, user_id: str) -> Any:
        context = {"user_id": user_id}
        final_context = await self.execute_pipeline("dashboard", context)
        return self.response_builder.build_dashboard_overview(final_context)

    async def build_assistant_context(self, user_id: str) -> Any:
        context = {"user_id": user_id, "query": "init"}
        final_context = await self.execute_pipeline("assistant", context)
        return self.response_builder.build_assistant_context(final_context, user_id)

    async def process_assistant_chat(self, user_id: str, query: str) -> Any:
        context = {"user_id": user_id, "query": query}
        final_context = await self.execute_pipeline("assistant", context)
        return self.response_builder.build_assistant_chat(final_context, user_id, query)

    async def build_emergency_status(self, session_id: str, user_id: str) -> Any:
        context = {"user_id": user_id, "session_id": session_id}
        final_context = await self.execute_pipeline("emergency", context)
        return self.response_builder.build_emergency_status(final_context, session_id, user_id)

    async def build_profile_response(self, user_id: str) -> Any:
        context = {"user_id": user_id}
        final_context = await self.execute_pipeline("profile", context)
        return self.response_builder.build_profile_response(final_context, user_id)

    async def build_settings_response(self, user_id: str) -> Any:
        context = {"user_id": user_id}
        final_context = await self.execute_pipeline("profile", context)
        return self.response_builder.build_settings_response(final_context, user_id)
