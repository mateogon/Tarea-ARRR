import time
import os
import subprocess
from ripe.atlas.cousteau import (
    AtlasCreateRequest,
    Traceroute,
    AtlasSource
)

# Configuration
RIPE_ATLAS_API_KEY = '0c49dc2f-35a2-46f7-a911-a5dad9d3796a'
MY_PUBLIC_IP = '191.112.23.7'
PROTOCOLS = ['ICMP', 'UDP', 'TCP']
DELAY_BETWEEN_IPS = 1  # 10 minutes between each IP (in seconds)
OUTPUT_DIR = "./captures"

# Target probe IDs and their corresponding destination IPs
TARGET_PROBES = {
     '185.131.204.20': 7344,
    '5.161.76.19': 1000916,
    '80.77.4.60': 7047,
    '130.104.228.159': 6937
}

# Ensure the capture directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_reverse_traceroute_measurements(target, probe_id):
    """
    Create reverse traceroute measurements from a specific probe near the target to the public IP.
    """
    measurements = []
    for protocol in PROTOCOLS:
        description = f"Reverse traceroute desde {target} hacia {MY_PUBLIC_IP} usando {protocol}"
        af = 4  # IPv4
        packets = 3
        first_hop = 1
        max_hops = 32
        resolve_on_probe = True

        # Configure protocol
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
            target=MY_PUBLIC_IP,
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
            value=str(probe_id),  # Use the provided probe ID
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
            print(f"Medición creada con éxito desde {target}: {response}")
            measurements.append(response)
        else:
            print(f"Error al crear la medición desde {target}: {response}")

    return measurements


def capture_reverse_traffic(ip, duration, output_file):
    """
    Capture traffic from the reverse traceroute measurement for analysis.
    """
    print(f"Iniciando captura de tráfico desde {ip} durante {duration // 60} minutos...")
    try:
        command = [
            "tshark",
            "-i", "docker0",  # Update this if using a different interface
            "-a", f"duration:{duration}",
            "-w", output_file,
            "host", ip
        ]
        subprocess.run(command, check=True)
        print(f"Captura guardada en {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error al capturar tráfico: {e}")


def perform_reverse_measurements():
    """
    Perform reverse measurements for each target IP and capture traffic.
    """
    for target, probe_id in TARGET_PROBES.items():
        print(f"\n### Iniciando mediciones inversas para {target} ###")
        capture_file = os.path.join(OUTPUT_DIR, f"reverse_{target.replace('.', '_')}.pcap")

        # Create reverse measurements
        print(f"Creando mediciones inversas desde {target} hacia {MY_PUBLIC_IP}...")
        create_reverse_traceroute_measurements(target, probe_id)

        # Capture traffic during the reverse measurements
        capture_duration = DELAY_BETWEEN_IPS  # 10 minutes
        capture_reverse_traffic(target, capture_duration, capture_file)

        print(f"Captura y mediciones completadas para {target}. Esperando antes de la siguiente IP...")
        time.sleep(DELAY_BETWEEN_IPS)  # Wait before moving to the next target


if __name__ == "__main__":
    perform_reverse_measurements()
