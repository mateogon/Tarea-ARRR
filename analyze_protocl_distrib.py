# analyze_protocl_distrib.py
import pandas as pd
import matplotlib.pyplot as plt

# Cargar el archivo CSV ordenado
df = pd.read_csv("resultados/summary_analysis_sorted.csv")

# Extraer datos de protocolo
protocols = df["Protocols"].str.extract(r"\{(\d+): (\d+)\}").astype(int)
protocols.columns = ["Protocolo", "Cantidad"]

# Resumir conteo de protocolos
protocol_summary = protocols.groupby("Protocolo")["Cantidad"].sum()

# Mapear los números de protocolo a nombres
protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
protocol_summary.index = protocol_summary.index.map(protocol_map)

# Gráfico: Distribución de protocolos
protocol_summary.plot(kind="bar", figsize=(8, 6), color="skyblue")
plt.title("Distribución de protocolos")
plt.ylabel("Total de paquetes")
plt.xlabel("Protocolo")
plt.tight_layout()
plt.savefig("distribucion_de_protocolos.png")
print("Análisis de distribución de protocolos guardado como distribucion_de_protocolos.png")
