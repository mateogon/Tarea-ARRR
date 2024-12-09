import requests
import time
import json
import csv

# Configuration
RIPE_ATLAS_API_KEY = '0c49dc2f-35a2-46f7-a911-a5dad9d3796a'
TARGETS = [
    "185.131.204.20",
    "5.161.76.19",
    "80.77.4.60",
    "130.104.228.159",
]
PROTOCOLS = ["ICMP", "UDP", "TCP"]

# New reverse measurement IDs
REVERSE_MEASUREMENT_IDS = {
    "ICMP": [84195577, 84196553, 84196563, 84196572],
    "UDP": [84195580, 84196556, 84196565, 84196574],
    "TCP": [84195582, 84196558, 84196567, 84196576],
}

# Global cache for ASN queries
asn_query_counter = {}
asn_cache = {}

# Fetch measurement results
def fetch_measurement_results(measurement_id):
    url = f"https://atlas.ripe.net/api/v2/measurements/{measurement_id}/results/"
    response = requests.get(url, headers={"Authorization": f"Key {RIPE_ATLAS_API_KEY}"})
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 1))  # Wait and retry
        print(f"[Rate limited] Measurement ID: {measurement_id}, waiting {retry_after} seconds...")
        time.sleep(retry_after)
        return fetch_measurement_results(measurement_id)
    else:
        print(f"Error fetching results for measurement {measurement_id}: {response.status_code}")
        return None

# Get AS for IP using bgpview API
def get_as_for_ip(ip):
    if ip in asn_cache:
        return asn_cache[ip]

    if ip not in asn_query_counter:
        asn_query_counter[ip] = 0
    asn_query_counter[ip] += 1

    bgp_url = f"https://api.bgpview.io/ip/{ip}"
    response = requests.get(bgp_url)
    if response.status_code == 200:
        data = response.json()
        if data.get("data", {}).get("prefixes"):
            asn = data["data"]["prefixes"][0]["asn"]["asn"]
            asn_cache[ip] = asn
            return asn
        else:
            asn_cache[ip] = "No AS found"
            return "No AS found"
    elif response.status_code == 429:
        print(f"[Rate limited] Querying IP: {ip}, total queries: {asn_query_counter[ip]}. Waiting 5 seconds...")
        time.sleep(5)
        return get_as_for_ip(ip)
    else:
        asn_cache[ip] = f"Error: {response.status_code}"
        return f"Error: {response.status_code}"

# Analyze results
def analyze_results(results):
    ip_hops = {}
    for result in results:
        for hop in result.get("result", []):
            if "result" in hop:
                for probe in hop["result"]:
                    if "from" in probe:
                        ip = probe["from"]
                        asn = get_as_for_ip(ip)
                        if ip not in ip_hops:
                            ip_hops[ip] = {"asn": asn, "count": 1}
                        else:
                            ip_hops[ip]["count"] += 1
    return ip_hops

# Save to JSON
def save_to_json(data, filename="reverse_measurement_results.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Results saved to {filename}")

# Save to CSV
def save_to_csv(data, filename="reverse_measurement_results.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Protocol", "Target", "IP", "ASN", "Occurrences"])
        for protocol, targets in data.items():
            for target, hops in targets.items():
                for ip, details in hops.items():
                    writer.writerow([protocol, target, ip, details["asn"], details["count"]])
    print(f"Results saved to {filename}")

# Generate a summary report
def generate_report(measurements_data):
    report = {}
    for protocol, data in measurements_data.items():
        for target, result in data.items():
            unique_ips = len(set(result.keys()))
            report[(protocol, target)] = unique_ips
    return report

# Process reverse measurements
def process_reverse_measurements():
    measurements_data = {}
    for protocol, ids in REVERSE_MEASUREMENT_IDS.items():
        measurements_data[protocol] = {}
        for target, measurement_id in zip(TARGETS, ids):
            print(f"Processing reverse measurement {protocol} for {target} (ID: {measurement_id})...")
            results = fetch_measurement_results(measurement_id)
            if results:
                ip_hops = analyze_results(results)
                measurements_data[protocol][target] = ip_hops
            time.sleep(1)  # Rate limiting between measurements

    # Save results
    save_to_json(measurements_data)
    save_to_csv(measurements_data)

    report = generate_report(measurements_data)

    # Print summary
    print("\n--- Reverse Measurement Summary ---\n")
    for (protocol, target), count in report.items():
        print(f"{protocol} for {target}: {count} unique IPs detected")

    # Print detailed results
    for protocol, targets in measurements_data.items():
        print(f"\n--- Details for {protocol} ---")
        for target, hops in targets.items():
            print(f"\nTarget: {target}")
            for ip, data in hops.items():
                print(f"IP: {ip}, ASN: {data['asn']}, Occurrences: {data['count']}")

    # Print API query counts
    print("\n--- ASN API Query Count ---")
    for ip, count in asn_query_counter.items():
        print(f"IP: {ip}, Queries made: {count}")

if __name__ == "__main__":
    process_reverse_measurements()
