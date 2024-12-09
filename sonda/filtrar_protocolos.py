import pyshark
import os
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from fpdf import FPDF

# Directories
PCAP_DIR = "./captures"  # Path to pcap files
OUTPUT_DIR = "./report"  # Directory to store the consolidated report

# Protocol Filters
PROTOCOL_FILTERS = {
    "ICMP": "icmp",
    "UDP": "udp",
    "TCP": "tcp"
}

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Traffic Analysis Report", align="C", ln=True)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True, align="L")
        self.ln(5)

    def chapter_body(self, body):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, body)
        self.ln(10)

def analyze_pcap(pcap_file, protocol):
    """
    Analyze the traffic pattern for a specific protocol in a pcap file.
    """
    print(f"Analyzing {pcap_file} for {protocol}...")
    protocol_filter = PROTOCOL_FILTERS[protocol]
    capture = pyshark.FileCapture(pcap_file, display_filter=protocol_filter)

    packet_details = []
    try:
        for packet in capture:
            packet_info = {
                "time": float(packet.sniff_timestamp),
                "length": int(packet.length),
                "src_ip": packet.ip.src if hasattr(packet, 'ip') else None,
                "dst_ip": packet.ip.dst if hasattr(packet, 'ip') else None
            }
            packet_details.append(packet_info)
    except Exception as e:
        print(f"Error processing {pcap_file} for {protocol}: {e}")
    finally:
        capture.close()

    if not packet_details:
        print(f"No {protocol} packets found in {pcap_file}.")
        return None

    # Convert to DataFrame
    df = pd.DataFrame(packet_details)
    df["time_diff"] = df["time"].diff()

    # Summary Statistics
    total_packets = len(df)
    avg_packet_size = df["length"].mean()
    avg_time_diff = df["time_diff"].mean()
    size_distribution = df["length"].value_counts()

    return {
        "df": df,
        "total_packets": total_packets,
        "avg_packet_size": avg_packet_size,
        "avg_time_diff": avg_time_diff,
        "size_distribution": size_distribution
    }

def generate_plots(size_distribution, protocol, pcap_name):
    """
    Generate a bar plot for packet size distribution.
    """
    plt.figure()
    size_distribution.sort_index().plot(kind='bar')
    plt.title(f"Packet Size Distribution - {protocol} ({pcap_name})")
    plt.xlabel("Packet Size (bytes)")
    plt.ylabel("Count")
    plot_file = os.path.join(OUTPUT_DIR, f"{pcap_name}_{protocol}_distribution.png")
    plt.savefig(plot_file)
    plt.close()
    return plot_file

def process_pcaps_and_generate_report():
    """
    Process all pcap files, analyze traffic, and generate a consolidated PDF report.
    """
    pdf = PDFReport()
    pdf.add_page()

    summary_data = []

    for pcap_file in os.listdir(PCAP_DIR):
        if not pcap_file.endswith(".pcap"):
            continue
        pcap_path = os.path.join(PCAP_DIR, pcap_file)
        pdf.chapter_title(f"Analysis for {pcap_file}")

        for protocol in PROTOCOL_FILTERS.keys():
            filtered_pcap = os.path.join(OUTPUT_DIR, f"{os.path.basename(pcap_file)}_{protocol}.pcap")

            # Filter packets by protocol using tshark
            print(f"Filtering {pcap_file} for {protocol}...")
            os.system(f"tshark -r {pcap_path} -Y {PROTOCOL_FILTERS[protocol]} -w {filtered_pcap}")

            # Analyze the filtered pcap
            analysis = analyze_pcap(filtered_pcap, protocol)
            if not analysis:
                continue

            # Summary for report
            summary_data.append({
                "pcap": pcap_file,
                "protocol": protocol,
                "total_packets": analysis["total_packets"],
                "avg_packet_size": analysis["avg_packet_size"],
                "avg_time_diff": analysis["avg_time_diff"]
            })

            # Add details to PDF
            pdf.chapter_body(
                f"Protocol: {protocol}\n"
                f"Total Packets: {analysis['total_packets']}\n"
                f"Average Packet Size: {analysis['avg_packet_size']:.2f} bytes\n"
                f"Average Time Difference: {analysis['avg_time_diff']:.6f} seconds\n"
            )

            # Generate and add plot
            plot_file = generate_plots(analysis["size_distribution"], protocol, pcap_file)
            pdf.image(plot_file, w=150)

    # Save PDF report
    report_file = os.path.join(OUTPUT_DIR, "Traffic_Analysis_Report.pdf")
    pdf.output(report_file)
    print(f"Report generated at {report_file}")

    # Generate consolidated summary CSV
    summary_df = pd.DataFrame(summary_data)
    summary_csv = os.path.join(OUTPUT_DIR, "Traffic_Analysis_Summary.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"Summary saved at {summary_csv}")

if __name__ == "__main__":
    process_pcaps_and_generate_report()
