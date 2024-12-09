import pandas as pd
import matplotlib.pyplot as plt

# Load the sorted summary CSV
df = pd.read_csv("resultados/summary_analysis_sorted.csv")

# Extract Protocol Data
protocols = df["Protocols"].str.extract(r"\{(\d+): (\d+)\}").astype(int)
protocols.columns = ["Protocol", "Count"]

# Summarize protocol counts
protocol_summary = protocols.groupby("Protocol")["Count"].sum()

# Map protocol numbers to names
protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
protocol_summary.index = protocol_summary.index.map(protocol_map)

# Plot protocol distribution
protocol_summary.plot(kind="bar", figsize=(8, 6), color="skyblue")
plt.title("Protocol Distribution Across Methods")
plt.ylabel("Total Packets")
plt.xlabel("Protocol")
plt.tight_layout()
plt.savefig("protocol_distribution.png")
print("Protocol distribution analysis saved as protocol_distribution.png")
