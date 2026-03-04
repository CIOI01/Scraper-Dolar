# 🤖 Bot Financiero Automatizado: API REST & WhatsApp (Dólar CLP)

Este proyecto es un microservicio automatizado que extrae el valor diario del dólar en Chile, genera análisis históricos, y utiliza Inteligencia Artificial para enviar reportes diarios a través de WhatsApp.

## 🚀 Arquitectura y Flujo de Automatización

El sistema está diseñado bajo una arquitectura de microservicios, separando la extracción de datos de la lógica de distribución:

1. **Orquestación (n8n):** Un flujo de n8n actúa como "reloj" (Schedule Trigger) que se ejecuta todos los días a las 09:00 AM.

2. **Extracción y Procesamiento (Flask API):** n8n hace una petición HTTP GET a esta API (alojada en Render). El servidor Python hace web scraping a la API de `mindicador.cl`, calcula la variación porcentual, guarda el registro histórico en un CSV y genera un gráfico evolutivo usando `pandas` y `matplotlib`.

3. **Análisis con IA (Google Gemini):** Los datos estructurados regresan a n8n, donde son procesados por un prompt en Gemini 2.0 Flash para redactar un análisis financiero profesional y amigable.

4. **Distribución (WhatsApp Cloud API):** Finalmente, n8n utiliza la API oficial de Meta para enviar el texto de la IA, junto con el gráfico PNG y el archivo CSV directamente al usuario vía WhatsApp.

## 🛠️ Stack Tecnológico

- **Backend:** Python 3, Flask, Gunicorn
- **Análisis de Datos:** Pandas, Matplotlib, CSV
- **Integraciones HTTP:** Requests
- **Automatización:** n8n (Node Automation)
- **Inteligencia Artificial:** Google Gemini API
- **Mensajería:** Meta WhatsApp Cloud API
- **Despliegue (CI/CD):** Render (Web Service)

## 📡 Endpoints de la API

La API expone las siguientes rutas principales:

- `GET /api/consultar-dolar`: Ejecuta el scraper, actualiza los datos físicos y devuelve un JSON con el valor actual, variación y URLs de descarga.
- `GET /archivos/<nombre_archivo>`: Sirve de forma segura el gráfico generado (`evolucion_dolar.png`) y el registro histórico (`dolar_historico.csv`).

## 💻 Instalación y Uso Local

Si deseas correr esta API en tu entorno local:

```bash
# 1. Clonar repositorio
git clone [https://github.com/TU-USUARIO/Scraper-Dolar.git](https://github.com/TU-USUARIO/Scraper-Dolar.git)
cd Scraper-Dolar

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar entorno
# Renombra .env.example a .env si usas variables locales (Opcional en esta versión)

# 4. Iniciar el servidor Flask
python scraper_dolar.py
