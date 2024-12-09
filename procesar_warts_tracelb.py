import os
import json
import csv

JSON_DIR = "resultados/json"
CONSOLIDATED_CSV = "resultados/consolidado_completo.csv"

def procesar_json_a_csv():
    """
    Procesa todos los archivos JSON en JSON_DIR y genera un archivo CSV consolidado con todos los campos.
    """
    consolidated_rows = []
    all_fields = set()

    # Procesar cada archivo JSON
    for filename in os.listdir(JSON_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(JSON_DIR, filename)
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if obj.get("type") == "tracelb":
                            rows, fields = procesar_tracelb(obj)
                            consolidated_rows.extend(rows)
                            all_fields.update(fields)
                    except json.JSONDecodeError as e:
                        print(f"Error al decodificar JSON en {filename}: {e}")
    
    # Crear el archivo CSV consolidado
    all_fields = list(all_fields)  # Convertir a lista para orden reproducible
    with open(CONSOLIDATED_CSV, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.DictWriter(cf, fieldnames=all_fields)
        writer.writeheader()
        for row in consolidated_rows:
            writer.writerow(row)

    print(f"Consolidación completada: {CONSOLIDATED_CSV}")

def procesar_tracelb(obj):
    """
    Procesa un objeto JSON de tipo 'tracelb' y devuelve las filas correspondientes para el CSV.
    """
    rows = []
    fields = set()

    # Datos generales de la traza
    trace_data = {
        "src": obj.get("src", "N/A"),
        "dst": obj.get("dst", "N/A"),
        "method": obj.get("method", "N/A"),
        "proto": obj.get("proto", "N/A"),
        "sport": obj.get("sport", "N/A"),
        "dport": obj.get("dport", "N/A"),
        "stime": obj.get("start", {}).get("ftime", "N/A"),
        "probe_size": obj.get("probe_size", "N/A"),
        "attempts": obj.get("attempts", "N/A"),
        "confidence": obj.get("confidence", "N/A"),
        "tos": obj.get("tos", "N/A"),
        "gaplimit": obj.get("gaplimit", "N/A"),
        "wait_timeout": obj.get("wait_timeout", "N/A"),
        "node_count": obj.get("nodec", "N/A"),
        "link_count": obj.get("linkc", "N/A"),
    }

    # Iterar sobre nodos
    for node in obj.get("nodes", []):
        node_data = {
            "node_addr": node.get("addr", "N/A"),
            "node_ttl": node.get("q_ttl", "N/A"),
            "node_link_count": node.get("linkc", "N/A"),
        }

        # Iterar sobre enlaces dentro de un nodo
        for link in node.get("links", []):
            for hop in link:
                hop_data = {
                    "hop_addr": hop.get("addr", "N/A"),
                }

                # Iterar sobre probes dentro del hop
                for probe in hop.get("probes", []):
                    probe_data = {
                        "probe_ttl": probe.get("ttl", "N/A"),
                        "probe_attempt": probe.get("attempt", "N/A"),
                        "probe_flowid": probe.get("flowid", "N/A"),
                        "probe_sent_sec": probe.get("tx", {}).get("sec", "N/A"),
                        "probe_sent_usec": probe.get("tx", {}).get("usec", "N/A"),
                    }

                    # Iterar sobre respuestas dentro del probe
                    if "replies" in probe:
                        for reply in probe["replies"]:
                            reply_data = {
                                "reply_rtt": reply.get("rtt", "N/A"),
                                "reply_ttl": reply.get("ttl", "N/A"),
                                "reply_ipid": reply.get("ipid", "N/A"),
                                "reply_icmp_type": reply.get("icmp_type", "N/A"),
                                "reply_icmp_code": reply.get("icmp_code", "N/A"),
                            }
                            # Consolidar todos los datos en una fila
                            full_row = {**trace_data, **node_data, **hop_data, **probe_data, **reply_data}
                            rows.append(full_row)
                            fields.update(full_row.keys())
                    else:
                        # Si no hay respuestas, agregar la fila con datos vacíos para reply
                        reply_data = {
                            "reply_rtt": "N/A",
                            "reply_ttl": "N/A",
                            "reply_ipid": "N/A",
                            "reply_icmp_type": "N/A",
                            "reply_icmp_code": "N/A",
                        }
                        full_row = {**trace_data, **node_data, **hop_data, **probe_data, **reply_data}
                        rows.append(full_row)
                        fields.update(full_row.keys())

    return rows, fields
import pandas as pd

# Ruta al archivo consolidado
CSV_FILE = "resultados/consolidado_completo.csv"

def contar_ips_por_metodo():
    # Leer el archivo CSV consolidado
    df = pd.read_csv(CSV_FILE)

    # Asegurarnos de trabajar con columnas relevantes: node_addr y hop_addr
    df = df[['dst', 'method', 'node_addr', 'hop_addr']].fillna('N/A')

    # Consolidar las IPs únicas detectadas (node_addr y hop_addr)
    df['detected_ip'] = df['node_addr']
    df.loc[df['node_addr'] == 'N/A', 'detected_ip'] = df['hop_addr']

    # Filtrar solo IPs válidas
    df = df[df['detected_ip'] != 'N/A']

    # Agrupar por destino y método
    resultados = df.groupby(['dst', 'method'])['detected_ip'].nunique().reset_index()

    # Renombrar la columna de conteo
    resultados.rename(columns={'detected_ip': 'unique_ips_count'}, inplace=True)

    # Ordenar resultados por cantidad de IPs únicas (descendente) y destino
    resultados.sort_values(by=['unique_ips_count', 'dst'], ascending=[False, True], inplace=True)

    # Guardar resultados en un archivo para análisis adicional
    resultados.to_csv("resultados/ips_por_metodo.csv", index=False)

    print("Resultados guardados en 'resultados/ips_por_metodo.csv'")
    return resultados


if __name__ == "__main__":
    #procesar_json_a_csv()
    contar_ips_por_metodo()
