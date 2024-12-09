import requests
import json
import time

API_KEY = "2995e090-02db-43ee-b6ca-1282e6f6a0cc"  # Replace with your actual RIPE Atlas API key

# Target IPs
TARGET_IPS = [
    "185.131.204.20",
    "5.161.76.19",
    "80.77.4.60",
    "130.104.228.159"
]

# Measurement types
MEASUREMENT_TYPES = ["ping", "traceroute", "http"]

# Probe settings
PROBE_SETTINGS = {
    "requested": 5,
    "type": "area",
    "value": "WW"  # Use worldwide probes
}

# API endpoint
API_URL = "https://atlas.ripe.net/api/v2/measurements/"

def create_measurement(target, measurement_type):
    """
    Create a measurement in RIPE Atlas.
    """
    payload = {
        "definitions": [
            {
                "target": target,
                "description": f"{measurement_type.upper()} measurement to {target}",
                "type": measurement_type,
                "af": 4  # IPv4
            }
        ],
        "probes": [PROBE_SETTINGS],
        "is_oneoff": True
    }

    headers = {
        "Authorization": f"Key {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    if response.status_code == 201:
        measurement_id = response.json()["measurements"][0]
        print(f"Measurement created: {measurement_id} for {measurement_type} to {target}")
        return measurement_id
    else:
        print(f"Error creating measurement for {target} ({measurement_type}): {response.text}")
        return None

def fetch_measurement_results(measurement_id):
    """
    Fetch results of a measurement.
    """
    results_url = f"{API_URL}{measurement_id}/results/"
    headers = {"Authorization": f"Key {API_KEY}"}
    response = requests.get(results_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching results for {measurement_id}: {response.text}")
        return None

def main():
    # Dictionary to store measurement IDs
    measurements = {}

    # Create measurements
    for target in TARGET_IPS:
        measurements[target] = {}
        for measurement_type in MEASUREMENT_TYPES:
            measurement_id = create_measurement(target, measurement_type)
            if measurement_id:
                measurements[target][measurement_type] = measurement_id

    # Wait for measurements to complete
    print("Waiting for measurements to complete...")
    time.sleep(300)  # Adjust waiting time as needed

    # Fetch and save results
    for target, types in measurements.items():
        for measurement_type, measurement_id in types.items():
            results = fetch_measurement_results(measurement_id)
            if results:
                filename = f"{target.replace('.', '_')}_{measurement_type}_results.json"
                with open(filename, "w") as f:
                    json.dump(results, f, indent=4)
                print(f"Results saved to {filename}")

if __name__ == "__main__":
    main()
