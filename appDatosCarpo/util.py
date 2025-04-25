# coding: utf-8
import datetime
import numpy as np
import math
import os
import pandas as pd
##os.chdir('D:\\Plagas')


## Trabajar con fechas, para insertar en sql hay que convertir a dd-mm-YYYY
## Me devuelve una fecha con un formato string para poder insertarlo en sql server (que me hace la conversión él)
## Lo usaremos si es un CSV
def convertirString(fecha,origen='otros'):
    out_format= '%Y-%m-%d'
    if (origen=='CSV'):
        in_format='%d/%m/%Y'
    elif (origen=='CSVL'):
          in_format='%Y%m%d'
    elif (origen=='BD'):
        in_format='%Y-%m-%d'
    elif (origen=='AEMET'):
        in_format='%Y-%m-%dT%H:%M:%S'
    else:
        in_format='%Y-%m-%d %H:%M:%S'
    ##in_format='%Y-%m-%d %H:%M:%S'
    fecha=datetime.datetime.strptime(fecha, in_format)
    strfecha=fecha.strftime(out_format)
    return strfecha

## Función que me calcula la distancia entre dos puntos (con latitud y longitud)
def haversine(lat1, lon1, lat2, lon2):
    # Radio de la Tierra en kilómetros
    R = 6371.0

    # Convertir las coordenadas de grados a radianes
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Diferencias de coordenadas
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Fórmula del Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance


## Función que me devuelve un dataframe con la leyenda
def leyendaTiempo():
    data = [
        ("TMax", "Temperatura del aire máxima (ºC)"),
        ("TMed", "Temperatura del aire media (ºC)"),
        ("TMin", "Temperatura del aire mínima (ºC)"),
        ("TsMax", "Temperatura en superficie máxima (ºC)"),
        ("TsMed", "Temperatura en superficie media (ºC)"),
        ("TsMin", "Temperatura en superficie mínima (ºC)"),
        ("HrMax", "Humedad relativa máxima (%)"),
        ("HrMed", "Humedad relativa media (%)"),
        ("HrMin", "Humedad relativa mínima (%)"),
        ("PAc", "Precipitación acumulada (l/m²)"),
        ("ProbPrecip", "Probabilidad de precipitaciones (%)"),
        ("RgAc", "Radiación acumulada (Mj/m²)"),
        ("VVMax", "Velocidad del viento máxima (km/h)"),
        ("VVMed", "Velocidad del viento media (km/h)")
    ]

    # Convertir la lista en un DataFrame
    df = pd.DataFrame(data, columns=["Variable", "Leyenda"])
    return df

def leyendaTiempoCorta():
    data = [
        ("TMax", "Temperatura del aire máxima (ºC)"),
        ("TMed", "Temperatura del aire media (ºC)"),
        ("TMin", "Temperatura del aire mínima (ºC)"),
        ("PAc", "Precipitación acumulada (l/m²)"),
        ("VVMed", "Velocidad del viento media (km/h)")
    ]
    # Convertir la lista en un DataFrame
    df = pd.DataFrame(data, columns=["Variable", "Leyenda"])
    return df

    # Convertir la lista en un DataFrame
    df = pd.DataFrame(data, columns=["Variable", "Leyenda"])
    return df





