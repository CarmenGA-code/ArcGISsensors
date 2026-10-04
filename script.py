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

CONFIGURACION_SENSOR = {
    "capa": "DT_Monitored_spaces_WSL12",
    "mac": "00:1F:94:03:06:D0",
    "nota": "Aula 1.5 (CO2 + Temp + RH)"
}

fehors = []
valores = []

try:
    # ==============================================================================
    # 2. PETICIÓN A LA API DE LASCAR CLOUD
    # ==============================================================================
    # (Aquí iría la llamada real cuando conectemos los endpoints definitivos)
    print("Conexión configurada para el sensor con MAC:", CONFIGURACION_SENSOR['mac'])

except Exception as e:
    print(f"Error al conectar con la plataforma: {e}")

# ==============================================================================
# 3. GUARDAR LOS DATOS EN 'datos.json' PARA LA WEB DE GITHUB PAGES
# ==============================================================================
datos_para_web = {
    "labels": fehors,  # Fechas y horas para el eje X
    "data": valores    # Valores de humedad para el eje Y
}

with open('datos.json', 'w', encoding='utf-8') as f:
    json.dump(datos_para_web, f, ensure_ascii=False, indent=4)

print("¡Proceso finalizado! El archivo datos.json se ha actualizado correctamente.")
