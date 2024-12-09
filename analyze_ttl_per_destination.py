# analyze_ttl_per_destination.py
import pandas as pd
import matplotlib.pyplot as plt

# Cargar el archivo CSV ordenado
df = pd.read_csv("resultados/summary_analysis_sorted.csv")

# Agrupar por IP y Método para analizar el TTL medio
ttl_per_ip_method = df.groupby(["IP", "Method"])["TTL Mean"].mean().unstack()

# Gráfico: TTL medio por IP y método
for ip in ttl_per_ip_method.index:
    ttl_per_ip_method.loc[ip].plot(kind="bar", figsize=(10, 6))
    plt.title(f"TTL medio por método para IP {ip}")
    plt.ylabel("TTL Medio")
    plt.xlabel("Método")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"ttl_medio_por_metodo_{ip.replace('.', '_')}.png")
    plt.close()
    print(f"Gráfico guardado para IP {ip} como ttl_medio_por_metodo_{ip.replace('.', '_')}.png")
