import os
import pandas as pd
import re

def identificar_nodos_bloqueantes(df, output_csv=None):
    """
    Analiza un DataFrame para identificar nodos que bloquean ciertas solicitudes.
    
    Args:
        df (pd.DataFrame): DataFrame consolidado con los datos de hops.
        output_csv (str): Ruta donde se guardará el análisis de nodos bloqueantes.
    
    Returns:
        pd.DataFrame: DataFrame con el análisis de nodos bloqueantes.
    """
    # Agrupar por IP de salto y protocolo, contando los intentos exitosos
    nodo_respuestas = (
        df.groupby(['IP', 'Protocol'])
        .agg(
            Total_Intentos=('Attempt', 'count'),
            Respuestas=('RTT', lambda x: x.notnull().sum())
        )
        .reset_index()
    )
    
    # Calcular porcentaje de respuestas exitosas
    nodo_respuestas['Porcentaje_Respuestas'] = (
        nodo_respuestas['Respuestas'] / nodo_respuestas['Total_Intentos'] * 100
    )
    
    # Identificar nodos bloqueantes
    nodo_respuestas['Es_Bloqueante'] = nodo_respuestas['Porcentaje_Respuestas'] < 50

    
    # Guardar el análisis en un archivo CSV si se proporciona una ruta
    if output_csv:
        nodo_respuestas.to_csv(output_csv, index=False)
        print(f"\nAnálisis de nodos bloqueantes guardado en {output_csv}")
    
    return nodo_respuestas

def analizar_nodos_por_metodo(combined_csv, output_dir):
    """
    Realiza un análisis detallado de los nodos bloqueantes por método y protocolo.
    
    Args:
        combined_csv (str): Ruta al archivo CSV consolidado.
        output_dir (str): Directorio donde se guardarán los resultados.
    """
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Leer el archivo consolidado
    if not os.path.exists(combined_csv):
        raise FileNotFoundError(f"El archivo {combined_csv} no existe.")
    
    df = pd.read_csv(combined_csv)
    
    # Guardar análisis global de nodos bloqueantes
    bloqueantes_csv = os.path.join(output_dir, "nodos_bloqueantes.csv")
    nodos_bloqueantes = identificar_nodos_bloqueantes(df, bloqueantes_csv)
    
    # Analizar nodos bloqueantes por método
    for metodo in df['Método'].unique():
        metodo_df = df[df['Método'] == metodo]
        metodo_csv = os.path.join(output_dir, f"nodos_bloqueantes_{metodo}.csv")
        
        # Analizar nodos bloqueantes para este método
        nodos_bloqueantes_metodo = identificar_nodos_bloqueantes(metodo_df, metodo_csv)
        print(f"Guardado análisis de nodos bloqueantes para el método {metodo} en {metodo_csv}")

def main():
    # Archivo CSV consolidado de las mediciones
    combined_csv = "resultados/analisis/analisis_combinado.csv"
    
    # Directorio para guardar los resultados
    output_dir = "resultados/analisis/nodos_bloqueantes"
    
    if not os.path.exists(combined_csv):
        print(f"Error: El archivo {combined_csv} no existe. Asegúrate de haber ejecutado el script 'analizar_warts_txt_consolidado.py' correctamente.")
        return
    
    # Ejecutar el análisis de nodos bloqueantes
    analizar_nodos_por_metodo(combined_csv, output_dir)

if __name__ == "__main__":
    main()
