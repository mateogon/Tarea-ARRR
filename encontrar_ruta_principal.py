# encontrar_ruta_principal.py
import pandas as pd
import os

def encontrar_ruta_mas_ips(csv_path):
    """
    Encuentra la ruta (Método + IP_Destino) con la mayor cantidad de IPs detectadas.
    
    Args:
        csv_path (str): Ruta al archivo CSV consolidado.
    
    Returns:
        pd.Series: Serie con información de la ruta principal.
    """
    df = pd.read_csv(csv_path)
    
    # Agrupar por Método y IP_Destino, contar IPs únicas
    conteo = df.groupby(['Método', 'IP_Destino'])['IP'].nunique().reset_index(name='Total_IPs_Detectadas')
    
    # Ordenar de mayor a menor y seleccionar la primera fila
    ruta_principal = conteo.sort_values(by='Total_IPs_Detectadas', ascending=False).iloc[0]
    
    print("=== Ruta con Mayor Cantidad de IPs Detectadas ===")
    print(f"Método: {ruta_principal['Método']}")
    print(f"IP Destino: {ruta_principal['IP_Destino']}")
    print(f"Total de IPs Detectadas: {ruta_principal['Total_IPs_Detectadas']}")
    
    # Guardar el resultado en un archivo CSV (opcional)
    output_csv = os.path.join(os.path.dirname(csv_path), "ruta_principal.csv")
    ruta_principal.to_frame().T.to_csv(output_csv, index=False)
    print(f"\nInformación de la ruta principal guardada en {output_csv}")
    print(conteo)
    return ruta_principal

def main():
    # Ruta al archivo CSV consolidado
    combined_csv = "resultados/analisis/analisis_combinado.csv"
    
    if not os.path.exists(combined_csv):
        print(f"Error: El archivo {combined_csv} no existe. Asegúrate de haber ejecutado el script 'analizar_warts_txt_consolidado.py' correctamente.")
        return
    
    # Encontrar la ruta con mayor cantidad de IPs
    ruta_principal = encontrar_ruta_mas_ips(combined_csv)
    
    # Guardar la información para uso posterior
    with open("ruta_principal_info.txt", "w") as f:
        f.write(f"Método: {ruta_principal['Método']}\n")
        f.write(f"IP Destino: {ruta_principal['IP_Destino']}\n")
        f.write(f"Total de IPs Detectadas: {ruta_principal['Total_IPs_Detectadas']}\n")
    
    print("\nInformación de la ruta principal guardada en 'ruta_principal_info.txt'.")

if __name__ == "__main__":
    main()
