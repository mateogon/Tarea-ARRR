import time
import os
import subprocess
from ripe.atlas.cousteau import (
    AtlasCreateRequest,
    Traceroute,
    AtlasSource
)

# Configuración
RIPE_ATLAS_API_KEY = '0c49dc2f-35a2-46f7-a911-a5dad9d3796a'
TARGETS = [
    '185.131.204.20',
    '5.161.76.19',
    '80.77.4.60',
    '130.104.228.159'
]
PROTOCOLS = ['ICMP', 'UDP', 'TCP']
DELAY_BETWEEN_IPS = 600  # 10 minutos entre cada IP (en segundos)
PROBE_ID = 1009650  # Cambiar al ID de la sonda configurada
OUTPUT_DIR = "./captures"

# Asegurarse de que el directorio de capturas exista
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_all_traceroute_measurements(target):
    """
    Crear mediciones de traceroute para todos los protocolos en RIPE Atlas.
    """
    measurements = []
    for protocol in PROTOCOLS:
        description = f'Traceroute a {target} usando {protocol}'
        af = 4  # IPv4
        packets = 3
        first_hop = 1
        max_hops = 32
        resolve_on_probe = True

        # Configuración del protocolo
        if protocol == 'ICMP':
            protocol_param = 'ICMP'
            port = None
        elif protocol == 'UDP':
            protocol_param = 'UDP'
            port = 33434
        elif protocol == 'TCP':
            protocol_param = 'TCP'
            port = 80
        else:
            raise ValueError(f'Protocolo no soportado: {protocol}')

        traceroute = Traceroute(
            af=af,
            target=target,
            description=description,
            protocol=protocol_param,
            packets=packets,
            first_hop=first_hop,
            max_hops=max_hops,
            resolve_on_probe=resolve_on_probe,
            port=port
        )

        source = AtlasSource(
            type='probes',
            value=str(PROBE_ID),
            requested=1
        )

        atlas_request = AtlasCreateRequest(
            start_time=None,
            key=RIPE_ATLAS_API_KEY,
            measurements=[traceroute],
            sources=[source],
            is_oneoff=True
        )

        is_success, response = atlas_request.create()
        if is_success:
            print(f"Medición creada con éxito para {target} usando {protocol}: {response}")
            measurements.append(response)
        else:
            print(f"Error al crear la medición: {response}")

    return measurements


def capture_traffic(ip, duration, output_file):
    """
    Captura tráfico de red filtrando por la IP de destino.
    """
    print(f"Iniciando captura de tráfico para {ip} durante {duration // 60} minutos...")
    try:
        command = [
            "tshark",
            "-i", "docker0",  # Cambia por la interfaz adecuada para tu configuración
            "-a", f"duration:{duration}",
            "-w", output_file,
            "host", ip
        ]
        subprocess.run(command, check=True)
        print(f"Captura guardada en {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error al capturar tráfico: {e}")


def perform_measurements():
    """
    Realiza las mediciones de traceroute para cada IP y captura tráfico.
    """
    for target in TARGETS:
        print(f"\n### Iniciando mediciones para {target} ###")
        capture_file = os.path.join(OUTPUT_DIR, f"{target.replace('.', '_')}.pcap")

        # Crear mediciones para todos los protocolos
        print(f"Creando mediciones para {target}...")
        create_all_traceroute_measurements(target)

        # Capturar tráfico durante 10 minutos
        capture_duration = DELAY_BETWEEN_IPS  # 10 minutos
        capture_traffic(target, capture_duration, capture_file)

        print(f"Captura y mediciones completadas para {target}. Esperando antes de la siguiente IP...")
        time.sleep(10)  # Breve pausa entre IPs


if __name__ == "__main__":
    perform_measurements()
