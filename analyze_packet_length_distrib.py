# analyze_packet_length_distrib.py
import pandas as pd
import matplotlib.pyplot as plt

# Cargar el archivo CSV ordenado
df = pd.read_csv("resultados/summary_analysis_sorted.csv")

# Agrupar por método y analizar longitudes de paquetes
frame_lengths = df.groupby("Method")[["Frame Length Min", "Frame Length Max", "Frame Length Mean"]].mean()

# Gráfico: Longitud media de paquetes por método
frame_lengths["Frame Length Mean"].plot(kind="bar", figsize=(8, 6), color="green")
plt.title("Longitud promedio de paquetes por método")
plt.ylabel("Longitud (bytes)")
plt.xlabel("Método")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("longitud_promedio_paquetes_por_metodo.png")
plt.close()

print("Análisis de longitud de paquetes guardado como longitud_promedio_paquetes_por_metodo.png")
