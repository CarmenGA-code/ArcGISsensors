import os
import json
import requests
from datetime import datetime

print("----------------------------------------------------------------")
print("Iniciando descarga automática del histórico semanal de Lascar Cloud...")
print("----------------------------------------------------------------\n")

# ==============================================================================
# 1. CREDENCIALES SEGURAS (Protegidas en los Secrets de GitHub)
# ==============================================================================
API_TOKEN = os.getenv("API_TOKEN")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

CONFIGURACION_SENSOR = {
    "mac": "00:1F:94:03:06:D0",
    "nota": "Aula 1.5 (Temp + RH)"
}

fehors = []
valores = []

try:
    # ==============================================================================
    # 2. LOGIN Y PETICIÓN DE HISTÓRICO A LA API
    # ==============================================================================
    url_login = "https://apiwww.easylogcloud.com/Users.svc/Login"
    params_login = {"APIToken": API_TOKEN, "email": EMAIL, "password": PASSWORD}
    res_login = requests.get(url_login, params=params_login).json()
    user_guid = res_login["GUID"]

    url_device = "https://apiwww.easylogcloud.com/Devices.svc/GetDeviceGUID"
    params_device = {"APIToken": API_TOKEN, "userGUID": user_guid, "MACAddress": CONFIGURACION_SENSOR["mac"]}
    sensor_guid = requests.get(url_device, params=params_device).json()

    url_readings = "https://apiwww.easylogcloud.com/Devices.svc/CurrentReadings"
    params_readings = {"APIToken": API_TOKEN, "userGUID": user_guid, "sensorGUID": sensor_guid, "localTime": True}
    res_readings = requests.get(url_readings, params=params_readings).json()

    canales = res_readings.get("channels", [])
    humedad = 0.0
    if len(canales) > 1 and canales[1]:
        humedad = float(canales[1].replace("%RH", "").strip())

    timestamp_completo = res_readings["datetime"]
    posicion = timestamp_completo.find("(") + 1
    timestamp_recortado = int(timestamp_completo[posicion : posicion + 10])
    fecha_hora_str = datetime.fromtimestamp(timestamp_recortado).strftime("%d %b. %H:%M")

    # ==============================================================================
    # 3. GESTIÓN DEL HISTÓRICO EN 'datos.json'
    # ==============================================================================
    try:
        with open('datos.json', 'r', encoding='utf-8') as f:
            datos_actuales = json.load(f)
    except:
        datos_actuales = {"labels": [], "data": []}

    fehors = datos_actuales.get("labels", [])
    valores = datos_actuales.get("data", [])

    if not fehors or fehors[-1] != fecha_hora_str:
        fehors.append(fecha_hora_str)
        valores.append(humedad)

    datos_para_web = {
        "labels": fehors,
        "data": valores
    }

    with open('datos.json', 'w', encoding='utf-8') as f:
        json.dump(datos_para_web, f, ensure_ascii=False, indent=4)

    print(f"¡Histórico actualizado correctamente! Total de puntos en la gráfica: {len(fehors)}")

except Exception as e:
    print(f"Error al conectar con la plataforma: {e}")
