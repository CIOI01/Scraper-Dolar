#!/usr/bin/env python3 (usa Python 3)
# -*- coding: utf-8 -*- (codificación UTF-8 para compatibilidad con caracteres especiales)

"""
Scraper del Dólar Chileno - Proyecto Profesional
Autor: CIOI
GitHub: https://github.com/tuusuario/scraper-dolar-chile
"""

# Importaciones organizadas (estándar, terceros, locales)
import requests # Importa requests para hacer peticiones HTTP
from datetime import datetime # Importa datetime para manejar fechas y horas
import csv # Importa csv para manejar archivos CSV
import pandas as pd # Importa pandas para análisis de datos
import matplotlib.pyplot as plt # Importa matplotlib para generar gráficos
import logging # Importa logging para registrar eventos y errores
from typing import Tuple, Optional # Importa tipos opcionales y tuplas para anotaciones de tipo
import os # Importa os para manejar el sistema de archivos
from dotenv import load_dotenv # Importa dotenv para manejar variables de entorno
import smtplib # Importa smtplib para enviar correos electrónicos
from email.mime.text import MIMEText # Importa MIMEText para crear mensajes de correo electrónico

# Configuración inicial
load_dotenv()  # Carga variables de entorno
logging.basicConfig( # Configura el logging
    level=logging.INFO, # Nivel de logging
    format='%(asctime)s - %(levelname)s - %(message)s', # Formato del mensaje
    filename='scraper.log' # Nombre del archivo de logging
)

class ScraperDolar: # Clase principal
    
    BASE_URL = "https://mindicador.cl/api/dolar" # URL de la API del dólar chileno
    CSV_HEADERS = ["Fecha", "Valor del Dólar (CLP)", "Hora", "Variación Diaria"] # Encabezados del CSV
    HISTORIC_CSV = "dolar_historico.csv" # Archivo CSV para almacenar datos históricos
    
    def __init__(self): # Constructor de la clase
        self.session = requests.Session() # Crea una sesión de requests para reutilizar conexiones
        self.session.headers.update({ # Actualiza los encabezados de la sesión
            "User-Agent": "Mozilla/5.0 (Scraper Dolar Chile)", # User-Agent para evitar bloqueos
            "Accept": "application/json" # Acepta respuestas en formato JSON
        })
    
    def obtener_datos_dolar(self) -> Tuple[Optional[float], Optional[str]]: # Método para obtener el valor actual del dólar desde la API con validación estricta
     
     try:
        response = self.session.get(self.BASE_URL, timeout=10) # Hace una solicitud GET a la API
        response.raise_for_status()  # Lanza error para códigos HTTP 4XX/5XX
        
        data = response.json() # Intenta decodificar la respuesta JSON
        
        # Validación en cascada (estructura de la API)
        if not isinstance(data, dict): # Verifica que la respuesta sea un diccionario
            logging.error("La API no devolvió un diccionario JSON válido") # Registra el error
            return None, None # Retorna None si la estructura es incorrecta
            
        if "serie" not in data: # Verifica que la clave 'serie' exista en el diccionario
            logging.error("La respuesta no contiene la clave 'serie'") # Registra el error
            return None, None # Retorna None si la clave 'serie' no está presente
            
        if not isinstance(data["serie"], list) or len(data["serie"]) == 0: # Verifica que 'serie' sea una lista no vacía
            logging.error("La serie de datos está vacía o no es una lista") # Registra el error
            return None, None # Retorna None si la serie está vacía
            
        primer_item = data["serie"][0] # Obtiene el primer item de la serie
        if "valor" not in primer_item or "fecha" not in primer_item: # Verifica que el primer item tenga las claves 'valor' y 'fecha'
            logging.error("Estructura del item inesperada (falta 'valor' o 'fecha')") # Registra el error
            return None, None # Retorna None si faltan claves
            
        valor_actual = primer_item["valor"] # Obtiene el valor actual del dólar
        fecha_actual = datetime.now().strftime("%Y-%m-%d") # Obtiene la fecha actual en formato YYYY-MM-DD
        
        logging.info(f"Datos obtenidos: ${valor_actual} - Fecha: {fecha_actual}") # Registra la información obtenida
        return valor_actual, fecha_actual # Retorna el valor actual y la fecha
        
     except requests.exceptions.RequestException as e: # Manejo de excepciones de requests
        logging.error(f"Error de conexión con la API: {str(e)}") # Registra el error de conexión
     except ValueError as e: # Manejo de excepciones de decodificación JSON
        logging.error(f"Error al decodificar JSON: {str(e)}") # Registra el error de decodificación
     except Exception as e: # Manejo de excepciones generales
        logging.error(f"Error inesperado: {str(e)}", exc_info=True) # Registra el error
        
     return None, None # Retorna None si hay un error al obtener los datos
    
    # Método para calcular la variación porcentual del valor del dólar respecto al día anterior
    def calcular_variacion(self, valor_actual: float) -> Optional[float]: 
     try:
        # 1. Leer datos históricos
        df = pd.read_csv(self.HISTORIC_CSV, sep=";") # Carga el archivo CSV con los datos históricos
        ultimo_valor_str = df.iloc[-1]["Valor del Dólar (CLP)"] # Obtiene el último valor del dólar del CSV
        
        # 2. Limpiar y convertir formato monetario ($1.234,56 → 1234.56)
        ultimo_valor = float( # Convierte el último valor a float
            ultimo_valor_str.replace("$", "") # Elimina el símbolo de dólar
                          .replace(".", "") # Elimina los puntos de miles
                          .replace(",", ".") # Reemplaza la coma decimal por un punto
        )
        
        # 3. Calcular variación porcentual
        variacion = ((valor_actual - ultimo_valor) / ultimo_valor) * 100 # Calcula la variación porcentual
        variacion_redondeada = round(variacion, 2) # Redondea la variación a 2 decimales
        
        # 4. Registrar información
        logging.info( # Registra la variación calculada
            f"Variación calculada: {variacion_redondeada}% | " # Valor actual: ${valor_actual:,.2f} | "
            f"Valor anterior: ${ultimo_valor:,.2f} → " # Valor anterior: ${ultimo_valor:,.2f} → "
            f"Valor actual: ${valor_actual:,.2f}" # Valor actual: ${valor_actual:,.2f}
        )
        
        return variacion_redondeada # Retorna la variación redondeada
        # Manejo de excepciones al calcular la variación
     except (FileNotFoundError, IndexError, KeyError): # Manejo de excepciones específicas
        logging.warning("No se pudo calcular variación: Sin datos históricos") # Registra una advertencia si no hay datos históricos
        return None # Retorna None si no se puede calcular la variación
     except Exception as e: # Manejo de excepciones generales
        logging.error(f"Error al calcular variación: {str(e)}", exc_info=True) # Registra el error al calcular la variación
        return None # Retorna None si hay un error al calcular la variación
    
    def guardar_datos(self, valor: float, fecha: str) -> None: # Método para guardar los datos en un archivo CSV con formato profesional
        
        try:
            hora_actual = datetime.now().strftime("%H:%M:%S") # Formatea la hora actual
            variacion = self.calcular_variacion(valor) if os.path.exists(self.HISTORIC_CSV) else None # Calcula la variación si el archivo CSV existe
            
            # Formateo profesional del valor
            valor_formateado = f"${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") # Reemplaza el formato de número para que sea profesional
            
            with open(self.HISTORIC_CSV, "a", newline="", encoding="utf-8") as file: # Abre el archivo CSV en modo append
                writer = csv.writer(file, delimiter=";") # Crea un escritor CSV con delimitador ";"
                
                if file.tell() == 0: # Verifica si el archivo está vacío
                    writer.writerow(self.CSV_HEADERS) # Escribe los encabezados si el archivo está vacío
                
                writer.writerow([ # Escribe los datos en el archivo CSV
                    fecha, # Fecha
                    valor_formateado, # Valor del dólar formateado
                    hora_actual, # Hora actual
                    f"{variacion}%" if variacion is not None else "N/A" # Variación diaria formateada
                ])
            
            logging.info("Datos guardados exitosamente") # Registra que los datos se guardaron correctamente
            
        except Exception as e: # Manejo de excepciones al guardar datos
            logging.error(f"Error al guardar datos: {e}") # Registra el error al guardar los datos
    
    def generar_grafico(self) -> None: # Método para generar un gráfico de tendencia del valor del dólar
        
        try:
            df = pd.read_csv(self.HISTORIC_CSV, sep=";") # Carga el archivo CSV con los datos históricos
            
            # Limpieza y conversión de datos
            df["Valor Numérico"] = df["Valor del Dólar (CLP)"].str.replace("$", "") \
                .str.replace(".", "").str.replace(",", ".").astype(float) # Convierte el valor del dólar a float
            df["Fecha"] = pd.to_datetime(df["Fecha"]) # Convierte la columna de fecha a tipo datetime
            
            # Gráfico profesional
            plt.figure(figsize=(12, 6)) # Crea una figura de tamaño 12x6
            plt.plot(df["Fecha"], df["Valor Numérico"], marker="o", linestyle="-", color="blue") # Grafica la serie temporal del valor del dólar
            
            # Personalización
            plt.title("Evolución del Valor del Dólar en Chile", pad=20) # Título del gráfico
            plt.xlabel("Fecha", labelpad=10) # Etiqueta del eje X
            plt.ylabel("Pesos Chilenos (CLP)", labelpad=10) # Etiqueta del eje Y
            plt.grid(True, linestyle="--", alpha=0.7) # Añade una cuadrícula al gráfico
            plt.xticks(rotation=45) # Rota las etiquetas del eje X para mejor legibilidad
            plt.tight_layout() # Ajusta el diseño para que no se solapen los elementos
            
            # Guardado
            plt.savefig("evolucion_dolar.png", dpi=300) # Guarda el gráfico como imagen PNG con alta resolución
            logging.info("Gráfico generado exitosamente") # Registra que el gráfico se generó correctamente
            
        except Exception as e: # Manejo de excepciones al generar el gráfico
            logging.error(f"Error al generar gráfico: {e}") # Registra el error al generar el gráfico


    """ 
       Método para enviar una alerta por email si hay una fluctuación significativa del dólar
       Requiere archivo .env con las variables de entorno:
       EMAIL_FROM: correo de remitente
       EMAIL_TO: correo de destinatario 
       SMTP_SERVER: servidor 
       SMTP_PORT: puerto  
       EMAIL_PASS: contraseña del correo de remitente
    """
    
    def enviar_alerta(self, valor: float, variacion: Optional[float]) -> None:
    
     try:
        # 1. Validar si hay variación significativa (umbral: 2%)
        if variacion is None: # Verifica si la variación es None
            logging.warning("No se envió alerta: Variación es None") # Registra una advertencia si la variación es None
            return # Retorna si no hay variación
            
        if abs(variacion) < 2: # Verifica si la variación es menor al umbral de 2%
            logging.info(f"Variación insuficiente ({variacion}%) para alerta. Umbral: 2%") # Registra información si la variación es insuficiente
            return # Retorna si la variación es insuficiente

        # 2. Preparar contenido del email
        email_subject = f"⚠️ Alerta Dólar: {variacion}% de variación" # Asunto del email con la variación
        email_body = f""" 
        Variación significativa del dólar detectada: 
        
        • Valor actual: ${valor:,.2f} CLP
        • Variación: {variacion}%
        • Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Revisar histórico completo: https://github.com/tuusuario/scraper-dolar-chile
        """
        
        # 3. Configurar mensaje
        msg = MIMEText(email_body.strip()) # Crea el cuerpo del mensaje como texto plano
        msg["Subject"] = email_subject # Asigna el asunto al mensaje
        msg["From"] = os.getenv("EMAIL_FROM") # Asigna el remitente del mensaje desde las variables de entorno
        msg["To"] = os.getenv("EMAIL_TO") # Asigna el destinatario del mensaje desde las variables de entorno

        # 4. Enviar email (con logging descriptivo)
        with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server: # Crea una conexión SMTP
            server.starttls() # Inicia TLS para seguridad
            server.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASS")) # Inicia sesión con las credenciales del remitente
            server.send_message(msg) # Envía el mensaje
            
        logging.info( # Registra que la alerta se envió exitosamente
            f"Alerta enviada exitosamente | " # Mensaje descriptivo
            f"Variación: {variacion}% | " # Variación detectada
            f"Valor: ${valor:,.2f} | " # Valor actual del dólar
            f"Destinatario: {os.getenv('EMAIL_TO')}" # Destinatario del email
        )
        
     except smtplib.SMTPException as e: # Manejo de excepciones específicas de SMTP
        logging.error( # Registra el error al enviar la alerta
            f"Fallo al enviar alerta | " # Mensaje descriptivo
            f"Error SMTP: {str(e)} | "  # Detalle del error SMTP
            f"Código: {e.smtp_code if hasattr(e, 'smtp_code') else 'N/A'}", # Código de error SMTP
            exc_info=True # Información de la excepción
        )
     except Exception as e: # Manejo de excepciones generales
        logging.error( # Registra un error inesperado al enviar la alerta
            f"Error inesperado al enviar alerta | " # Mensaje descriptivo
            f"Tipo: {type(e).__name__} | " # Tipo de excepción
            f"Detalle: {str(e)}", # Detalle del error
            exc_info=True # Información de la excepción
        )

def main(): # Función principal
    scraper = ScraperDolar()
    
    valor, fecha = scraper.obtener_datos_dolar() # Obtiene el valor actual del dólar y la fecha
    if valor and fecha: # Verifica si se obtuvo el valor y la fecha correctamente
        print(f"\n💵 Dólar actual: ${valor:,.2f} CLP") 
        
        scraper.guardar_datos(valor, fecha) # Guarda los datos en el archivo CSV
        scraper.generar_grafico() # Genera el gráfico de evolución del dólar
        
        variacion = scraper.calcular_variacion(valor) # Calcula la variación del dólar respecto al día anterior
        if variacion:
            print(f"📈 Variación: {variacion}% respecto al día anterior") 
            scraper.enviar_alerta(valor, variacion) # Envía una alerta por email si la variación es significativa
        
        print("\n✅ Proceso completado. Revisa los archivos generados:") # Imprime un mensaje de éxito y los archivos generados
        print(f"- Datos históricos: {scraper.HISTORIC_CSV}") # Archivo CSV con los datos históricos
        print("- Gráfico: evolucion_dolar.png") # Imagen del gráfico de evolución del dólar
        print("- Logs: scraper.log") # Archivo de logs con el registro de eventos y errores

if __name__ == "__main__": # Verifica si el script se está ejecutando directamente
    main() # Llama a la función principal para iniciar el scraper