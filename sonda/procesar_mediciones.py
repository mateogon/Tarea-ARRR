import requests
import time
import json
import csv

# Configuración
RIPE_ATLAS_API_KEY = '0c49dc2f-35a2-46f7-a911-a5dad9d3796a'
TARGETS = [
    "185.131.204.20",
    "5.161.76.19",
    "80.77.4.60",
    "130.104.228.159",
]
PROTOCOLS = ["ICMP", "UDP", "TCP"]

# IDs de mediciones proporcionados
MEASUREMENT_IDS = {
    "ICMP": [84186995, 84187769, 84188531, 84189317],
    "UDP": [84186997, 84187771, 84188533, 84189320],
    "TCP": [84187000, 84187773, 84188535, 84189321],
}

# Contador de consultas a la API de ASN
asn_query_counter = {}

# Obtener resultados de las mediciones
def fetch_measurement_results(measurement_id):
    url = f"https://atlas.ripe.net/api/v2/measurements/{measurement_id}/results/"
    response = requests.get(url, headers={"Authorization": f"Key {RIPE_ATLAS_API_KEY}"})
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 1))  # Espera antes de reintentar
        print(f"[Límite alcanzado] Medición ID: {measurement_id}, esperando {retry_after} segundos...")
        time.sleep(retry_after)
        return fetch_measurement_results(measurement_id)
    else:
        print(f"Error al obtener resultados para medición {measurement_id}: {response.status_code}")
        return None

# Asociar IPs a AS utilizando la API de https://bgp.he.net/
# Global cache for IP-AS mapping
asn_cache = {}

# Asociar IPs a AS utilizando la API de https://bgp.he.net/
def get_as_for_ip(ip):
    # Check if AS is already cached
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
            asn_cache[ip] = asn  # Cache the AS
            return asn
        else:
            asn_cache[ip] = "No AS found"  # Cache the result
            return "No AS found"
    elif response.status_code == 429:
        print(f"[Límite alcanzado] Consultando IP: {ip}, total consultas: {asn_query_counter[ip]}. Esperando 5 segundos...")
        time.sleep(5)
        return get_as_for_ip(ip)
    else:
        asn_cache[ip] = f"Error: {response.status_code}"  # Cache the error
        return f"Error: {response.status_code}"


# Analizar los resultados
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

# Guardar los datos en formato JSON
def save_to_json(data, filename="measurement_results.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Resultados guardados en {filename}")

# Guardar los datos en formato CSV
def save_to_csv(data, filename="measurement_results.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Protocol", "Target", "IP", "ASN", "Occurrences"])
        for protocol, targets in data.items():
            for target, hops in targets.items():
                for ip, details in hops.items():
                    writer.writerow([protocol, target, ip, details["asn"], details["count"]])
    print(f"Resultados guardados en {filename}")

# Generar informe comparativo
def generate_report(measurements_data):
    report = {}
    for protocol, data in measurements_data.items():
        for target, result in data.items():
            unique_ips = len(set(result.keys()))
            report[(protocol, target)] = unique_ips
    return report

# Procesar las mediciones
def process_measurements():
    measurements_data = {}
    for protocol, ids in MEASUREMENT_IDS.items():
        measurements_data[protocol] = {}
        for target, measurement_id in zip(TARGETS, ids):
            print(f"Procesando medición {protocol} para {target} (ID: {measurement_id})...")
            results = fetch_measurement_results(measurement_id)
            if results:
                ip_hops = analyze_results(results)
                measurements_data[protocol][target] = ip_hops
            time.sleep(1)  # Rate limiting entre mediciones

    # Guardar resultados
    save_to_json(measurements_data)
    save_to_csv(measurements_data)

    report = generate_report(measurements_data)

    # Imprimir resumen
    print("\n--- Comparación de Resultados ---\n")
    for (protocol, target), count in report.items():
        print(f"{protocol} hacia {target}: {count} IPs únicas detectadas")

    # Generar análisis detallado
    for protocol, targets in measurements_data.items():
        print(f"\n--- Detalle para {protocol} ---")
        for target, hops in targets.items():
            print(f"\nDestino: {target}")
            for ip, data in hops.items():
                print(f"IP: {ip}, ASN: {data['asn']}, Apariciones: {data['count']}")

    # Imprimir contador de consultas
    print("\n--- Contador de Consultas a la API de ASN ---")
    for ip, count in asn_query_counter.items():
        print(f"IP: {ip}, Consultas realizadas: {count}")

if __name__ == "__main__":
    process_measurements()
