# analizar_warts_txt_consolidado.py
import os
import re
import pandas as pd
import requests
import time
from ipwhois import IPWhois
from ipwhois.exceptions import IPDefinedError

def es_ip_privada(ip):
    """
    Verifica si una dirección IP es privada.
    """
    private_ip_patterns = [
        r'^10\.',
        r'^172\.(1[6-9]|2[0-9]|3[01])\.',
        r'^192\.168\.',
        r'^169\.254\.',
        r'^127\.0\.0\.',
    ]
    for pattern in private_ip_patterns:
        if re.match(pattern, ip):
            return True
    return False

def obtener_as(ip):
    """
    Obtiene el Sistema Autónomo (AS) para una dirección IP utilizando ipwhois.
    """
    if es_ip_privada(ip):
        return 'IP Privada'
    try:
        obj = IPWhois(ip)
        results = obj.lookup_rdap(depth=1)
        asn = results.get('asn', 'Desconocido')
        asn_description = results.get('asn_description', 'Desconocido')
        if asn != 'NA':
            return f"AS{asn} - {asn_description}"
        else:
            return 'Desconocido'
    except IPDefinedError:
        return 'Reservado/Bogon'
    except Exception as e:
        print(f"Error al obtener AS para {ip}: {e}")
        return 'Desconocido'

def determinar_protocolo(metodo):
    """
    Determina el protocolo basado en el método utilizado por Scamper.
    """
    if 'icmp' in metodo.lower():
        return 'ICMP'
    elif 'udp' in metodo.lower():
        return 'UDP'
    elif 'tcp' in metodo.lower():
        return 'TCP'
    else:
        return 'Desconocido'

def parse_warts_txt(file_path):
    """
    Parsea un archivo .txt generado por sc_wartsdump y extrae información de cada hop.
    """
    hops = []
    current_hop = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Detectar inicio de traceroute
            if line.startswith('traceroute from'):
                traceroute_info = line
                continue
            # Detectar cada salto
            hop_match = re.match(r'^hop\s+(\d+)\s+([\d\.]+)', line, re.IGNORECASE)
            if hop_match:
                if current_hop:
                    # Añadir el hop anterior a la lista
                    hops.append(current_hop)
                    current_hop = {}
                current_hop['Hop'] = int(hop_match.group(1))
                current_hop['IP'] = hop_match.group(2)
                # Obtener AS para la IP
                current_hop['AS'] = obtener_as(current_hop['IP'])
                time.sleep(0.1)  # Pequeña pausa para evitar sobrecargar el servicio
                continue
            # Detectar cada salto
            hop_match = re.match(r'^hop\s+(\d+)\s+([\d\.]+)', line, re.IGNORECASE)
            if hop_match:
                if current_hop:
                    # Obtener AS para la IP
                    if 'IP' in current_hop:
                        current_hop['AS'] = obtener_as(current_hop['IP'])
                        time.sleep(0.5)  # Pausa para evitar sobrecargar la API
                    hops.append(current_hop)
                    current_hop = {}
                current_hop['Hop'] = int(hop_match.group(1))
                current_hop['IP'] = hop_match.group(2)
                continue
            # Extraer detalles del salto
            if line.startswith('attempt:'):
                # Ejemplo: attempt: 1, tx: 0.000005s, rtt: 0.000420s, probe-size: 44
                attempt_match = re.search(r'attempt:\s*(\d+),\s*tx:\s*([\d\.]+)s,\s*rtt:\s*([\d\.]+)s,\s*probe-size:\s*(\d+)', line)
                if attempt_match:
                    current_hop['Attempt'] = int(attempt_match.group(1))
                    current_hop['TX_Time'] = float(attempt_match.group(2))
                    current_hop['RTT'] = float(attempt_match.group(3))
                    current_hop['Probe_Size'] = int(attempt_match.group(4))
                continue
            if line.startswith('reply-ttl:'):
                # Ejemplo: reply-ttl: 64, reply-size: 72, reply-ipid: 0x7ad1, reply-tos: 0xc0
                reply_match = re.search(r'reply-ttl:\s*(\d+),\s*reply-size:\s*(\d+),\s*reply-ipid:\s*(0x[0-9a-fA-F]+),\s*reply-tos:\s*(0x[0-9a-fA-F]+)', line)
                if reply_match:
                    current_hop['Reply_TTL'] = int(reply_match.group(1))
                    current_hop['Reply_Size'] = int(reply_match.group(2))
                    current_hop['Reply_IPID'] = reply_match.group(3)
                    current_hop['Reply_TOS'] = reply_match.group(4)
                continue
            if line.startswith('icmp-type:'):
                # Ejemplo: icmp-type: 11, icmp-code: 0, q-ttl: 1, q-len: 44, q-tos 0
                icmp_match = re.search(r'icmp-type:\s*(\d+),\s*icmp-code:\s*(\d+),\s*q-ttl:\s*(\d+),\s*q-len:\s*(\d+),\s*q-tos\s*(\d+)', line)
                if icmp_match:
                    current_hop['ICMP_Type'] = int(icmp_match.group(1))
                    current_hop['ICMP_Code'] = int(icmp_match.group(2))
                    current_hop['Query_TTL'] = int(icmp_match.group(3))
                    current_hop['Query_Len'] = int(icmp_match.group(4))
                    current_hop['Query_TOS'] = int(icmp_match.group(5))
                continue
            if line.startswith('flags:'):
                # Ejemplo: flags: 0x11 ( sockrxts replyttl )
                flags_match = re.search(r'flags:\s*(0x[0-9a-fA-F]+)\s*\((.*?)\)', line)
                if flags_match:
                    current_hop['Flags'] = flags_match.group(1)
                    current_hop['Flags_Description'] = flags_match.group(2)
                # Verificar si hay extensiones MPLS
                mpls_match = re.search(r'mpls ext ttl:\s*(\d+),\s*s:\s*(\d+),\s*exp:\s*(\d+),\s*label:\s*(\d+)', line)
                if mpls_match:
                    current_hop['MPLS_Ext_TTL'] = int(mpls_match.group(1))
                    current_hop['MPLS_S'] = int(mpls_match.group(2))
                    current_hop['MPLS_EXP'] = int(mpls_match.group(3))
                    current_hop['MPLS_Label'] = int(mpls_match.group(4))
                continue
    # Añadir el último hop
    if current_hop:
            hops.append(current_hop)
    return hops
def main():
    # Directorio que contiene los archivos .txt
    TXT_DIR = "resultados/txt"
    OUTPUT_DIR = "resultados/analisis"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Lista para almacenar todos los registros
    all_hops = []
    
    # Recorrer todos los archivos .txt en el directorio
    for filename in os.listdir(TXT_DIR):
        if filename.endswith(".txt"):
            file_path = os.path.join(TXT_DIR, filename)
            print(f"Analizando archivo: {filename}")
            hops = parse_warts_txt(file_path)
            # Añadir columnas adicionales basadas en el nombre del archivo
            # Asumiendo el formato: metodo_IP.txt
            base_name = os.path.splitext(filename)[0]
            partes = base_name.split('_')
            metodo = partes[0]
            ip = '.'.join(partes[1:])
            protocol = determinar_protocolo(metodo)
            for hop in hops:
                hop['Método'] = metodo
                hop['IP_Destino'] = ip
                hop['Protocol'] = protocol
            all_hops.extend(hops)
    
    # Crear un DataFrame consolidado
    if all_hops:
        combined_df = pd.DataFrame(all_hops)
        # Reordenar columnas para mayor claridad
        columnas = [
            'Método', 'Protocol', 'IP_Destino', 'Hop', 'IP', 'AS', 'Attempt',
            'TX_Time', 'RTT', 'Probe_Size', 'Reply_TTL', 'Reply_Size',
            'Reply_IPID', 'Reply_TOS', 'ICMP_Type', 'ICMP_Code',
            'Query_TTL', 'Query_Len', 'Query_TOS', 'Flags', 'Flags_Description',
            'MPLS_Ext_TTL', 'MPLS_S', 'MPLS_EXP', 'MPLS_Label'
        ]
        # Filtrar solo las columnas existentes en el DataFrame
        columnas_presentes = [col for col in columnas if col in combined_df.columns]
        combined_df = combined_df[columnas_presentes]
        # Guardar el DataFrame consolidado en un único CSV
        combined_csv = os.path.join(OUTPUT_DIR, "analisis_combinado.csv")
        combined_df.to_csv(combined_csv, index=False)
        print(f"\nAnálisis consolidado guardado en {combined_csv}")
    else:
        print("No se encontraron archivos .txt para analizar.")

if __name__ == "__main__":
    main()