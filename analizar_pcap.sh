#!/bin/bash

# Directories
PCAP_DIR="resultados/pcap"
OUTPUT_DIR="resultados/csv"

# Create output directory if it doesn't exist
mkdir -p $OUTPUT_DIR

# Process each .pcap file
for pcap in $PCAP_DIR/*.pcap; do
  # Extract base name
  base_name=$(basename "$pcap" .pcap)

  # Use tshark to extract fields and save as CSV
  tshark -r "$pcap" -T fields \
    -e ip.src -e ip.dst -e ip.proto -e frame.len -e ip.ttl \
    -E header=y -E separator=, \
    > "$OUTPUT_DIR/${base_name}.csv"

  echo "Extracted data from $pcap to $OUTPUT_DIR/${base_name}.csv"
done

echo "Extraction complete. CSV files saved in $OUTPUT_DIR."
