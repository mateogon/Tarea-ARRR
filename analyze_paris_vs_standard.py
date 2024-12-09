# analyze_paris_vs_standard.py
import pandas as pd
import matplotlib.pyplot as plt

# Cargar el archivo CSV de resumen
df = pd.read_csv("resultados/summary_analysis_sorted.csv")

# Extraer el nombre del método de la columna "File"
df["Method"] = df["File"].str.extract(r"^(\w+)_", expand=False)

# Añadir una columna "Method Type" para diferenciar Paris vs. Standard
df["Method Type"] = df["File"].apply(lambda x: "Paris" if "paris" in x else "Estándar")

# Agrupar por tipo de método y método para analizar el TTL medio
ttl_comparison = df.groupby(["Method Type", "Method"])["TTL Mean"].mean().unstack()

# Graficar el TTL medio para métodos Paris vs. Estándar
ttl_comparison.T.plot(kind="bar", figsize=(10, 6), color=["blue", "orange"])
plt.title("Comparación del TTL medio: Métodos Paris vs. Estándar")
plt.ylabel("TTL Medio")
plt.xlabel("Método")
plt.xticks(rotation=45)
plt.legend(title="Tipo de Método")
plt.tight_layout()
plt.savefig("ttl_paris_vs_estandar.png")
print("Análisis de TTL Paris vs. Estándar guardado como ttl_paris_vs_estandar.png")
