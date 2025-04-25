#Modulo obtenerDatos
#Nos permite comunicarnos con la API de la CAR para recuperar la informacion de su red de estaciones clim�ticas

import pandas as pd
import numpy as np
import json
import requests
import http.client
import datetime
import conexionSGBD as cS
import util as ut
__apiKey__="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqdW5lZ3VlcnVlbGFAZ21haWwuY29tIiwianRpIjoiYjMzZmVkYTYtODEzOS00ZDdjLWEyOTktN2Q0M2NiYzMwZDA5IiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3MTM1NDYzODEsInVzZXJJZCI6ImIzM2ZlZGE2LTgxMzktNGQ3Yy1hMjk5LTdkNDNjYmMzMGQwOSIsInJvbGUiOiIifQ.hZT8YCEAuhb8tZmrTdBf7KFi6k3U5cV_ln-AdXiBFxk"


## Obtenemos la predicci�n semanal de la AEMET para un municipio con su codigo.
def getPrediccionAemet(municipio):
    conn = http.client.HTTPSConnection("opendata.aemet.es")

    headers = {
        'cache-control': "no-cache"
        }
    #https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/16125 -> Es la de Rincon 
    ##Obtenemos la predicci�n clim�tica por municipio, le añadimos el prefijo 26
    conn.request("GET", "/opendata/api/prediccion/especifica/municipio/diaria/26"+municipio.zfill(3)+"/?api_key="+__apiKey__, headers=headers)
    res = conn.getresponse()
    data = res.read()
    #print(data.decode("latin-1"))
    json_response=json.loads(data.decode("latin-1"))
    #json_response=json.loads(data)
    URL=json_response['datos']
    ## Llamanos a la URL que est� en la clave datos y nos devuelve un json con las predicciones
    response_t = requests.get(URL)
    data=response_t.json()
    pPrediccion=data[0]['prediccion']['dia']
    ## Obtenemos un dataframe con la temperatura m�xima y m�nima
    temperaturas = []
    for dia in pPrediccion:
        fecha = dia['fecha']
        maxima = dia['temperatura']['maxima']
        minima = dia['temperatura']['minima']
        ## La temperatura media, guarda datos cada x horas los primeros dos d�as.
        ## As� que hago una media de esos valores.
        ## Si no existen, hago la media entre m�xima y m�nima
        tms=[tm['value'] for tm  in dia['temperatura']['dato']]
        media=sum(tms)/len(tms) if tms else (maxima+minima)/2
        hrMaxima=dia['humedadRelativa']['maxima']
        hrMinima=dia['humedadRelativa']['minima']
        ## Lo mismo me pasa con las presiones
        hrs=[hr['value'] for hr  in dia['humedadRelativa']['dato']]
        hrMedia=sum(hrs)/len(hrs) if hrs else (hrMaxima+hrMinima)/2
        ## Calculo las precicipationes, similar al viento.
        pacs= [pac['value'] for pac in dia['probPrecipitacion']]
        pPr = sum(pacs)/len(pacs) if pacs else 0
        ## Para el viento, hay varios valores, por lo que obtengo la media
        velocidades = [viento['velocidad'] for viento in dia['viento']]
        vViento= sum(velocidades) / len(velocidades) if velocidades else None
        temperaturas.append({"fecha": fecha, "Tmax": maxima, 'TMed': media, "Tmin": minima,'HrMax':hrMaxima,'HrMed':hrMedia, 'HrMin':hrMinima, 'ProbPrecip':pPr, 'VVMed':vViento})
    df = pd.DataFrame(temperaturas)
    df['VVMed']=df['VVMed'].round(2)
    df['ProbPrecip']=df['ProbPrecip'].round(2)
    return df





def getDatosClimaticosCAR(fIni, fFin, estacion):
    ''' 
    Obtenemos los datos relativos a
        Temperatura T: M�xima, media y m�nima
        Temperatura del suelo TS: M�xima, media y m�nima.
        Humedad relativa Hr: M�xima, media y m�nima
        Precipitaci�n acumulada PAc
        �ndice de radiaci�n acumulada RgAc
        Velocidad del viento en km/h VV: M�xima y media.
    Args: 
         fIni: fecha de incio de la consulta
         fFin: Fecha fin de la consulta
         estacion: C�digo de estaci�n agroclim�tica que queremos consultar
    Returns:
        Un dataframe con todos los datos
    '''
    URL="https://ias1.larioja.org/apiSiar/servicios/v2/datos-climaticos/"+estacion+ "/D?fecha_inicio="+fIni+"&fecha_fin="+fFin \
    +"&dato_valido=True&parametro=TS&parametro=T"
    ## Creo un dataFrame vac�o por si falla
    dfT = pd.DataFrame(columns=['fecha','TMax', 'TMed','Tmin','TsMax', 'TsMed','Tsmin'])
    try:
        response = requests.get(URL,timeout=90)
        j_data=response.json()
    ## De la respuesta me quedon con los datos.
        df=pd.DataFrame(j_data['datos'])
        ## Substituyo lo - por nulos
        df = df.replace('-','')
        ## A veces da varias medidas para un d�a de un par�metro, as� que selecciono la media
        df['valor']=df['valor'].astype('float')
        df=df.groupby(['parametro','fecha','funcion_agregacion'])['valor'].mean().reset_index()
        df['valor']=df['valor'].round(2)
        ## Recupero las temperaturas del aire y las agrupo en un dataframe
        dfTMax=df[(df['parametro']=='T')&(df['funcion_agregacion']=='Max')][['fecha','valor']].rename(columns={'valor':'TMax'})
        dfTMed=df[(df['parametro']=='T')&(df['funcion_agregacion']=='Med')][['fecha','valor']].rename(columns={'valor':'TMed'})
        dfTMin=df[(df['parametro']=='T')&(df['funcion_agregacion']=='Min')][['fecha','valor']].rename(columns={'valor':'TMin'})
        dfTe=pd.merge(dfTMax,dfTMed, on='fecha',how='left')
        dfTe=pd.merge(dfTe,dfTMin, on='fecha',how='left')
        ## Recupero las temperaturas del suelo y las agrupo en un dataframe
        ## Como las temperatus del suelo tienen varias medidas, hago una �nica agrupaci�n por fecha primero
        dfTsMax=df[(df['parametro']=='TS')&(df['funcion_agregacion']=='Max')][['fecha','valor']].rename(columns={'valor':'TsMax'})
        dfTsMed=df[(df['parametro']=='TS')&(df['funcion_agregacion']=='Med')][['fecha','valor']].rename(columns={'valor':'TsMed'})
        dfTsMin=df[(df['parametro']=='TS')&(df['funcion_agregacion']=='Min')][['fecha','valor']].rename(columns={'valor':'TsMin'})
        dfTs=pd.merge(dfTsMax,dfTsMed, on='fecha',how='left')
        dfTs=pd.merge(dfTs,dfTsMin, on='fecha',how='left')
        ## hago un merge de la Temperatura y la Temperatura m�xima
        dfT=pd.merge(dfTe,dfTs,on='fecha',how='left')
    except requests.exceptions.Timeout:
        print ("Time out al consultar las temperaturas")
    except requests.exceptions.InvalidJSONError:
         print ("Error al consultar las temperaturas")
    except Exception as e:
        print ("No ha devuelto datos la consulta")
    URL="https://ias1.larioja.org/apiSiar/servicios/v2/datos-climaticos/"+estacion+ "/D?fecha_inicio="+fIni+"&fecha_fin="+fFin \
    +"&dato_valido=True&parametro=Hr"
    ## Creo un dataFrame vac�o por si falla
    dfHr = pd.DataFrame(columns=['fecha','HrMax', 'HrMed','Hrmin'])
    try:
        response = requests.get(URL,timeout=90)
        j_data=response.json()
        ## De la respuesta me quedon con los datos.
        df=pd.DataFrame(j_data['datos'])
        ## Substituyo lo - por nulos
        df = df.replace('-','')
        ## A veces da varias medidas para un d�a de un par�metro, as� que selecciono la media
        df['valor']=df['valor'].astype('float')
        df=df.groupby(['parametro','fecha','funcion_agregacion'])['valor'].mean().reset_index()
        df['valor']=df['valor'].round(2)
        ## Recupero las humedades relativas y las agrupo en un dataframe
        dfHrMax=df[(df['parametro']=='Hr')&(df['funcion_agregacion']=='Max')][['fecha','valor']].rename(columns={'valor':'HrMax'})
        dfHrMed=df[(df['parametro']=='Hr')&(df['funcion_agregacion']=='Med')][['fecha','valor']].rename(columns={'valor':'HrMed'})
        dfHrMin=df[(df['parametro']=='Hr')&(df['funcion_agregacion']=='Min')][['fecha','valor']].rename(columns={'valor':'HrMin'})
        dfHr=pd.merge(dfHrMax,dfHrMed, on='fecha',how='outer')
        dfHr=pd.merge(dfHr,dfHrMin, on='fecha',how='left')
    except requests.exceptions.Timeout:
        print ("Time out al consultar la humedad relativa")
    except requests.exceptions.InvalidJSONError:
         print ("Error al consultar la humedad relativa")
    except Exception as e:
        print ("No ha devuelto datos la consulta")
    ## Hago la tercera petici�n
    URL="https://ias1.larioja.org/apiSiar/servicios/v2/datos-climaticos/"+estacion+ "/D?fecha_inicio="+fIni+"&fecha_fin="+fFin \
    +"&dato_valido=True&parametro=P&parametro=Rg"
    ## Creo un dataFrame vac�o por si falla
    dfR = pd.DataFrame(columns=['fecha','Pac', 'RgAc'])
    try:
        response = requests.get(URL,timeout=90)
        j_data=response.json()
        ## De la respuesta me quedon con los datos.
        df=pd.DataFrame(j_data['datos'])
        ## Substituyo lo - por nulos
        df = df.replace('-','')
        ## A veces da varias medidas para un d�a de un par�metro, as� que selecciono la media
        df['valor']=df['valor'].astype('float')
        df=df.groupby(['parametro','fecha','funcion_agregacion'])['valor'].mean().reset_index()
        df['valor']=df['valor'].round(2)
        ## Obtengo el dataframe para la precipitaci�n acumulada
        dfPAc=df[(df['parametro']=='P')][['fecha','valor']].rename(columns={'valor':'PAc'})
        ## Recupero los �ndice de radiaci�n acumulada
        dfRgAc=df[(df['parametro']=='Rg')&(df['funcion_agregacion']=='Ac')][['fecha','valor']].rename(columns={'valor':'RgAc'})
        dfR=pd.merge(dfPAc,dfRgAc,on='fecha',how='left') 
    except requests.exceptions.Timeout:
        print ("Time out al consultar las precipitaciones")
    except requests.exceptions.InvalidJSONError:
         print ("Error al consultar las precipitaciones")
    except Exception as e:
        print ("No ha devuelto datos la consulta")
    ## Hago la cuarta petici�n
    URL="https://ias1.larioja.org/apiSiar/servicios/v2/datos-climaticos/"+estacion+ "/D?fecha_inicio="+fIni+"&fecha_fin="+fFin \
    +"&dato_valido=True&parametro=VV"
    ## Creo un dataFrame vac�o por si falla
    dfVV = pd.DataFrame(columns=['fecha','VVMax', 'VVMed'])
    try:
        response = requests.get(URL,timeout=90)
        j_data=response.json()
        ## De la respuesta me quedon con los datos.
        df=pd.DataFrame(j_data['datos'])
        ## Substituyo lo - por nulos
        df = df.replace('-','')
        ## A veces da varias medidas para un d�a de un par�metro, as� que selecciono la media
        df['valor']=df['valor'].astype('float')
        ## Como es el viento, lo convierto en km/h
        df['valor']=df['valor']*3.6
        df=df.groupby(['parametro','fecha','funcion_agregacion'])['valor'].mean().reset_index()
        df['valor']=df['valor'].round(2)
        ## Recupero la velocidad del viento m�ximo y media y las agrupo en un dataframe
        dfVVMax=df[(df['parametro']=='VV')&(df['funcion_agregacion']=='Max')][['fecha','valor']].rename(columns={'valor':'VVMax'})
        dfVVMed=df[(df['parametro']=='VV')&(df['funcion_agregacion']=='Med')][['fecha','valor']].rename(columns={'valor':'VVMed'})
        dfVV=pd.merge(dfVVMax,dfVVMed,on='fecha',how='left')
    except requests.exceptions.Timeout:
        print ("Time out al consultar la velocidad del viento")
    except requests.exceptions.InvalidJSONError:
        print ("Error al consultar la velocidad del viento")
    except Exception as e:
        print ("No ha devuelto datos la consulta")
    ## Los junto todos
    dfT=pd.merge(dfT,dfHr,on='fecha',how='left')
    dfT=pd.merge(dfT,dfR,on='fecha',how='left')
    dfT=pd.merge(dfT,dfVV,on='fecha',how='left')    
    ##A�ado la columna estaci�n y la pongo al principio
    dfT['estacion']=estacion
    dfT.replace('',np.nan)
    dfT = dfT[['estacion'] + [col for col in dfT.columns if col != 'estacion']]
    return dfT

    




## Dada una estaci�n meteorol�gica, obtengo los datos clim�ticos desde la �ltima medici�n
## Y los guardo en base de datos.
def actualizarEstacion(estacion):
    strEstacion=str(estacion)
    fechaInicio=cS.getFechaMaxima(strEstacion) + datetime.timedelta(days=1)
    fechaFin=(datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    dfSalida=getDatosClimaticosCAR(str(fechaInicio), str(fechaFin),strEstacion)
    try:
        cS.insertarDatosTiempo(dfSalida)
        print ("Estacion "+strEstacion+" actualizada correctamente")
    except Exception as e:
       print('Error al insertar datos de la estaci�n ' + strEstacion + ' para el rango de fecha de '+ str(fechaInicio) + ' a ' + str(fechaFin))




## Actualizo los datos que faltan de todas las estaciones
def actualizarTodasEstaciones():
    dfEstaciones=cS.getEstaciones()
    for estacion in dfEstaciones['estacion']:
        actualizarEstacion(estacion)


## Dada un municipio, obtengo la predicci�n
## Y los guardo en base de datos.
def actualizarPrediccion(municipio):
    strMunicipio=str(municipio)
    dfSalida=getPrediccionAemet(strMunicipio)
    dfSalida.insert(0,'idMunicipio',municipio)
    dfSalida['fecha']=dfSalida['fecha'].apply(lambda x: ut.convertirString(x,'AEMET'))
    try:
        cS.borraPrediccion(municipio)
        cS.insertarPrediccion(dfSalida)
        print('Predicci�n de '+strMunicipio+' actualizada correctamente')
       
    except Exception as e:
       print('Error al insertar predicci�n del municipio '+strMunicipio)

## Actualizo la predicci�n de todos los Municipios
def actualizarPrediccionMunicipios():
    dfMunicipios=cS.getMunicipios()
    for municipio in dfMunicipios['idMunicipio']:
        actualizarPrediccion(municipio)
# In[ ]:


def calcularModelo(dias):
    dfMunicipios=cS.getMunicipiosConVuelos()
    for municipio in dfMunicipios['municipio']:
        dfModelo=cS.getModelo(str(municipio),dias)
        cS.insertarModelo(dfModelo)

