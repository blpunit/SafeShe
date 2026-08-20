from typing import Dict, Any, List

class FeatureEngineer:
    def engineer_features(self, normalized_data: Dict[str, Any]) -> List[float]:
        """
        Transforms normalized provider data into a feature vector for the ML model.
        """
        features = [
            normalized_data.get("distance_km", 0.0),
            float(normalized_data.get("eta_mins", 0.0)),
            24.0 if normalized_data.get("weather_condition") == "Clear" else 12.0,
            float(normalized_data.get("total_community_reports", 0)),
            1.0 # Bias term or user preference weight
        ]
        return features
