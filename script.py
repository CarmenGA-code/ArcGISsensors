import json
import requests
from datetime import datetime

print("----------------------------------------------------------------")
print("Iniciando conexión automática con Lascar Cloud para la web...")
print("----------------------------------------------------------------\n")

# ==============================================================================
# 1. CREDENCIALES Y CONFIGURACIÓN DEL SENSOR
# ==============================================================================
API_TOKEN = "6b853ae5-6661-11f1-a86d-0aeee635d34b"
EMAIL = "Carmen.Gomez@uclm.es"
PASSWORD = "@Dtwin2025"

CONFIGURACION_SENSOR = {
    "mac": "00:1F:94:03:06:D0",
    "nota": "Aula 1.5 (Temp + RH)"
}

try:
    # ==============================================================================
    # 2. LOGIN Y PETICIÓN A LA API DE LASCAR CLOUD
    # ==============================================================================
    url_login = "https://apiwww.easylogcloud.com/Users.svc/Login"
    params_login = {"APIToken": API_TOKEN, "email": EMAIL, "password": PASSWORD}
    res_login = requests.get(url_login, params=params_login).json()
    user_guid = res_login["GUID"]

    # Obtener Device GUID
    url_device = "https://apiwww.easylogcloud.com/Devices.svc/GetDeviceGUID"
    params_device = {"APIToken": API_TOKEN, "userGUID": user_guid, "MACAddress": CONFIGURACION_SENSOR["mac"]}
    sensor_guid = requests.get(url_device, params=params_device).json()

    # Obtener lecturas actuales del sensor
    url_readings = "https://apiwww.easylogcloud.com/Devices.svc/CurrentReadings"
    params_readings = {"APIToken": API_TOKEN, "userGUID": user_guid, "sensorGUID": sensor_guid, "localTime": True}
    res_readings = requests.get(url_readings, params=params_readings).json()

    canales = res_readings.get("channels", [])
    
    # Extraer el valor de humedad (suele estar en el canal índice 1)
    humedad = 0.0
    if len(canales) > 1 and canales[1]:
        humedad = float(canales[1].replace("%RH", "").strip())

    # Procesar la fecha y hora de la lectura
    timestamp_completo = res_readings["datetime"]
    posicion = timestamp_completo.find("(") + 1
    timestamp_recortado = int(timestamp_completo[posicion : posicion + 10])
    fecha_hora_str = datetime.fromtimestamp(timestamp_recortado).strftime("%d %b. %H:%M")

    # ==============================================================================
    # 3. ACTUALIZAR 'datos.json' ACUMULANDO EL HISTÓRICO
    # ==============================================================================
    try:
        with open('datos.json', 'r', encoding='utf-8') as f:
            datos_actuales = json.load(f)
    except:
        datos_actuales = {"labels": [], "data": []}

    # Evitamos duplicar si la hora es exactamente la misma
    if not datos_actuales["labels"] or datos_actuales["labels"][-1] != fecha_hora_str:
        datos_actuales["labels"].append(fecha_hora_str)
        datos_actuales["data"].append(humedad)

    # Guardar el archivo JSON actualizado
    with open('datos.json', 'w', encoding='utf-8') as f:
        json.dump(datos_actuales, f, ensure_ascii=False, indent=4)

    print(f"¡Lectura añadida con éxito! -> Fecha: {fecha_hora_str} | Humedad: {humedad}%")

except Exception as e:
    print(f"Error al conectar con la plataforma: {e}")
