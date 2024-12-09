# analyze_combined_ttl_packet_trend.py
import pandas as pd
import matplotlib.pyplot as plt

# Cargar el archivo CSV ordenado
df = pd.read_csv("resultados/summary_analysis_sorted.csv")

# Agrupar por IP y Método para analizar Total de Paquetes y TTL Medio
summary = df.groupby(["IP", "Method"])[["Total Packets", "TTL Mean"]].mean().unstack()

# Gráfico combinado por IP
for ip in summary.index:
    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Gráfico: Total de paquetes
    summary.loc[ip, "Total Packets"].plot(kind="bar", ax=axes[0], color="skyblue")
    axes[0].set_title(f"Total de paquetes por método para IP {ip}")
    axes[0].set_ylabel("Total de paquetes")
    axes[0].tick_params(axis="x", rotation=45)

    # Gráfico: TTL Medio
    summary.loc[ip, "TTL Mean"].plot(kind="bar", ax=axes[1], color="orange")
    axes[1].set_title(f"TTL promedio por método para IP {ip}")
    axes[1].set_ylabel("TTL Promedio")
    axes[1].tick_params(axis="x", rotation=45)

    # Ajustar diseño
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.suptitle(f"Análisis combinado: Total de paquetes y TTL medio para IP {ip}", fontsize=14, y=1.02)

    # Guardar el gráfico
    plt.savefig(f"analisis_combinado_{ip.replace('.', '_')}.png")
    plt.close()
    print(f"Gráfico combinado guardado para IP {ip} como analisis_combinado_{ip.replace('.', '_')}.png")
