import json

# Definimos unos datos de prueba temporales
fehors = ["11 sep. 02:00", "11 sep. 02:05", "11 sep. 02:10"]
valores = [36.57, 36.61, 36.70]

datos_para_web = {
    "labels": fehors,  
    "data": valores    
}

with open('datos.json', 'w', encoding='utf-8') as f:
    json.dump(datos_para_web, f, ensure_ascii=False, indent=4)

print("¡Datos guardados con éxito!")
