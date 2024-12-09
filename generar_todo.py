# analizar_summary_analysis_consola.py
import pandas as pd

def cargar_datos(ruta_csv):
    try:
        df = pd.read_csv(ruta_csv)
        print(f"Datos cargados exitosamente desde {ruta_csv}\n")
        return df
    except FileNotFoundError:
        print(f"Error: El archivo {ruta_csv} no se encontró.")
        exit(1)
    except Exception as e:
        print(f"Error al cargar el archivo CSV: {e}")
        exit(1)

def total_paquetes_por_archivo(df):
    print("=== Total de Paquetes por Archivo ===")
    total_paquetes = df[['File', 'Total Packets']].copy()
    total_paquetes = total_paquetes.sort_values(by='Total Packets', ascending=False)
    print(total_paquetes.to_string(index=False))
    print("Referencia de imagen: total_paquetes_por_archivo.png\n")

def ttl_promedio_por_metodo(df):
    print("=== TTL Promedio por Método ===")
    ttl_means = df.groupby('Method')['TTL Mean'].mean().reset_index()
    print(ttl_means.to_string(index=False))
    print("Referencia de imagen: ttl_promedio_por_metodo.png\n")
    return ttl_means

def resumen_uso_protocolos(df):
    print("=== Resumen de Uso de Protocolos ===")
    # Asumiendo que la columna 'Protocols' tiene un formato tipo "{1: 100, 6: 50, 17: 30}"
    protocol_counts = df['Protocols'].dropna().apply(lambda x: pd.Series(eval(x)))
    protocol_summary = protocol_counts.sum().sort_values(ascending=False).rename_axis('Protocolo').reset_index(name='Cantidad')
    # Mapear los números de protocolo a nombres
    protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
    protocol_summary['Protocolo'] = protocol_summary['Protocolo'].map(protocol_map).fillna(protocol_summary['Protocolo'])
    print(protocol_summary.to_string(index=False))
    print("Referencia de imagen: distribucion_de_protocolos.png\n")

def analisis_combinado_por_ip(df):
    print("=== Análisis Combinado: Total de Paquetes y TTL Medio por IP ===")
    summary = df.groupby(["IP", "Method"])[["Total Packets", "TTL Mean"]].mean().reset_index()
    for ip in summary['IP'].unique():
        print(f"--- IP: {ip} ---")
        datos_ip = summary[summary['IP'] == ip][['Method', 'Total Packets', 'TTL Mean']]
        print(datos_ip.to_string(index=False))
        print("Referencia de imagen: analisis_combinado_{ip}.png\n".format(ip=ip.replace('.', '_')))
    print()

def longitud_promedio_paquetes_por_metodo(df):
    print("=== Longitud Promedio de Paquetes por Método ===")
    frame_lengths = df.groupby("Method")[["Frame Length Mean"]].mean().reset_index()
    print(frame_lengths.to_string(index=False))
    print("Referencia de imagen: longitud_promedio_paquetes_por_metodo.png\n")

def comparacion_ttl_paris_vs_estandar(df):
    print("=== Comparación del TTL Medio: Métodos Paris vs. Estándar ===")
    # Extraer el nombre del método de la columna "File"
    df["Method_Name"] = df["File"].str.extract(r"^(\w+)_", expand=False)
    # Añadir una columna "Method Type" para diferenciar Paris vs. Estándar
    df["Method Type"] = df["File"].apply(lambda x: "Paris" if "paris" in x.lower() else "Estándar")
    # Agrupar por tipo de método y método para analizar el TTL medio
    ttl_comparison = df.groupby(["Method Type", "Method_Name"])["TTL Mean"].mean().reset_index()
    # Pivotar para una mejor visualización
    ttl_pivot = ttl_comparison.pivot(index='Method_Name', columns='Method Type', values='TTL Mean').fillna(0)
    print(ttl_pivot.to_string())
    print("Referencia de imagen: ttl_paris_vs_estandar.png\n")

def distribucion_de_protocolos(df):
    print("=== Distribución de Protocolos ===")
    # Asumiendo que la columna 'Protocols' tiene un formato tipo "{1: 100, 6: 50, 17: 30}"
    protocols = df["Protocols"].dropna().apply(lambda x: pd.Series(eval(x)))
    protocol_summary = protocols.sum().sort_values(ascending=False).rename_axis('Protocolo').reset_index(name='Cantidad')
    # Mapear los números de protocolo a nombres
    protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
    protocol_summary['Protocolo'] = protocol_summary['Protocolo'].map(protocol_map).fillna(protocol_summary['Protocolo'])
    print(protocol_summary.to_string(index=False))
    print("Referencia de imagen: distribucion_de_protocolos.png\n")

def total_paquetes_y_ttl_por_destino(df):
    print("=== Total de Paquetes y TTL Promedio por IP de Destino ===")
    summary_per_ip = df.groupby("IP")[["Total Packets", "TTL Mean"]].mean().reset_index()
    print("** Total de Paquetes por IP de Destino **")
    print(summary_per_ip[['IP', 'Total Packets']].to_string(index=False))
    print("Referencia de imagen: total_paquetes_por_destino.png\n")
    print("** TTL Promedio por IP de Destino **")
    print(summary_per_ip[['IP', 'TTL Mean']].to_string(index=False))
    print("Referencia de imagen: ttl_promedio_por_destino.png\n")

def ttl_medio_por_ip_y_metodo(df):
    print("=== TTL Medio por IP y Método ===")
    ttl_per_ip_method = df.groupby(["IP", "Method"])["TTL Mean"].mean().reset_index()
    for ip in ttl_per_ip_method['IP'].unique():
        print(f"--- IP: {ip} ---")
        datos_ip = ttl_per_ip_method[ttl_per_ip_method['IP'] == ip][['Method', 'TTL Mean']]
        print(datos_ip.to_string(index=False))
        print("Referencia de imagen: ttl_medio_por_metodo_{ip}.png\n".format(ip=ip.replace('.', '_')))
    print()

def main():
    ruta_csv = "resultados/summary_analysis_sorted.csv"
    df = cargar_datos(ruta_csv)

    # 1. Total de paquetes por archivo
    total_paquetes_por_archivo(df)

    # 2. TTL promedio por método
    ttl_means = ttl_promedio_por_metodo(df)

    # 3. Resumen de uso de protocolos
    resumen_uso_protocolos(df)

    # 4. Análisis combinado por IP
    analisis_combinado_por_ip(df)

    # 5. Longitud promedio de paquetes por método
    longitud_promedio_paquetes_por_metodo(df)

    # 6. Comparación de TTL entre Paris y Estándar
    comparacion_ttl_paris_vs_estandar(df)

    # 7. Distribución de protocolos
    distribucion_de_protocolos(df)

    # 8. Total de paquetes y TTL promedio por IP de destino
    total_paquetes_y_ttl_por_destino(df)

    # 9. TTL medio por IP y método
    ttl_medio_por_ip_y_metodo(df)

if __name__ == "__main__":
    main()
