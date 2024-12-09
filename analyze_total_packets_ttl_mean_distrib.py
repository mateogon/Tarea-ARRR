# analyze_total_packets_ttl_mean_distrib.py
import pandas as pd
import matplotlib.pyplot as plt

# Cargar el archivo CSV ordenado
df = pd.read_csv("resultados/summary_analysis_sorted.csv")

# Agrupar por IP para analizar Total de Paquetes y TTL Medio
summary_per_ip = df.groupby("IP")[["Total Packets", "TTL Mean"]].mean()

# Gráfico: Total de paquetes por IP de destino
summary_per_ip["Total Packets"].plot(kind="bar", figsize=(10, 6), color="orange")
plt.title("Total de paquetes por IP de destino")
plt.ylabel("Total de paquetes")
plt.xlabel("IP de destino")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("total_paquetes_por_destino.png")
plt.close()

# Gráfico: TTL medio por IP de destino
summary_per_ip["TTL Mean"].plot(kind="bar", figsize=(10, 6), color="purple")
plt.title("TTL promedio por IP de destino")
plt.ylabel("TTL Promedio")
plt.xlabel("IP de destino")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("ttl_promedio_por_destino.png")
plt.close()

print("Análisis por destino guardado como total_paquetes_por_destino.png y ttl_promedio_por_destino.png")
