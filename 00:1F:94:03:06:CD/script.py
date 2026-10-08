import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta

print("----------------------------------------------------------------")
print("Iniciando descarga y generación de gráficos de los últimos 7 días...")
print("----------------------------------------------------------------\n")

# ==============================================================================
# 1. CREDENCIALES Y CONFIGURACIÓN (Solo modificas la MAC del sensor que quieras)
# ==============================================================================
API_TOKEN = os.getenv("API_TOKEN")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

CONFIGURACION_SENSOR = {
    "mac": "00:1F:94:03:06:CD",  # Cambia esta MAC para cada sensor que despliegues
}

try:
    # ==============================================================================
    # 2. LOGIN Y OBTENCIÓN DE GUIDs Y NOMBRE DEL DISPOSITIVO
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
    FECHA_FIN_html = ahora.strftime('%d/%m/%Y')
    
    fecha_inicio_dt = ahora - timedelta(days=7)
    FECHA_INICIO = fecha_inicio_dt.strftime('%m/%d/%Y')
    FECHA_INICIO_html = fecha_inicio_dt.strftime('%d/%m/%Y')

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

            temp = float(str(channels[0]).replace("°C", "").strip()) if channels[0] is not None else 0.0
            hum = float(str(channels[1]).replace("%RH", "").strip()) if channels[1] is not None else 0.0
            co2 = float(str(channels[2]).replace("ppm", "").strip()) if len(channels) > 2 and channels[2] is not None else 0.0

            filas_matriz.append([fecha_hora, temp, hum, co2])

    matriz_df = pd.DataFrame(filas_matriz, columns=["FECHA_HORA", "TEMPERATURA", "HUMEDAD", "CO2"])
    matriz_df = matriz_df.sort_values("FECHA_HORA")

    fechas_list = matriz_df["FECHA_HORA"].dt.strftime("%d %b. %H:%M").tolist()
    temp_list = matriz_df["TEMPERATURA"].round(2).tolist()
    hum_list = matriz_df["HUMEDAD"].round(2).tolist()
    co2_list = matriz_df["CO2"].round(0).tolist()

    # ==============================================================================
    # 6. GUARDAR EN 'datos.json'
    # ==============================================================================
    datos_para_web = {
        "labels": fechas_list,
        "temperatura": temp_list,
        "humedad": hum_list,
        "co2": co2_list
    }

    with open('datos.json', 'w', encoding='utf-8') as f:
        json.dump(datos_para_web, f, ensure_ascii=False, indent=4)
    print("¡Archivo datos.json actualizado con éxito!")

    # ==============================================================================
    # 7. GENERACIÓN DE LOS ARCHIVOS HTML INTERACTIVOS (Sin mención a espacios)
    # ==============================================================================
    
    def generar_html(nombre_variable, unidad_medida, titulo_grafico, lista_valores, nombre_archivo):
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{titulo_grafico}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1/dist/chartjs-plugin-zoom.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f9; margin: 0; padding: 20px; }}
        .nav {{ margin-bottom: 20px; }}
        .nav a {{ margin: 0 10px; text-decoration: none; font-weight: bold; color: #0066cc; padding: 8px 15px; background: white; border-radius: 4px; box-shadow: 0px 2px 5px rgba(0,0,0,0.1); }}
        .nav a.active {{ background: #0066cc; color: white; }}
        .container {{ background: white; padding: 20px; border-radius: 8px; display: inline-block; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); width: 95%; max-width: 1200px; }}
        .instructions {{ margin-bottom: 15px; font-size: 14px; color: #555; }}
        .chart-wrapper {{ position: relative; width: 100%; height: 500px; }}
        canvas {{ width: 100% !important; height: 100% !important; }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="index.html" class="{'active' if nombre_archivo=='index.html' else ''}">Temperatura</a>
        <a href="humedad.html" class="{'active' if nombre_archivo=='humedad.html' else ''}">Humedad</a>
        <a href="co2.html" class="{'active' if nombre_archivo=='co2.html' else ''}">CO2</a>
    </div>

    <div class="container">
        <div class="instructions">
            💡 <b>Interactivo:</b> Pasa el cursor para ver coordenadas exactas. Usa la rueda del ratón o arrastra para hacer zoom.
        </div>
        <div class="chart-wrapper">
            <canvas id="sensorChart"></canvas>
        </div>
    </div>
    <script>
        const ctx = document.getElementById('sensorChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(fechas_list)},
                datasets: [{{
                    label: '{nombre_variable} ({unidad_medida})',
                    data: {json.dumps(lista_valores)},
                    borderColor: 'crimson',
                    backgroundColor: 'rgba(220, 20, 60, 0.1)',
                    borderWidth: 1.5,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    fill: false,
                    tension: 0.1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: '{titulo_grafico} ({FECHA_INICIO_html} al {FECHA_FIN_html})',
                        font: {{ size: 16, weight: 'bold' }}
                    }},
                    legend: {{ display: false }},
                    zoom: {{
                        zoom: {{ wheel: {{ enabled: true }}, pinch: {{ enabled: true }}, mode: 'x' }},
                        pan: {{ enabled: true, mode: 'x' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Generado archivo: {nombre_archivo}")

    # Generación de archivos limpios centrados exclusivamente en las mediciones
    generar_html("Temperatura", "ºC", "Evolución de Temperatura", temp_list, "index.html")
    generar_html("Temperatura", "ºC", "Evolución de Temperatura", temp_list, "temperatura.html")
    generar_html("Humedad", "%", "Evolución de Humedad", hum_list, "humedad.html")
    generar_html("CO2", "ppm", "Evolución de CO2", co2_list, "co2.html")

    print("\n¡Proceso completo y generación de web finalizada con éxito!")

except Exception as e:
    print(f"Error durante la ejecución del script: {e}")
