import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta

print("----------------------------------------------------------------")
print("Iniciando descarga del histórico de los últimos 7 días...")
print("----------------------------------------------------------------\n")

# ==============================================================================
# 1. CREDENCIALES SEGURAS (Leídas desde los Secrets de GitHub)
# ==============================================================================
API_TOKEN = os.getenv("API_TOKEN")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

CONFIGURACION_SENSOR = {
    "mac": "00:1F:94:03:06:D0",
    "nota": "Aula 1.5 (Temp + RH + CO2)"
}

try:
    # ==============================================================================
    # 2. LOGIN Y OBTENCIÓN DE GUIDs
    # ==============================================================================
    url_login = "https://apiwww.easylogcloud.com/Users.svc/Login"
    params_login = {"APIToken": API_TOKEN, "email": EMAIL, "password": PASSWORD}
    res_login = requests.get(url_login, params=params_login).json()
    user_guid = res_login["GUID"]

    url_device = "https://apiwww.easylogcloud.com/Devices.svc/GetDeviceGUID"
    params_device = {"APIToken": API_TOKEN, "userGUID": user_guid, "MACAddress": CONFIGURACION_SENSOR["mac"]}
    sensor_guid = requests.get(url_device, params=params_device).json()

    # ==============================================================================
    # 3. CÁLCULO DE FECHAS (Últimos 7 días)
    # ==============================================================================
    ahora = datetime.now()
    FECHA_FIN = ahora.strftime('%m/%d/%Y')
    fecha_inicio_dt = ahora - timedelta(days=7)
    FECHA_INICIO = fecha_inicio_dt.strftime('%m/%d/%Y')

    # ==============================================================================
    # 4. PETICIÓN DEL HISTÓRICO DE 7 DÍAS A LA API
    # ==============================================================================
    url_readings = "https://apiwww.easylogcloud.com/Devices.svc/Readings"
    params_readings = {
        "APIToken": API_TOKEN,
        "userGUID": user_guid,
        "sensorGUID": sensor_guid,
        "startDate": FECHA_INICIO,
        "endDate": FECHA_FIN,
        "samplesOnly": True
    }
    
    respuesta = requests.get(url_readings, params=params_readings)
    datos_crudos = respuesta.json()

    if not isinstance(datos_crudos, list) or len(datos_crudos) == 0:
        print("Aviso: No se han recibido datos en el rango de fechas especificado.")
        exit()

    # ==============================================================================
    # 5. PROCESAMIENTO DE DATOS CON PANDAS
    # ==============================================================================
    filas_matriz = []
    for item in datos_crudos:
        datetime_val = item.get("datetime")
        channels = item.get("channels", [])

        if datetime_val and len(channels) >= 2:
            posicion = datetime_val.find("(") + 1
            timestamp_recortado = int(datetime_val[posicion : posicion + 10])
            fecha_hora = datetime.fromtimestamp(timestamp_recortado)

            # Extraer valores limpiando unidades si vienen como texto
            temp = float(str(channels[0]).replace("°C", "").strip()) if channels[0] is not None else 0.0
            hum = float(str(channels[1]).replace("%RH", "").strip()) if channels[1] is not None else 0.0
            co2 = float(str(channels[2]).replace("ppm", "").strip()) if len(channels) > 2 and channels[2] is not None else 0.0

            filas_matriz.append([fecha_hora, temp, hum, co2])

    matriz_df = pd.DataFrame(filas_matriz, columns=["FECHA_HORA", "TEMPERATURA", "HUMEDAD", "CO2"])
    matriz_df = matriz_df.sort_values("FECHA_HORA")

    # ==============================================================================
    # 6. GUARDAR EN 'datos.json' PARA LA WEB
    # ==============================================================================
    fechas_list = matriz_df["FECHA_HORA"].dt.strftime("%d %b. %H:%M").tolist()
    temp_list = matriz_df["TEMPERATURA"].round(2).tolist()
    hum_list = matriz_df["HUMEDAD"].round(2).tolist()
    co2_list = matriz_df["CO2"].round(0).tolist()

    datos_para_web = {
        "labels": fechas_list,
        "temperatura": temp_list,
        "humedad": hum_list,
        "co2": co2_list
    }

    with open('datos.json', 'w', encoding='utf-8') as f:
        json.dump(datos_para_web, f, ensure_ascii=False, indent=4)

    print(f"¡Histórico de 7 días actualizado con éxito! Puntos procesados: {len(fechas_list)}")

except Exception as e:
    print(f"Error durante la obtención del histórico: {e}")
