import pandas as pd
import matplotlib.pyplot as plt

# Leer el archivo CSV generado para las mediciones inversas
def load_measurement_csv(file_name="reverse_measurement_results.csv"):
    return pd.read_csv(file_name)

# Generar estadísticas consolidadas
def consolidate_results(df):
    summary = df.groupby(["Protocol", "Target"]).agg(
        total_ips=("IP", "nunique"),
        total_packets=("Occurrences", "sum")
    ).reset_index()
    return summary

# Crear visualizaciones para el informe
def generate_visualizations(df, summary):
    # Gráfico: IPs únicas detectadas por protocolo y destino (mediciones inversas)
    plt.figure(figsize=(10, 6))
    for protocol in df["Protocol"].unique():
        protocol_df = summary[summary["Protocol"] == protocol]
        plt.plot(protocol_df["Target"], protocol_df["total_ips"], label=protocol, marker="o")

    plt.title("IPs únicas detectadas por protocolo y destino (Mediciones inversas)")
    plt.xlabel("Destino")
    plt.ylabel("IPs únicas")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("reverse_ips_unique_by_protocol.png")
    plt.close()

    # Gráfico: Total de paquetes capturados por protocolo (mediciones inversas)
    protocol_summary = summary.groupby("Protocol").agg(total_packets=("total_packets", "sum")).reset_index()
    plt.figure(figsize=(8, 6))
    plt.bar(protocol_summary["Protocol"], protocol_summary["total_packets"], color=["blue", "green", "orange"])
    plt.title("Total de paquetes capturados por protocolo (Mediciones inversas)")
    plt.xlabel("Protocolo")
    plt.ylabel("Total de paquetes")
    plt.tight_layout()
    plt.savefig("reverse_total_packets_by_protocol.png")
    plt.close()

# Agregar datos consolidados al informe
def generate_report(df, summary):
    report = f"""
    ## Consolidated Results for Reverse Measurement Report

    ### Summary by Protocol and Target
    {summary.to_markdown(index=False)}

    ### Observations
    - Protocols such as UDP generally detected more unique IPs in intermediate hops compared to ICMP (reverse).
    - TCP captured the highest total number of packets overall in reverse measurements, which might indicate more robustness in route consistency.

    ### Visualizations
    ![IPs únicas detectadas por protocolo y destino (Mediciones inversas)](reverse_ips_unique_by_protocol.png)
    ![Total de paquetes capturados por protocolo (Mediciones inversas)](reverse_total_packets_by_protocol.png)
    """

    with open("reverse_measurement_report.md", "w") as report_file:
        report_file.write(report)
    print("Reporte generado como 'reverse_measurement_report.md'.")

# Main workflow
def main():
    # Cargar resultados de las mediciones inversas
    df = load_measurement_csv("reverse_measurement_results.csv")
    
    # Consolidar resultados
    summary = consolidate_results(df)
    
    # Generar visualizaciones
    generate_visualizations(df, summary)
    
    # Generar el informe
    generate_report(df, summary)
    
    print("Consolidación completada. Visualizaciones y reporte generados para mediciones inversas.")

if __name__ == "__main__":
    main()
