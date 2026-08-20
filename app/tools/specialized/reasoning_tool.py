from typing import Dict, Any
from app.tools.base import BaseTool, ToolMetadata

class ReasoningTool(BaseTool):
    @property
    def name(self) -> str:
        return "ReasoningTool"

    @property
    def description(self) -> str:
        return "Provides LLM explanation and reasoning."

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            capability="Reasoning",
            required_inputs=["context"],
            output_schema={"type": "dict"},
            ranking_score=10
        )

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Since this is still a dummy implementation, we hardcode the output.
        """
        decision = params.get("context", {}).get("decision", {})
        
        return {
            "summary": "This route avoids the current heavy crowding near the Transit Center while maintaining excellent lighting.",
            "reasoning": [
                "ML model scored this path high due to low crowds.",
                "Zero community hazard reports found.",
                "High visibility metrics from weather."
            ]
        }
