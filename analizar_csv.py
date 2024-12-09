import os
import pandas as pd

# Directory containing the CSV files
INPUT_DIR = "resultados/csv"
OUTPUT_FILE = "resultados/summary_analysis_sorted.csv"

# Initialize a list to hold summary data
summary_data = []

# Process each CSV file in the directory
for csv_file in os.listdir(INPUT_DIR):
    if csv_file.endswith(".csv"):
        file_path = os.path.join(INPUT_DIR, csv_file)
        print(f"Processing {csv_file}...")
        
        # Load the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        
        # Extract the IP and method from the filename
        method = csv_file.split("_")[0]  # Extract the method (e.g., "icmp", "tcp")
        ip = csv_file.split("_", 1)[1].replace(".csv", "").replace("_", ".")  # Extract the IP (e.g., "185.131.204.20")
        
        # Extract required metrics
        protocol_counts = df['ip.proto'].value_counts().to_dict()
        unique_src_ips = df['ip.src'].nunique()
        unique_dst_ips = df['ip.dst'].nunique()
        ttl_stats = df['ip.ttl'].agg(['min', 'max', 'mean']).to_dict()
        frame_stats = df['frame.len'].agg(['min', 'max', 'mean']).to_dict()
        
        # Add data to summary
        summary_data.append({
            "File": csv_file,
            "Method": method,
            "IP": ip,
            "Total Packets": len(df),
            "Protocols": protocol_counts,
            "Unique Source IPs": unique_src_ips,
            "Unique Destination IPs": unique_dst_ips,
            "TTL Min": ttl_stats['min'],
            "TTL Max": ttl_stats['max'],
            "TTL Mean": ttl_stats['mean'],
            "Frame Length Min": frame_stats['min'],
            "Frame Length Max": frame_stats['max'],
            "Frame Length Mean": frame_stats['mean']
        })

# Convert the summary data into a DataFrame
summary_df = pd.DataFrame(summary_data)

# Sort the DataFrame by IP and Method
summary_df.sort_values(by=["IP", "Method"], inplace=True)

# Save the sorted summary as a CSV file
summary_df.to_csv(OUTPUT_FILE, index=False)
print(f"Analysis complete. Sorted summary saved to {OUTPUT_FILE}.")
