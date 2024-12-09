import pandas as pd
import requests
import re
import os
from ipwhois import IPWhois
from ipwhois.exceptions import IPDefinedError
import requests



def es_ip_privada(ip):
    """
    Verifica si una dirección IP es privada.

    Args:
        ip (str): Dirección IP.

    Returns:
        bool: True si es una IP privada, False de lo contrario.
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

def obtener_asn_y_organizacion(ip):
    """
    Obtiene el ASN y la organización para una dirección IP usando ipwhois.
    """
    if es_ip_privada(ip):
        return 'IP Privada', 'IP Privada'
    try:
        obj = IPWhois(ip)
        results = obj.lookup_rdap()
        asn = results.get('asn', 'Desconocido')
        org = results.get('asn_description', 'Desconocido')
        return asn, org
    except IPDefinedError:
        return 'Reservado/Bogon', 'Reservado/Bogon'
    except Exception as e:
        print(f"Error al obtener ASN para {ip}: {e}")
        return 'Desconocido', 'Desconocido'

def obtener_geoip(ip):
    """
    Obtiene información geográfica detallada de una dirección IP utilizando la API de ip-api.com.
    """
    if es_ip_privada(ip):
        return 'IP Privada'
    try:
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data['status'] == 'success':
            ciudad = data.get('city', 'Desconocido')
            region = data.get('regionName', 'Desconocido')
            pais = data.get('country', 'Desconocido')
            lat = data.get('lat', 'Desconocido')
            lon = data.get('lon', 'Desconocido')
            isp = data.get('isp', 'Desconocido')
            return f"{ciudad}, {region}, {pais} - ({lat}, {lon}) - {isp}"
        else:
            return 'Desconocido'
    except Exception as e:
        print(f"Error al obtener GeoIP para {ip}: {e}")
        return 'Desconocido'

def main():
    # Ruta al archivo CSV consolidado
    combined_csv = "resultados/analisis/analisis_combinado.csv"
    
    if not os.path.exists(combined_csv):
        print(f"Error: El archivo {combined_csv} no existe. Asegúrate de haber ejecutado los scripts anteriores correctamente.")
        return
    
    # Leer el archivo CSV
    df = pd.read_csv(combined_csv)
    
    # Leer la información de la ruta principal
    ruta_info_path = "ruta_principal_info.txt"
    if not os.path.exists(ruta_info_path):
        print(f"Error: El archivo {ruta_info_path} no existe. Asegúrate de haber ejecutado 'encontrar_ruta_principal.py' correctamente.")
        return
    
    with open(ruta_info_path, "r") as f:
        lines = f.readlines()
        if len(lines) < 2:
            print("Error: El archivo 'ruta_principal_info.txt' no contiene la información necesaria.")
            return
        metodo = lines[0].strip().split(": ")[1]
        ip_destino = lines[1].strip().split(": ")[1]
    
    print(f"Ruta Principal Identificada:\nMétodo: {metodo}\nIP Destino: {ip_destino}\n")
    
    # Filtrar los datos para la ruta principal
    df_principal = df[(df['Método'] == metodo) & (df['IP_Destino'] == ip_destino)]
    
    # Eliminar duplicados si hay múltiples entradas para el mismo IP en diferentes hops
    df_principal = df_principal.drop_duplicates(subset=['IP'])
    
    # Eliminar filas donde 'IP' es NaN
    df_principal = df_principal.dropna(subset=['IP'])
    
    # Seleccionar solo las columnas necesarias
    df_principal = df_principal[['Hop', 'IP', 'AS']]
    
    # Añadir columnas vacías para los metadatos
    df_principal['Metadata1'] = ''
    df_principal['Metadata2'] = ''
    df_principal['Metadata3'] = ''
    df_principal['Metadata4'] = ''  # Nueva columna para Hurricane Electric

    
    # Iterar sobre las filas para obtener los metadatos
        # Iterar sobre las filas para obtener los metadatos
    for index, row in df_principal.iterrows():
        ip = row['IP']
        print(f"Obteniendo metadata para IP: {ip}")
        if es_ip_privada(ip):
            asn = 'IP Privada'
            org = 'IP Privada'
            geoip = 'IP Privada'
        else:
            asn, org = obtener_asn_y_organizacion(ip)
            geoip = obtener_geoip(ip)
        
        # Asignar los resultados a las columnas correspondientes
        df_principal.at[index, 'Metadata1'] = asn
        df_principal.at[index, 'Metadata2'] = org
        df_principal.at[index, 'Metadata3'] = geoip

    
    # Reordenar las columnas para incluir Hurricane
    df_principal = df_principal[['Hop', 'IP', 'AS', 'Metadata1', 'Metadata2', 'Metadata3', 'Metadata4']]
    
    # Guardar el resultado en un nuevo archivo CSV
    output_csv = "resultados/analisis/metadata_ruta_principal_con_hurricane.csv"
    df_principal.to_csv(output_csv, index=False)
    print(f"\nInformación complementada guardada en {output_csv}")

    
    # Opcional: Mostrar una vista previa del DataFrame
    print("\n=== Vista Previa de la Metadata Complementada ===")
    print(df_principal.head())

if __name__ == "__main__":
    main()
