#!/bin/bash

# Lista de IPs destino
DESTINOS=("185.131.204.20" "5.161.76.19" "80.77.4.60" "130.104.228.159")

# Metodos de Scamper
METODOS=("icmp" "udp" "tcp" "icmp-paris" "udp-paris" "tcp-ack")

# Carpeta para guardar resultados
OUTPUT_DIR="resultados"
PCAP_DIR="$OUTPUT_DIR/pcap"
WARTS_DIR="$OUTPUT_DIR/warts"
TXT_DIR="$OUTPUT_DIR/txt"
INTERFACE=$1

mkdir -p $PCAP_DIR $WARTS_DIR $TXT_DIR
chmod -R 755 $OUTPUT_DIR

# Iterar sobre cada IP destino
for IP in "${DESTINOS[@]}"; do
  for METODO in "${METODOS[@]}"; do
    echo "Ejecutando Scamper con metodo $METODO hacia $IP..."

    # Nombre de archivo base
    BASE_NAME="${METODO}_${IP//./_}"

    # Iniciar captura de trafico con tshark
    tshark -i "$INTERFACE" -f "host $IP" -w "$PCAP_DIR/${BASE_NAME}.pcap" &
    TSHARK_PID=$!

    # Ejecutar Scamper
    scamper -O warts -o "$WARTS_DIR/${BASE_NAME}.warts" -c "trace -P $METODO" -i "$IP"

    # Detener captura de tshark
    kill $TSHARK_PID

    # Analizar archivo .warts
    sc_wartsdump "$WARTS_DIR/${BASE_NAME}.warts" > "$TXT_DIR/${BASE_NAME}.txt"
  done
done

echo "Automatizacion completada. Resultados guardados en $OUTPUT_DIR."