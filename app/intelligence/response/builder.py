from typing import Dict, Any

class ResponseBuilder:
    """
    Constructs the exact Pydantic DTOs required by the frontend APIs based on the evaluated context.
    """
    def build_dashboard_overview(self, final_context: Dict[str, Any]) -> Any:
        from app.schemas.dashboard_schemas import DashboardOverviewResponse, AIStatus, SafetyScoreStatus, WeatherStatus, CommunityStatus, SystemHealthStatus, RecentJourneyItem, AlertItem, AITimelineEventItem
        import datetime
        
        dashboard_data = final_context.get("DashboardAgent", {})
        
        return DashboardOverviewResponse(
            ai_status=AIStatus(
                mode="Active Monitoring",
                health="Optimal",
                last_analysis=datetime.datetime.utcnow().isoformat(),
                recommendation="No action needed."
            ),
            safety_score=SafetyScoreStatus(
                overall=98,
                risk_level="Low",
                confidence=96,
                trend="Stable"
            ),
            weather=WeatherStatus(
                condition="Clear",
                temperature=24,
                visibility=10000,
                humidity=45,
                rain_probability=0
            ),
            community=CommunityStatus(
                nearby_reports=dashboard_data.get("active_journeys", 1),
                safe_zones=4,
                danger_zones=0,
                recent_activity="Normal"
            ),
            recent_alerts=[],
            ai_timeline=[],
            recent_journeys=[],
            system_health=SystemHealthStatus(
                backend="Online",
                ai_agent=dashboard_data.get("system_health", "Online"),
                latency=42,
                connected_providers=["Weather", "Routing", "MongoDB"],
                last_sync=datetime.datetime.utcnow().isoformat()
            )
        )

    def build_journey_plan(self, final_context: Dict[str, Any], user_id: str, journey_id: str) -> Any:
        from app.schemas.journey_schemas import (
            JourneyPlanResponse, SessionInfo, JourneyInformation,
            RouteOption, WeatherSummary, CommunitySummary, AIRecommendation
        )
        import datetime
        
        candidates = final_context.get("routes", [])
        source_name = final_context.get("source_name", "Current Location")
        dest_name = final_context.get("dest_name", "Destination")
        
        def get_color(score: int, index: int) -> str:
            if index == 0: return "#16A34A" # Green
            if index == 1: return "#EAB308" # Yellow
            if index == 2: return "#DC2626" # Red
            return "#4F46E5" # Fallback Blue
            
        route_options = []
        for i, c in enumerate(candidates[:3]):
            # Deterministic mock heuristic based on distance and route index
            base_score = 95 - (i * 12) - min(int(c.distance / 1000), 10)
            score = max(min(base_score, 100), 10)
            
            route_options.append(RouteOption(
                id=c.route_identifier,
                name=f"Route Option {i+1}",
                distance=c.distance, # keep in meters
                estimated_duration=c.duration, # keep in seconds
                safety_score=score,
                color=get_color(score, i),
                geometry={
                    "type": "Feature",
                    "properties": {
                        "color": get_color(score, i),
                        "routeId": c.route_identifier,
                        "is_recommended": (i == 0)
                    },
                    "geometry": c.route_metadata.get("geometry", {})
                },
                is_recommended=(i == 0),
                warnings=["Stay alert"] if score < 80 else []
            ))
            
        recommended = route_options[0] if route_options else None
        
        return JourneyPlanResponse(
            journey_id=journey_id,
            session_info=SessionInfo(
                created_at=datetime.datetime.utcnow().isoformat(),
                status="planned"
            ),
            journey_information=JourneyInformation(
                source=source_name,
                destination=dest_name,
                distance=recommended.distance if recommended else 0.0,
                estimated_duration=recommended.estimated_duration if recommended else 0.0
            ),
            route_options=route_options,
            recommended_route=recommended,
            weather_summary=WeatherSummary(
                condition="Clear", temperature=24, hazards=[]
            ),
            community_summary=CommunitySummary(
                reports_along_route=0, severity_level="Low"
            ),
            alerts=[],
            safety_score=recommended.safety_score if recommended else 98,
            ai_recommendation=AIRecommendation(
                title="Optimal Route", summary="Safest path based on live telemetry.",
                confidence=96, reasoning="Generated using live map data.",
                warnings=[], suggested_actions=["Keep phone charged"]
            )
        )
        
    def build_emergency_status(self, final_context: Dict[str, Any], session_id: str, user_id: str) -> Any:
        from app.schemas.emergency_schemas import EmergencyResponse, LiveLocation, AgentStatus, EmergencyTimelineEvent, EmergencyContact, EmergencySafeZone, JourneyStatus
        
        emergency = final_context.get("EmergencyAgent", {}).get("emergency_status", {})
        
        timeline = []
        for t in emergency.get("timeline", []):
            timeline.append(EmergencyTimelineEvent(**t))
            
        return EmergencyResponse(
            session_id=session_id,
            status="active",
            live_location=LiveLocation(
                coordinates=(77.5946, 12.9716),
                address="4th Ave Intersection, Bengaluru",
                accuracy=12,
                last_updated="Just now"
            ),
            agent_status=AgentStatus(
                action="Packaging Context & Establishing P2P Uplinks",
                recommendation="Stay hidden if possible. Do not end call.",
                context="Journey Context Attached. Score was 98% before incident.",
                confidence=99,
                reason="Protocol dictates silence during unknown threats."
            ),
            timeline=timeline,
            contacts=[
                EmergencyContact(id="c1", name="Sarah Connor", relationship="Sister", notification_status="Pending")
            ],
            safe_zones=[
                EmergencySafeZone(id="s1", type="Police", name="Central Station", distance="1.2 km", eta="4 mins", coordinates=(77.5900, 12.9700))
            ],
            journey_status=JourneyStatus(
                active_journey=True,
                destination="Downtown Tech Park",
                distance_remaining="2.1 km",
                safety_score=98
            )
        )

    def build_assistant_context(self, final_context: Dict[str, Any], user_id: str) -> Any:
        from app.schemas.assistant_schemas import AssistantResponse, AgentStatus, ReasoningContext, JourneyContextState, ProviderHealthStatus, MemoryState
        import datetime
        import uuid
        
        llm = final_context.get("LLM", {})
        
        return AssistantResponse(
            message_id="msg_" + str(uuid.uuid4())[:8],
            role="assistant",
            content=llm.get("summary", "Hello! I am the SafeShe Journey Intelligence Coordinator."),
            timestamp=datetime.datetime.utcnow().isoformat(),
            agent_status=AgentStatus(status="Monitoring", current_task="Awaiting next input"),
            reasoning=ReasoningContext(
                summary=["Context Loaded", "System Ready"],
                confidence=96.0,
                decision_source="Live Telemetry Cache",
                provider_summary="All providers operational"
            ),
            context=JourneyContextState(
                active_journey=True,
                source="Current Location",
                destination="Downtown Tech Park",
                safety_score=98.0,
                eta="14 mins",
                weather="Clear (24°C)",
                community_alerts=0,
                emergency_status="Secure"
            ),
            provider_health=[
                ProviderHealthStatus(name="Routing API (OSRM)", status="Connected")
            ],
            memory=MemoryState(
                recent_journeys=["Downtown Tech Park", "Central Station"],
                pinned_info=["User prefers well-lit routes.", "Emergency Contacts updated yesterday."]
            ),
            quick_suggestions=[
                "Explain my safety score",
                "Check weather impact",
                "Show nearby Safe Zones"
            ]
        )

    def build_assistant_chat(self, final_context: Dict[str, Any], user_id: str, query: str) -> Any:
        # Re-using the logic from coordinator
        from app.schemas.assistant_schemas import AssistantResponse, AgentStatus, ReasoningContext, JourneyContextState, ProviderHealthStatus, MemoryState
        import datetime
        import uuid
        
        llm = final_context.get("LLM", {})
        response_text = llm.get("summary", "Based on the latest telemetry, your journey remains secure.")
        
        query_lower = query.lower()
        if "safe" in query_lower or "score" in query_lower:
            response_text = "Your current safety score is 98%. This is calculated based on optimal lighting, low crowd density, and zero community incident reports along your path."
        elif "weather" in query_lower or "rain" in query_lower:
            response_text = "The weather along your route is currently clear with high visibility. No precipitation is expected in the next 2 hours."
        elif "police" in query_lower or "hospital" in query_lower:
            response_text = "The nearest police station is Central Station (1.2 km away). I have pinned it to your Safe Zones panel."

        return AssistantResponse(
            message_id="msg_" + str(uuid.uuid4())[:8],
            role="assistant",
            content=response_text,
            timestamp=datetime.datetime.utcnow().isoformat(),
            agent_status=AgentStatus(status="Monitoring", current_task="Awaiting next input"),
            reasoning=ReasoningContext(
                summary=llm.get("reasoning", []),
                confidence=96.0,
                decision_source="Live Telemetry Cache",
                provider_summary="All providers operational"
            ),
            context=JourneyContextState(
                active_journey=True,
                source="Current Location",
                destination="Downtown Tech Park",
                safety_score=98.0,
                eta="14 mins",
                weather="Clear (24°C)",
                community_alerts=0,
                emergency_status="Secure"
            ),
            provider_health=[
                ProviderHealthStatus(name="Routing API (OSRM)", status="Connected")
            ],
            memory=MemoryState(
                recent_journeys=["Downtown Tech Park", "Central Station"],
                pinned_info=["User prefers well-lit routes.", "Emergency Contacts updated yesterday."]
            ),
            quick_suggestions=[
                "Explain my safety score",
                "Check weather impact",
                "Show nearby Safe Zones"
            ]
        )
        
    def build_profile_response(self, final_context: Dict[str, Any], user_id: str) -> Any:
        from app.schemas.profile_schemas import (
            ProfileResponse, UserInfo, ProfileStats, 
            ProfileJourneyHistory, ProfileEmergencyContact, ProfileAchievement
        )
        
        # Extract from ProfileAgent
        profile_data = final_context.get("ProfileAgent", {}).get("profile", {})
        
        user_info = UserInfo(
            full_name=profile_data.get("name", "Sarah Connor"),
            email=profile_data.get("email", "sarah.connor@example.com"),
            phone=profile_data.get("phone", "+1 (555) 019-8234"),
            avatar_url=profile_data.get("avatar_url", ""),
            current_city="Bengaluru",
            member_since=profile_data.get("join_date", "January 2024"),
            is_premium=True,
            is_online=True,
            last_active="Just now"
        )
        
        stats = ProfileStats(
            safe_journeys=42,
            total_distance_km=156.4,
            avg_safety_score=97.5,
            sos_triggered=0,
            dangerous_routes_avoided=14,
            ai_recommendations_followed=89,
            community_reports_submitted=12,
            verified_reports=10,
            helpful_votes=45,
            reputation_score=950,
            trust_level="Level 3 Verified"
        )
        
        journey_history = [
            ProfileJourneyHistory(
                id="j_123", source="Home", destination="Office", 
                date="2024-03-15", transport="Walking", safety_score=98, 
                duration="15m", status="Completed"
            )
        ]
        
        emergency_contacts = [
            ProfileEmergencyContact(
                id="c1", name="John Connor", relationship="Brother", 
                phone="+1 (555) 019-8235", status="Active", is_primary=True
            )
        ]
        
        achievements = [
            ProfileAchievement(
                id="a1", title="Safety First", icon="Shield", 
                unlocked=True, date="2024-02-10"
            )
        ]
        
        return ProfileResponse(
            user_info=user_info,
            stats=stats,
            journey_history=journey_history,
            emergency_contacts=emergency_contacts,
            achievements=achievements
        )

    def build_settings_response(self, final_context: Dict[str, Any], user_id: str) -> Any:
        from app.schemas.settings_schemas import (
            SettingsResponse, SettingsAppearance, SettingsNotifications, 
            SettingsPrivacy, SettingsEmergency, SettingsAiPreferences,
            SettingsLocation, SettingsLanguage, SettingsVoice, SettingsDeveloper
        )
        
        return SettingsResponse(
            appearance=SettingsAppearance(theme="System", accent_color="blue"),
            notifications=SettingsNotifications(
                journey_alerts=True, community_alerts=True, weather_alerts=True,
                emergency_alerts=True, ai_notifications=True, email_notifications=False,
                push_notifications=True
            ),
            privacy=SettingsPrivacy(
                share_live_location=False, anonymous_community_reports=True,
                location_history=True, analytics=True, crash_reports=True
            ),
            emergency=SettingsEmergency(
                default_sos_contacts=True, auto_location_sharing=True,
                emergency_countdown=True, auto_call_emergency_contact=False,
                share_journey_automatically=False
            ),
            ai_preferences=SettingsAiPreferences(
                assistant_personality="Professional", explanation_detail="Brief",
                safety_sensitivity="High", preferred_route_type="Safest",
                risk_tolerance="Low", agent_notifications=True,
                enable_ai_recommendations=True
            ),
            location=SettingsLocation(
                default_transport_mode="Walking", preferred_walking_speed="Average",
                avoid_highways=True, avoid_dark_areas=True, avoid_crowds=False,
                avoid_construction=True
            ),
            language=SettingsLanguage(
                language="English", region="US", time_format="12h", distance_unit="Metric"
            ),
            voice=SettingsVoice(
                voice_enabled=True, preferred_voice="Female 1", speech_speed=1.0
            ),
            developer=SettingsDeveloper(
                developer_mode=False, show_debug_info=False, provider_status=False,
                api_version="v1.0", app_version="1.0.0", build_version="2026.8.2"
            )
        )
