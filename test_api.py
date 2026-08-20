import requests
import json

response = requests.post("http://localhost:8000/api/v1/journeys/", json={"source": "77.5946, 12.9716", "destination": "77.5800, 12.9800"})
with open("test_api.json", "w") as f:
    json.dump(response.json(), f, indent=2)
