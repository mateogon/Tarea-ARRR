import pandas as pd
import requests
import re
from ipwhois import IPWhois
from ipwhois.exceptions import IPDefinedError

def is_private_ip(ip):
    private_ip_patterns = [
        r'^10\.',
        r'^172\.(1[6-9]|2[0-9]|3[01])\.',
        r'^192\.168\.',
        r'^169\.254\.',
        r'^127\.0\.0\.',
    ]
    for pattern in private_ip_patterns:
        if re.match(pattern, ip):
            return True
    return False

def get_asn_and_organization(ip):
    if is_private_ip(ip):
        return "Private IP", "Private Network"
    try:
        obj = IPWhois(ip)
        results = obj.lookup_rdap()
        asn = results.get("asn", "Unknown")
        organization = results.get("asn_description", "Unknown")
        return asn, organization
    except IPDefinedError:
        return "Reserved/Bogon", "Reserved/Bogon"
    except Exception as e:
        print(f"Error retrieving ASN for {ip}: {e}")
        return "Unknown", "Unknown"

def get_geoip(ip):
    if is_private_ip(ip):
        return "Private IP"
    try:
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data["status"] == "success":
            country = data.get("country", "Unknown")
            region = data.get("regionName", "Unknown")
            city = data.get("city", "Unknown")
            lat = data.get("lat", "Unknown")
            lon = data.get("lon", "Unknown")
            return f"{country}, {region}, {city} - ({lat}, {lon})"
        else:
            return "Unknown"
    except Exception as e:
        print(f"Error retrieving GeoIP for {ip}: {e}")
        return "Unknown"

def get_network_type(asn_description):
    if "backbone" in asn_description.lower():
        return "Backbone Network"
    elif "isp" in asn_description.lower() or "telecom" in asn_description.lower():
        return "ISP Network"
    elif "enterprise" in asn_description.lower() or "corporate" in asn_description.lower():
        return "Corporate Network"
    elif "university" in asn_description.lower() or "academic" in asn_description.lower():
        return "Academic Network"
    else:
        return "General Network"

def parse_route_data(raw_data):
    rows = []
    for ip, details in raw_data.items():
        if isinstance(details, dict):  # Ensure `details` is a dictionary
            rows.append({
                "Hop": ip,
                "IP": ip,
                "ASN": details.get("asn", "Unknown"),
                "Occurrences": details.get("count", 0)
            })
        else:
            print(f"Skipping malformed entry: {ip} -> {details}")
    return pd.DataFrame(rows)

def enrich_route_data(df):
    df["ASN"] = ""
    df["Organization"] = ""
    df["GeoIP"] = ""
    df["Network Type"] = ""

    for index, row in df.iterrows():
        ip = row["IP"]
        print(f"Processing IP: {ip}")

        if is_private_ip(ip):
            asn = "Private IP"
            organization = "Private Network"
            geoip = "Private IP"
            network_type = "Private Network"
        else:
            asn, organization = get_asn_and_organization(ip)
            geoip = get_geoip(ip)
            network_type = get_network_type(organization)

        df.at[index, "ASN"] = asn
        df.at[index, "Organization"] = organization
        df.at[index, "GeoIP"] = geoip
        df.at[index, "Network Type"] = network_type

    return df

def main():
    # Example input: Replace with actual route data
    route_data = {
        "172.17.0.1": {"asn": "No AS found", "count": 3},
        "192.168.1.1": {"asn": "No AS found", "count": 3},
        "191.112.0.1": {"asn": 7418, "count": 3},
        "10.50.3.21": {"asn": "No AS found", "count": 2},
        "10.50.3.9": {"asn": "No AS found", "count": 1},
        "10.50.3.22": {"asn": "No AS found", "count": 3},
        "5.53.0.144": {"asn": 12956, "count": 2},
        "213.140.43.234": {"asn": 12956, "count": 2},
        "62.115.120.176": {"asn": 1299, "count": 3},
        "62.115.136.200": {"asn": 1299, "count": 1},
        "62.115.112.71": {"asn": 1299, "count": 3},
        "62.115.57.79": {"asn": 1299, "count": 3},
        "85.95.26.222": {"asn": 15412, "count": 3},
        "62.216.128.214": {"asn": 15412, "count": 3},
        "62.216.131.154": {"asn": 15412, "count": 3},
        "85.95.25.93": {"asn": 15412, "count": 3},
        "80.77.4.60": {"asn": 15412, "count": 3},
    }

    # Parse the route data into a DataFrame
    raw_df = parse_route_data(route_data)
    print("Parsed Route Data:")
    print(raw_df)

    # Enrich the DataFrame with metadata
    enriched_df = enrich_route_data(raw_df)

    # Save the enriched data to a CSV
    enriched_df.to_csv("enriched_route_data.csv", index=False)
    print("\nEnriched route data saved to 'enriched_route_data.csv'.")
    print(enriched_df.head())

if __name__ == "__main__":
    main()
