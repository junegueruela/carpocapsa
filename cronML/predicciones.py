import pandas as pd
import numpy as np

## Métodos de clasificación
from sklearn.ensemble import RandomForestClassifier
## Balanceado
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from imblearn.under_sampling import RandomUnderSampler
#Estandarización
from sklearn.preprocessing import StandardScaler #, MinMaxScaler,QuantileTransformer, RobustScaler
## Calcular distancias
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cdist

## Para guardar binarios
import joblib

# Ficheros de aplicación
import conexionSGBD as cS
import util as ut
import modelos as mod
import os
from datetime import datetime, timedelta


def entrenarModelo():
    ## Entrenamos el modelo
    df=cS.getTodoModelo()
    # Definimos las columnas
    df['generacionC']=df['generacion']
    df['anyoC']=df['anyo']
    df['idMunicipioC']=df['idMunicipio']
    df['dias_grado_ac_c']=df['dias_grado_ac']
    atributos = [ 'altitud','generacionC', 'anyoC', 'dias_grado_ac_c', \
                 'semana','dia_g', \
                 't_min','t_max','t_med','hr_med','vv_med', \
                 't_min_p','t_max_p','t_med_p','hr_med_p','vv_med_p', \
                             'dias_grado_ac_7', 'rg_md_7', 'hr_md_7', 't_med_7', \
                             'dias_grado_ac_28','t_med_28','rg_md_28','hr_md_28', \
                             'num_vuelos_1','num_vuelos_2','num_vuelos_3','num_vuelos_4','num_vuelos_5','num_vuelos_6']
    ## Vamos a entrenar un Random Forest con todo el dataset
    X_train = np.array(df[atributos])
    Y_train = np.array(df['incidencia'])
    ## Estandarizamos
    scaler = StandardScaler()
    #scaler = QuantileTransformer(output_distribution='normal')
    X_train = scaler.fit_transform(X_train)
    ##X_validation =  scaler.transform(X_validation)
    ## Realizamos un sobremuestreo de la clase minoritaria y un submuestreo de la mayoritaria
    pipeline = Pipeline([
        ('oversample', SMOTE(sampling_strategy=0.6)),
        ('undersample', RandomUnderSampler(sampling_strategy=0.9))
    ])
    X_resampled, y_resampled = pipeline.fit_resample(X_train, Y_train)
    model=RandomForestClassifier(class_weight= None, max_depth=7, min_samples_leaf=4, min_samples_split=2, n_estimators=132)
    model.fit(X_resampled,y_resampled) 
    # Guardamos el modelo entrenado
    joblib.dump(model, "random_forest_model.pkl")
    # Guardamos los datos de escalado
    joblib.dump(scaler, "scaler.pkl")


def realizarPredicciones():
    # Definimos las columnas
    atributos = [ 'altitud','generacionC', 'anyoC', 'dias_grado_ac_c', \
                 'semana','dia_g', \
                 't_min','t_max','t_med','hr_med','vv_med', \
                 't_min_p','t_max_p','t_med_p','hr_med_p','vv_med_p', \
                             'dias_grado_ac_7', 'rg_md_7', 'hr_md_7', 't_med_7', \
                             'dias_grado_ac_28','t_med_28','rg_md_28','hr_md_28', \
                             'num_vuelos_1','num_vuelos_2','num_vuelos_3','num_vuelos_4','num_vuelos_5','num_vuelos_6']
    # Cargamos el modelo
    rf_loaded = joblib.load("random_forest_model.pkl")
    
    # Cargar el escalador
    scaler_loaded = joblib.load("scaler.pkl")
    
    dfProbabilidades=pd.DataFrame(columns=['municipio','fecha','probabilidad','carpo_detectada'])
    dfListaMunicipios=cS.getMunicipiosConVuelos()
    fecha_actual = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    #Aplicamos el modelo de RF y el escalador generado para obtener una predicción diaria de los municipios que disponene de fincas de controls
    for municipio in dfListaMunicipios['municipio']:
        prediccion=mod.calcularModeloMunicipio(municipio,fecha_actual,'N')
        prediccion['generacionC']=prediccion['generacion']
        prediccion['anyoC']=prediccion['anyo']
        prediccion['idMunicipioC']=prediccion['idMunicipio']
        prediccion['dias_grado_ac_c']=prediccion['dias_grado_ac']
        prediccion['detectada']=prediccion['num_vuelos_1']+prediccion['num_vuelos_2']+prediccion['num_vuelos_3']
        prediccion['detectada']=prediccion['detectada'].apply(lambda x: 0 if x <3 else 1)
        predict=scaler_loaded.transform(prediccion[atributos])
        prediction=rf_loaded.predict(predict)
        probabilidad = rf_loaded.predict_proba(predict)[:, 1]
        fecha = str(prediccion['fecha'].max())
        incidencia_detectada=prediccion.loc[(prediccion['idMunicipio'] == municipio) & (prediccion['fecha'] == fecha), 'detectada'].iloc[0]
        dfProbabilidades.loc[len(dfProbabilidades)] = [municipio, fecha , probabilidad[0],incidencia_detectada]
    # Definimos los atributos a escalar para realizar las estimaciones
    atributosE = [ 'dias_grado_ac', \
                 'semana','dia_g', \
                 't_min','t_max','t_med','hr_med','vv_med', \
                 't_min_p','t_max_p','t_med_p','hr_med_p','vv_med_p', \
                             'dias_grado_ac_7', 'rg_md_7', 'hr_md_7', 't_med_7', \
                                 'dias_grado_ac_28','t_med_28','rg_md_28','hr_md_28']
    municipios_con_capturas = [11, 36, 59, 75, 84, 102, 109,125]
    ## Calculamos las medias climáticas para todos los municipios en la última fecha disponible
    estimaciones=pd.DataFrame()
    dfListaSinvuelos=cS.getMunicipios()
    for municipio in dfListaSinvuelos['idMunicipio']:
        estimacion=mod.calcularModeloMunicipio(municipio,fecha_actual,'S')
        estimaciones=pd.concat([estimaciones, estimacion[['idMunicipio', 'fecha','altitud','dias_grado_ac', 'semana','dia_g', \
                                                         't_min','t_max','t_med','hr_med','vv_med', \
                                                         't_min_p','t_max_p','t_med_p','hr_med_p','vv_med_p', \
                                                         'dias_grado_ac_7', 'rg_md_7', 'hr_md_7', 't_med_7', \
                                                         'dias_grado_ac_28','t_med_28','rg_md_28','hr_md_28']][estimacion['fecha']==fecha_actual]], ignore_index=True)
    ## Estandarizamos
    scalerE = StandardScaler()
    estimaciones[atributosE] = scalerE.fit_transform(estimaciones[atributosE])
    
    # Separamos las métricas para los atributos que van a servir de referencia y los que no.
    estimacionesmunicipios = estimaciones[estimaciones['idMunicipio'].isin(municipios_con_capturas)]
    estimacionesotros = estimaciones[~estimaciones['idMunicipio'].isin(municipios_con_capturas)]
    distancias = cdist(estimacionesotros[atributosE], estimacionesmunicipios[atributosE], metric='euclidean')
    # Cogemos los dos más cercanos
    k = 2
    
    # Inicializar una lista para almacenar las probabilidades estimadas
    probabilidades_estimadas = []
    
    # Iterar sobre cada municipio sin probabilidad conocida
    for i, dist in enumerate(distancias):
        # Obtener los índices de los k municipios más cercanos
        indices_vecinos = np.argsort(dist)[:k]
        # Obtener las distancias correspondientes
        distancias_vecinos = dist[indices_vecinos]
        # Obtener las probabilidades de los municipios más cercanos
        # Obtener los idMunicipio de los vecinos más cercanos
        id_vecinos = estimacionesmunicipios.iloc[indices_vecinos]['idMunicipio'].values
        
        # Obtener las probabilidades correspondientes de dfProbabilidades utilizando idMunicipio
        probabilidades_vecinos = dfProbabilidades.set_index('municipio').loc[id_vecinos, 'probabilidad'].values
        
        # Calcular los pesos como el inverso de la distancia
        pesos = 1 / distancias_vecinos
        # Calcular la probabilidad estimada como la media ponderada
        probabilidad_estimada = np.average(probabilidades_vecinos, weights=pesos)
        # Obtener los idMunicipio, distancias y probabilidades de los vecinos más cercanos
        #vecinos_info = [(estimacionesmunicipios.iloc[idx]['idMunicipio'], dist[idx], dfProbabilidades.iloc[idx]['probabilidad']) for idx in indices_vecinos]
        
        # Almacenar el resultado con el idMunicipio y la fecha correspondiente
        probabilidades_estimadas.append({
            'idMunicipio': estimacionesotros.iloc[i]['idMunicipio'],
            'fecha': estimacionesotros.iloc[i]['fecha'],
            'probabilidad': probabilidad_estimada
        })
    
    #Convertir la lista de resultados en un DataFrame
    df_probabilidades_estimadas = pd.DataFrame(probabilidades_estimadas)
    
    ## Juntamos todas las estimaciones
    estimacionesotros = estimacionesotros.merge(df_probabilidades_estimadas, on=['idMunicipio', 'fecha'])
    estimacionesotros['municipio']=estimacionesotros['idMunicipio']
    estimacionesotros=estimacionesotros[['municipio','fecha','probabilidad']]
    probabilidades= pd.concat([dfProbabilidades, estimacionesotros])
    probabilidades = probabilidades.rename(columns={'municipio': 'idMunicipio'})
    probabilidades['prediccion']=probabilidades['probabilidad'].apply(lambda x: 0 if x < 0.5 else 1)
    probabilidades.sort_values(by='probabilidad').head(40)
    # Convierte todo a datetime, ignorando errores
    probabilidades["fecha"] = pd.to_datetime(probabilidades["fecha"], errors='coerce')
    
    # Ahora suma un día
    probabilidades["fecha"] = probabilidades["fecha"] + timedelta(days=1)
    
    fecha_actual = (datetime.now()).strftime('%Y-%m-%d')
    ## Guardamos las estimaciones
    print(fecha_actual)
    cS.borraPrediccionPlaga(fecha_actual)
    cS.insertarPrediccion(probabilidades)