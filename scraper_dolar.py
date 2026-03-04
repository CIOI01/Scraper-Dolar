#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, send_from_directory
import requests 
from datetime import datetime 
import csv 
import pandas as pd 
import matplotlib
matplotlib.use('Agg')  # Configuramos Matplotlib para que funcione sin necesidad de una interfaz gráfica
import matplotlib.pyplot as plt 
import logging 
import os 
from dotenv import load_dotenv 

# Configuramos la aplicación Flask (Nuestro servidor)
app = Flask(__name__)
# Cargamos las variables de entorno desde el archivo .env
ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_env = os.path.join(ruta_actual, '.env')
load_dotenv(ruta_env)  
# Configuramos el logging para registrar errores y eventos importantes
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='scraper.log')
# Definimos la clase ScraperDolar que se encargará de obtener los datos del dólar, calcular variaciones y guardar la información
class ScraperDolar: 
    BASE_URL = "https://mindicador.cl/api/dolar" 
    CSV_HEADERS = ["Fecha", "Valor del Dólar (CLP)", "Hora", "Variación Diaria"] 
    HISTORIC_CSV = "dolar_historico.csv"
     
    # Inicializamos la sesión de requests para reutilizar conexiones y mejorar el rendimiento
    def __init__(self): 
        self.session = requests.Session() 
        self.session.headers.update({"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        
    # Método para obtener los datos del dólar desde la API
    def obtener_datos_dolar(self): 
        try:
            response = self.session.get(self.BASE_URL, timeout=10) 
            response.raise_for_status()  
            data = response.json() 
            primer_item = data["serie"][0] 
            return primer_item["valor"], datetime.now().strftime("%Y-%m-%d") 
        except Exception as e: 
            logging.error(f"Error: {str(e)}") 
            return None, None 
        
    # Método para calcular la variación porcentual del dólar con respecto al último valor registrado
    def calcular_variacion(self, valor_actual): 
        try:
            df = pd.read_csv(self.HISTORIC_CSV, sep=";") 
            ultimo_valor_str = df.iloc[-1]["Valor del Dólar (CLP)"] 
            ultimo_valor = float(ultimo_valor_str.replace("$", "").replace(".", "").replace(",", "."))
            return round(((valor_actual - ultimo_valor) / ultimo_valor) * 100, 2) 
        except Exception: 
            return None 
        
    # Método para guardar los datos obtenidos en un archivo CSV, incluyendo la fecha, valor, hora y variación
    def guardar_datos(self, valor, fecha, variacion): 
        try:
            hora = datetime.now().strftime("%H:%M:%S") 
            valor_form = f"${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 
            with open(self.HISTORIC_CSV, "a", newline="", encoding="utf-8") as file: 
                writer = csv.writer(file, delimiter=";") 
                if file.tell() == 0: writer.writerow(self.CSV_HEADERS) 
                writer.writerow([fecha, valor_form, hora, f"{variacion}%" if variacion is not None else "N/A"])
        except Exception as e: 
            logging.error(f"Error guardar: {e}") 
            
    # Método para generar un gráfico de la evolución del valor del dólar a lo largo del tiempo utilizando Matplotlib
    def generar_grafico(self): 
        try:
            print("Generando gráfico actualizado...")
            df = pd.read_csv(self.HISTORIC_CSV, sep=";") 
            df["Valor Numérico"] = df["Valor del Dólar (CLP)"].str.replace("$", "").str.replace(".", "").str.replace(",", ".", regex=False).astype(float) 
            df["Fecha"] = pd.to_datetime(df["Fecha"]) 
            plt.figure(figsize=(12, 6)) 
            plt.plot(df["Fecha"], df["Valor Numérico"], marker="o", linestyle="-", color="blue") 
            plt.title("Evolución del Valor del Dólar en Chile", pad=20) 
            plt.xlabel("Fecha", labelpad=10) 
            plt.ylabel("Pesos Chilenos (CLP)", labelpad=10) 
            plt.grid(True, linestyle="--", alpha=0.7) 
            plt.xticks(rotation=45) 
            plt.tight_layout() 
            plt.savefig("evolucion_dolar.png", dpi=300) 
        except Exception as e: 
            logging.error(f"Error grafico: {e}")        

# Endpoint raíz para verificar que el servidor está funcionando correctamente
@app.route('/', methods=['GET', 'HEAD'])
def inicio():
    return "🤖 Bot Financiero en línea y escuchando puerto 10000...", 200

# Definimos el endpoint de la API que n8n llamará para obtener los datos del dólar
@app.route('/api/consultar-dolar', methods=['GET'])
def endpoint_dolar():
    print("Recibiendo llamada desde n8n...")
    scraper = ScraperDolar()
    valor, fecha = scraper.obtener_datos_dolar()
    
    # Si se obtuvo un valor válido, calculamos la variación (si es posible) y guardamos los datos, luego respondemos a n8n con un JSON que incluye el valor del dólar, la variación y la hora actual
    if valor is not None:
        variacion = scraper.calcular_variacion(valor) if os.path.exists(scraper.HISTORIC_CSV) else None
        scraper.guardar_datos(valor, fecha, variacion)
        
        # Creacion de Grafico de Evolución del Dólar
        scraper.generar_grafico() 
        
        # Deteccion de la URL base del servidor para construir las URLs de los archivos
        url_base = request.host_url.rstrip('/')
        
        # retorno a N8N con la información del dólar, variación, hora actual y URLs para el gráfico y el CSV histórico
        return jsonify({
            "status": "success",
            "valor_dolar": valor,
            "variacion": variacion if variacion is not None else 0,
            "hora_actual": datetime.now().strftime("%H:%M:%S"),
            "url_grafico": f"{url_base}/archivos/evolucion_dolar.png",
            "url_csv": f"{url_base}/archivos/dolar_historico.csv"
        }), 200
    else:
        return jsonify({"status": "error", "message": "Fallo al consultar la API"}), 500
    
    
@app.route('/archivos/<nombre_archivo>', methods=['GET'])
def obtener_archivo(nombre_archivo):
    # Seleccion precisa de archivos permitidos para descargar, evitando cualquier intento de acceso a archivos no autorizados
    if nombre_archivo in ["evolucion_dolar.png", "dolar_historico.csv"]:
        return send_from_directory(ruta_actual, nombre_archivo)
    
    # Si alguien intenta descargar otro archivo, le damos error
    return jsonify({"error": "Archivo no permitido o inexistente"}), 403

# Encendemos el servidor en el puerto 5000
if __name__ == "__main__":
    print("🚀 Servidor Flask iniciado. Esperando llamadas...")
    # host='0.0.0.0' es vital para que la nube permita conexiones externas
    app.run(host="0.0.0.0", port=5000)