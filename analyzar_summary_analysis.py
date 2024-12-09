# analyzar_summary_analysis.py
import pandas as pd
import matplotlib.pyplot as plt

# Cargar el archivo CSV ordenado
df = pd.read_csv("resultados/summary_analysis_sorted.csv")

# Gráfico: Total de paquetes por archivo
plt.figure(figsize=(10, 6))
df.plot(x='File', y='Total Packets', kind='bar', legend=False)
plt.title('Total de paquetes por archivo')
plt.ylabel('Paquetes')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("total_paquetes_por_archivo.png")
plt.close()

# Gráfico: TTL medio por método
ttl_means = df.groupby('Method')['TTL Mean'].mean()

plt.figure(figsize=(8, 6))
ttl_means.plot(kind='bar', color='skyblue')
plt.title('TTL promedio por método')
plt.ylabel('TTL Promedio')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("ttl_promedio_por_metodo.png")
plt.close()

# Imprimir información clave
print("Información clave:")
print("1. TTL promedio por método:\n", ttl_means)
print("\n2. Resumen de uso de protocolos:")
print(df['Protocols'].value_counts())
