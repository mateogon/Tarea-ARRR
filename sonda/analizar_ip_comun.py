import pandas as pd
import itertools

# Load forward and reverse CSVs
forward_csv = "measurement_results.csv"
reverse_csv = "reverse_measurement_results.csv"

# Read the CSVs into DataFrames
forward_df = pd.read_csv(forward_csv)
reverse_df = pd.read_csv(reverse_csv)

# Merge the forward and reverse data
merged_df = pd.merge(
    forward_df,
    reverse_df,
    on=["IP"],
    suffixes=("_forward", "_reverse"),
    how="inner"
)

# Analyze common IPs
common_ips = merged_df[["IP", "ASN_forward", "ASN_reverse", "Protocol_forward", "Protocol_reverse"]]
print("Common IPs between forward and reverse measurements:")
print(common_ips)

# Function to determine if two IPs belong to the same device
def check_same_device(ip1, ip2, asn1, asn2):
    return asn1 == asn2

# Pairwise comparison to identify IP pairs potentially belonging to the same device
potential_same_device_pairs = []
for target, group in forward_df.groupby("Target"):
    reverse_ips = reverse_df[reverse_df["Target"] == target]["IP"]
    for ip1, ip2 in itertools.combinations(reverse_ips, 2):
        asn1 = reverse_df[reverse_df["IP"] == ip1]["ASN"].values[0]
        asn2 = reverse_df[reverse_df["IP"] == ip2]["ASN"].values[0]
        if check_same_device(ip1, ip2, asn1, asn2):
            potential_same_device_pairs.append((ip1, ip2, asn1))

# Convert the pairs into a DataFrame for better visualization
pairs_df = pd.DataFrame(potential_same_device_pairs, columns=["IP1", "IP2", "ASN"])
print("\nPotential pairs of IPs belonging to the same device:")
print(pairs_df)

# Save the analysis results
common_ips.to_csv("common_ips_analysis.csv", index=False)
pairs_df.to_csv("same_device_pairs.csv", index=False)

# Summary comparison of routes
route_summary = pd.concat(
    [
        forward_df.groupby(["Target", "Protocol"]).size().rename("Forward Route IPs"),
        reverse_df.groupby(["Target", "Protocol"]).size().rename("Reverse Route IPs"),
    ],
    axis=1,
)
print("\nRoute comparison summary (forward vs reverse):")
print(route_summary)

# Save the route comparison summary
route_summary.to_csv("route_comparison_summary.csv", index=True)
