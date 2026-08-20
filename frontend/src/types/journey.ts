export interface JourneyCreateRequest {
  source: string; 
  destination: string;
  preferences?: string[]; 
}

export interface RouteOption {
  id: string;
  name: string;
  distance: number; // meters
  estimated_duration: number; // seconds
  safety_score: number;
  color: string;
  geometry: any; // GeoJSON
  is_recommended: boolean;
  warnings: string[];
}

export interface AIRecommendation {
  title: string;
  summary: string;
  confidence: number;
  reasoning: string;
  warnings: string[];
  suggested_actions: string[];
}

export interface JourneyPlanResponse {
  journey_id: string;
  session_info: {
    created_at: string;
    status: string;
  };
  journey_information: {
    source: string;
    destination: string;
    distance: number;
    estimated_duration: number;
  };
  route_options: RouteOption[];
  recommended_route: RouteOption;
  weather_summary: {
    condition: string;
    temperature: number;
    hazards: string[];
  };
  community_summary: {
    reports_along_route: number;
    severity_level: string;
  };
  alerts: string[];
  safety_score: number;
  ai_recommendation: AIRecommendation;
}
