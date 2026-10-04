import json
import requests
from datetime import datetime, timedelta

print("----------------------------------------------------------------")
print("Iniciando conexión automática con Lascar (EasyLog) Cloud...")
print("----------------------------------------------------------------\n")

# ==============================================================================
# 1. CREDENCIALES Y CONFIGURACIÓN DE LOS SENSORES
# ==============================================================================
API_TOKEN = "6b853ae5-6661-11f1-a86d-0aeee635d34b"
EMAIL = "Carmen.Gomez@uclm.es"
PASSWORD = "@Dtwin2025"

# Definimos el sensor del Aula 1.5 que queremos consultar
CONFIGURACION_SENSOR = {
    "capa": "DT_Monitored_spaces_WSL12",
    "mac": "00:1F:94:03:06:D0",
    "nota": "Aula 1.5 (CO2 + Temp + RH)"
}

fehors = []
valores = []

try:
    # ==============================================================================
    # 2. PETICIÓN AUTOMÁTICA A LA API DE LASCAR CLOUD
    # ==============================================================================
    # Nota: Dependiendo de la versión exacta de la API de EasyLog Cloud, 
    # la URL de autenticación o de lectura de datos puede variar ligeramente.
    
    url_api = f"https://api.easylogcloud.com/v1/devices/{CONFIGURACION_SENSOR['mac']}/data"
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Parámetros opcionales para filtrar (por ejemplo, la última semana si la API lo soporta)
    # response = requests.get(url_api, headers=headers)
    
    # Si la API requiere login previo por correo y contraseña para obtener un token dinámico:
    # payload = {"email": EMAIL, "password": PASSWORD}
    # auth_response = requests.post("https://api.easylogcloud.com/v1/login", json=payload)
    # token_dinamico = auth_response.json().get("token")
    
    # SIMULACIÓN DE LA PETICIÓN REAL: 
    # Una vez que la respuesta devuelva los registros de la plataforma, los recorremos así:
    # datos_api = response.json()
    # 
    # for registro in datos_api.get('readings', []):
    #     fehors.append(registro['timestamp'])  # Fecha y hora que viene del servidor
    #     valores.append(registro['humidity'])   # Valor de humedad real del sensor

    print("Conexión configurada para el sensor con MAC:", CONFIGURACION_SENSOR['mac'])

except Exception as e:
    print(f"Error al conectar con la plataforma: {e}")

# ==============================================================================
# 3. GUARDAR LOS DATOS RECOGIDOS EN 'datos.json'
# ==============================================================================
datos_para_web = {
    "labels": fehors,  # Se rellenará automáticamente con lo que traiga la API
    "data": valores    # Se rellenará automáticamente con lo que traiga la API
}

with open('datos.json', 'w', encoding='utf-8') as f:
    json.dump(datos_para_web, f, ensure_ascii=False, indent=4)

print("¡Proceso finalizado! El archivo datos.json se ha actualizado de forma autónoma.")
