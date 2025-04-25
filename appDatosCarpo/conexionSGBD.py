# coding: utf-8

import pyodbc
import pandas as pd
import warnings
import datetime
import sqlalchemy
from sqlalchemy import create_engine, text

##Ignoramos los warnings
warnings.filterwarnings('ignore')
## Utilizamos mejor sqlalchemy
__engine = create_engine('mysql+mysqlconnector://Plagas:Plagas@mySqlDocker:3306/Plagas') ## Para el docker
##__engine = create_engine('mysql+mysqlconnector://Plagas:plagas@103.241.67.163:3306/Plagas') ## Para el docker
##__engine = create_engine('mysql+mysqlconnector://Plagas:plagas@127.0.0.1:3306/Plagas')  ## Para local

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

## PROCEDIMIENTOS DE AUTENTICACIÓN

### Autenticación de usuario. Nos devuelve la clave
def getClave(usuario):
    aut="select clave from Usuarios where login='"+usuario+"'"
    cuenta=ejecuteQuery(aut)
    if cuenta.empty:
        return "no existe"
    else:
        return cuenta["clave"][0]

### Get usuario por nombre, a través del id de usuario nos devuelve los datos del usuario
def getUsuarioPorLogin(id):
    aut="select idusuario as id, login as usuario, clave, email, tecnico, nombre from Usuarios where login='"+str(id)+"'"
    cuenta=ejecuteQuery(aut)
    return cuenta

### Get usuario por id, a través del id de usuario nos devuelve los datos del usuario
def getUsuarioPorID(id):
    aut="select idusuario as id, login as usuario,  clave, email, tecnico, nombre from Usuarios where idusuario="+str(id)
    cuenta=ejecuteQuery(aut)
    return cuenta
## Actualizamos la clave de usuario
def actualizaClave(id, clave):
    sql="update Usuarios set clave = :clave where idUsuario = :id"
    with __engine.connect() as connection:
        connection.execute(text(sql), {"id": id,"clave":clave})
        connection.commit() 


### ESTACIONES. FUNCIONES Y PROCEDIMIENTOS PARA OBTENER DATOS DE ESTACIONES

### Obtención de la mayor fecha con datos para una estación en concreto
def getFechaMaxima(estacion):
    date_format= '%Y-%m-%d'
    maxT='select max(fecha) as fecha_MAX from TemperaturasDiarias where Estacion='+estacion
    df_fecha=ejecuteQuery( maxT)
    return df_fecha["fecha_MAX"][0]



### Obtención de la mayor fecha con datos para una estación en concreto
def getFechaMinima(estacion):
    date_format= '%Y-%m-%d'
    minT='select min(fecha) as fecha_MIN from TemperaturasDiarias where Estacion='+estacion
    df_fecha=ejecuteQuery( minT)
    return df_fecha["fecha_MIN"][0]



### Obtención de las TODAS estaciones que tenemos en base de datos
def getEstaciones():
    query='select estacion, municipio from Estaciones' 
    df=ejecuteQuery(query)
    return df

### Obtención de  los datos de una estación por su Id.
def getEstacion(estacion):
    date_format= '%Y-%m-%d'
    sqlEstacion='select * from Estaciones where estacion='+estacion
    df=ejecuteQuery( sqlEstacion)
    return df

### Obtención de un resumen de los últimos datos recogidos por estación
def getUltimosDatosEstaciones():
    query='''SELECT e.estacion estacion, e.municipio localidad, e.altitud altitud, t.fecha, tMax, tMed, tMin, PAc, VVMed
        FROM TemperaturasDiarias t
        JOIN Estaciones e ON t.estacion = e.estacion
        JOIN (
            SELECT estacion, MAX(fecha) AS max_fecha
            FROM TemperaturasDiarias
            GROUP BY estacion
        ) t2 ON t.estacion = t2.estacion AND t.fecha = t2.max_fecha''' 
    df=ejecuteQuery(query)
    return df

### PROCEDIMIENTOS Y FUNCIONES PARA OPERAR CON LOS VUELOS

## Nos devuelve un dataframe con los datos de vuelos para un término dado entre fechaMin y fechaMax
def getDatosVuelos(termino,fechaMin='2005-01-01',fechaMax=datetime.datetime.today().strftime("%Y-%m-%d")):
    queryDatos="SELECT idVuelo, fecha, valor as vuelos" \
    + ' FROM VuelosCarpo' \
    +      " WHERE idTermino="+termino+" AND fecha between '"+fechaMin+"' AND '"+fechaMax+"' order by fecha desc;"
    df_DatosTiempo=ejecuteQuery(queryDatos)
    ## Convierto la fecha a fecha
    df_DatosTiempo['fecha']=pd.to_datetime(df_DatosTiempo['fecha'])
    return df_DatosTiempo

## Nos devuelve un dataframe con los datos de los últimos vuelos para un término dado, por defecto, 30
def getUltimosVuelos(termino,nCapturas=30):
    strCapturas=str(nCapturas)
    queryDatos="SELECT idVuelo, fecha, valor as vuelos" \
    + ' FROM VuelosCarpo' \
    +      " WHERE idTermino="+termino+" order by fecha desc LIMIT "+strCapturas+";"
    df_DatosTiempo=ejecuteQuery(queryDatos)
    ## Convierto la fecha a fecha
    if len(df_DatosTiempo)>0:
        df_DatosTiempo['fecha']=pd.to_datetime(df_DatosTiempo['fecha'])
    return df_DatosTiempo

### Obtención de los terminos y municipios que tenemos en base de datos
## Esto nos permitirá seleccionar una finca para luego consultas sus vuelos o añadir nuevos.
def getTerminos():
    query= "select idTermino, concat(Municipio,' -  ',Termino) as Termino from Terminos T, Municipios M " \
    + "where M.idMunicipio=T.idMunicipio order by Termino"
    df=ejecuteQuery(query)
    return df

## Nos devuelve el término del idVuelo indicado. 
def getTermino(idVuelo):
    queryDatos="SELECT idTermino" \
    + ' FROM VuelosCarpo' \
    +      " WHERE idVuelo="+idVuelo+";"
    df_DatosTiempo=ejecuteQuery(queryDatos)
    return df_DatosTiempo['idTermino'][0]

## Procedimiento para insertar un vuelo o conjunto (dataframe) de vuelos..
def insertarVuelo(df):
    insertaTabla('VuelosCarpo',df)

## Borramos un vuelo por su id
def borraVuelo(id):
    sql="delete from VuelosCarpo where idVuelo = :id"
    with __engine.connect() as connection:
        connection.execute(text(sql), {"id": id})
        connection.commit()  

## PROCEDIMIENTOS Y FUNCIONES PARA TRABAJAR CON TEMPERATURAS DIARIAS.

## Nos devuelve un dataframe con los datos metereológicos de la estación indicada en el periodo entre fechaMin y fechaMax
def getDatosTiempo(estacion,fechaMin='2005-01-01',fechaMax=datetime.datetime.today().strftime("%Y-%m-%d")):
    queryDatos="SELECT Estacion, fecha, TMax, TMed, TMin, TsMax, TsMed, TsMin, HrMax, HrMed, HrMin, PAc, RgAc, VVMax, VVMed" \
    + ' FROM TemperaturasDiarias' \
    +      " WHERE Estacion="+estacion+" AND fecha between '"+fechaMin+"' AND '"+fechaMax+"' order by fecha desc;"
    df_DatosTiempo=ejecuteQuery(queryDatos)
    ## Convierto la fecha a fecha
    df_DatosTiempo['fecha']=pd.to_datetime(df_DatosTiempo['fecha'])
    return df_DatosTiempo


## Nos devuelve un dataframe con los datos metereológicos de la estación indicada, de las últimas n entradas
def getDatosTiempoDias(estacion,ndias=30):
    queryDatos="SELECT Estacion, fecha, TMax, TMed, TMin, TsMax, TsMed, TsMin, HrMax, HrMed, HrMin, PAc, RgAc, VVMax, VVMed" \
    + ' FROM TemperaturasDiarias' \
    +      " WHERE Estacion="+estacion+" order by fecha desc LIMIT "+str(ndias)+";"
    df_DatosTiempo=ejecuteQuery(queryDatos)
    ## Convierto la fecha a fecha
    df_DatosTiempo['fecha']=pd.to_datetime(df_DatosTiempo['fecha'])
    return df_DatosTiempo

## Procedimiento que inserta un df de las temperaturas diarias en base de datos.
def insertarDatosTiempo(df):
    insertaTabla('TemperaturasDiarias',df)

## Procedimiento para borrar un rango de temperaturas para una estación.
## Por ejemplo, si los datos no son completos.
def borraDatosTemperatura(idEstacion, fechaMin, fechaMax):
    date_format= '%Y-%m-%d'
    sql="delete from TemperaturasDiarias where Estacion=:id and fecha >= :fechaMin and fecha <= :fechaMax"
    with __engine.connect() as connection:
        connection.execute(text(sql), {"id": idEstacion,"fechaMin":fechaMin,"fechaMax":fechaMax})
        connection.commit()  # Asegúrate de hacer commit si es necesario

## PROCEDIMIENTOS Y FUNCIONES PARA OPERAR CON MUNICIPIOS

### Obtención de los municipios que tenemos en base de datos
def getMunicipios():
    query='select * from Municipios' 
    df=ejecuteQuery(query)
    return df

### Obtención de los municipios que tenemos en base de datos y sus estaciones de referencia
def getMunicipiosEstacion():
    query='''select m.idMunicipio idMunicipio, m.municipio Municipio, m.altitud altitudMunicipio,
		        e.estacion as idEstacion, e.municipio Estacion, 
                distancia, difAltitud
	        from Municipios m, Estaciones e, DistanciasEst de
         where de.idMunicipio=m.idMunicipio 
           and de.estacion=e.estacion
           and m.estacion=e.estacion''' 
    df=ejecuteQuery(query)
    return df

## Obtiene los datos medios de los últimos x días (22, por defecto) para la última fecha
def getModelo(municipio,dias=22):
    queryDatos= '''select TD1.fecha fecha, round(sum(TD2.TMed-10),2) diasGrado,
       round(avg(TD2.TMed),2) TMed , round(avg(TD2.HrMed),2) HrMed,
	   round(sum(TD2.Pac),2) Pac, round(avg(TD2.VVMed),2) VVMed
 from TemperaturasDiarias TD1, TemperaturasDiarias TD2, Municipios M
  where TD1.Estacion = TD2.Estacion
   and M.idMunicipio  = ''' +str(municipio) + \
'''   and TD2.fecha <=TD1.fecha
   and TD2.fecha >  date_add(TD1.fecha,interval - '''+str(dias)+''' day)
   and M.Estacion=TD1.Estacion
 group by TD1.fecha order by TD1.fecha DESC LIMIT 1'''
    df_Modelo=ejecuteQuery(queryDatos)
    return df_Modelo    


## PROCEDIMIENTOS Y FUNCIONES PARA OPERAR CON PREDICCIONES
## Nos devuelve un dataframe con la predicción del municipio indicado
def getPrediccion(municipio):
    queryDatos="SELECT  fecha, TMax, TMed, TMin, HrMax, HrMed, HrMin, ProbPrecip, VVMed" \
    + ' FROM PrediccionAEMET' \
    +      " WHERE idMunicipio="+municipio+";"
    df_DatosTiempo=ejecuteQuery(queryDatos)
    df_DatosTiempo['fecha']=pd.to_datetime(df_DatosTiempo['fecha'])
    return df_DatosTiempo

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



## Le pasamos un dataframe con el modeloa insertar y nos los inserta.
def insertarModelo(df):
    insertaTabla('Modelo',df)
