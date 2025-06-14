# 📊 Scraper del Dólar Chileno

Aplicación que obtiene el valor diario del dólar desde la API de Mindicador.cl, lo almacena en CSV, genera gráficos y envía alertas por email.

## 🚀 Características

- **Scraping automático**: Obtiene el valor actualizado del dólar.
- **Almacenamiento**: Guarda histórico en CSV con formato profesional.
- **Visualización**: Genera gráficos con matplotlib.
- **Alertas**: Envía emails cuando hay fluctuaciones significativas (>2%).


## 📦 Requisitos

- Python 3.7 o superior
- Librerías especificadas en `requirements.txt`
- Cuenta de email para las alertas (opcional)


### Instalacion
```bash
# Clonar repositorio
git clone https://github.com/CIOI01/Scraper-Dolar.git
cd scraper-dolar-chile

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (copiar .env.example a .env)
cp .env.example .env
nano .env  # Editar con tus credenciales

# Ejecutar
python scraper_dolar.py

## Solución de Problemas

### Error de conexión con la API
Si recibes errores de conexión, verifica:
1. Tu conexión a internet
2. Que la API (https://mindicador.cl/api/dolar) esté disponible

### Problemas con el envío de emails
- Verifica que las credenciales en `.env` sean correctas
- Para Gmail, es posible que necesites habilitar "Acceso de apps menos seguras"
- Verifica que el puerto SMTP sea el correcto para tu proveedor