# Usa una imagen oficial de Python como base
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY . . 

# Instala las dependencias listadas en requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define un volumen para guardar los datos persistentes (CSV y gráficos)
VOLUME /app/data

# Comando que se ejecutará al iniciar el contenedor
CMD ["python", "scraper_dolar.py"]