from abc import ABC, abstractmethod
from typing import List

class BaseSafetyModel(ABC):
    """
    Abstract base class for all machine learning models in the safety pipeline.
    Ensures that the Agent doesn't need to know the underlying implementation.
    """
    
    @abstractmethod
    def predict(self, features: List[float]) -> float:
        pass


class XGBoostSafetyModel(BaseSafetyModel):
    """
    A concrete implementation representing an XGBoost model.
    In a real-world scenario, this would load a .pkl or ONNX file.
    For this prototype, it uses a weighted heuristic simulating the model's behavior.
    """
    
    def predict(self, features: List[float]) -> float:
        """
        Features expected: [time_feat, weather_feat, crowd_feat, police_feat]
        Returns a safety score from 0.0 to 1.0 (or mapped to 0-100).
        
        # [ML MODEL BOUNDARY]
        # TODO: Replace the heuristic below with actual model inference.
        # Example:
        # model = joblib.load("safety_xgboost.pkl")
        # return model.predict([features])[0]
        """
        if len(features) < 4:
            return 50.0  # Safe default fallback

        time_feat, weather_feat, crowd_feat, police_feat = features[:4]
        
        # Simulated XGBoost decision boundaries/weights
        # Police presence is highly weighted for safety
        # Bad weather reduces safety
        # High crowd density increases safety in daylight, decreases at night
        
        base_score = 0.5
        
        # Police adds up to +0.3
        police_impact = police_feat * 0.3
        
        # Weather adds up to +0.2 (Clear = +0.2, Storm = 0.0)
        weather_impact = weather_feat * 0.2
        
        # Time and crowd interaction
        is_night = time_feat < 0.25 or time_feat > 0.8  # Before 6 AM or after 7 PM
        if is_night:
            # At night, high crowd density might be slightly less safe depending on context,
            # but generally "eyes on the street" is good.
            crowd_impact = crowd_feat * 0.1
            time_penalty = -0.2
        else:
            crowd_impact = crowd_feat * 0.2
            time_penalty = 0.0
            
        raw_score = base_score + police_impact + weather_impact + crowd_impact + time_penalty
        
        # Clamp to 0-1
        clamped_score = max(0.0, min(1.0, raw_score))
        
        # Return as 0-100 score
        return round(clamped_score * 100, 2)
