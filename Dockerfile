# Usa una imagen base liviana de Python
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de dependencias
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente de la API
COPY . .

# Expone el puerto en el que uvicorn correrá
EXPOSE 8000

# Ejecuta la aplicación desde main.py, que está en el mismo directorio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
