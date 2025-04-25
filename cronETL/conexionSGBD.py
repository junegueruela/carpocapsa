# coding: utf-8
# Módulo personalizado para obtener los datos de estación y municipio y almacenarlos en el SGBD

import pyodbc
import pandas as pd
import warnings
import datetime
import sqlalchemy
from sqlalchemy import create_engine, text

##Ignoramos los warnings
warnings.filterwarnings('ignore')
## Utilizamos mejor sqlalchemy
__engine = create_engine('mysql+mysqlconnector://Plagas:plagas@mySqlDocker:3306/Plagas') ## Para el docker
##__engine = create_engine('mysql+mysqlconnector://Plagas:plagas@127.0.0.1:3306/Plagas')  ## Para local
##__engine = create_engine('mssql+pyodbc://plagas:Plagas@DESKTOP-DOEKCPE\\SQLEXPRESS/Plagas?driver=ODBC+Driver+17+for+SQL+Server') ##Para SqlServer
## Definimos un formato de fecha por defecto
date_format= '%Y-%m-%d'

## PROCEDIMIENTOS COMUNES PARA TODAS LAS OPERACIONES DE BASE DE DATOS

## Procedimiento genérico que inserta en la tabla el dataframe df que le pasamos como parámetro.
def insertaTabla(tabla, df):
    df.to_sql(tabla, con=__engine, if_exists='append', index=False) 

## Funcion genérica que me ejecuta una query 
def ejecuteQuery(query):
    df = pd.read_sql_query(query, con=__engine)
    return df 

### ESTACIONES. FUNCIONES Y PROCEDIMIENTOS PARA OBTENER DATOS DE ESTACIONES

### Obtención de la mayor fecha con datos para una estación en concreto
def getFechaMaxima(estacion):
    date_format= '%Y-%m-%d'
    maxT='select max(fecha) as fecha_MAX from TemperaturasDiarias where Estacion='+estacion
    df_fecha=ejecuteQuery( maxT)
    return df_fecha["fecha_MAX"][0]

### Obtención de las TODAS estaciones que tenemos en base de datos
def getEstaciones():
    query='select estacion, municipio from Estaciones' 
    df=ejecuteQuery(query)
    #fechaDate=convertirDate(df_fecha["fecha_MAX"][0])
    return df



## PROCEDIMIENTOS Y FUNCIONES PARA TRABAJAR CON TEMPERATURAS DIARIAS.

## Procedimiento que inserta un df de las temperaturas diarias en base de datos.
def insertarDatosTiempo(df):
    insertaTabla('TemperaturasDiarias',df)

## PROCEDIMIENTOS Y FUNCIONES PARA TRABAJAR CON MUNICIPIOS

### Obtención de los municipios que tenemos en base de datos
def getMunicipios():
    query='select * from Municipios' 
    df=ejecuteQuery(query)
    #fechaDate=convertirDate(df_fecha["fecha_MAX"][0])
    return df

## PROCEDIMIENTOS Y FUNCIONES PARA TRABAJAR CON PREDICCIONES

## Procedimiento que inserta un df de la predicción meterorológica.
def insertarPrediccion(df):
    insertaTabla('PrediccionAEMET',df)

## Procedimiento para borrar la predicción de un municipio
## Por ejemplo, si los datos no son completos.
def borraPrediccion(idMunicipio):
    date_format= '%Y-%m-%d'
    sql="delete from PrediccionAEMET where idMunicipio=:id"
    with __engine.connect() as connection:
        connection.execute(text(sql), {"id": idMunicipio})
        connection.commit()  # Asegúrate de hacer commit si es necesario


