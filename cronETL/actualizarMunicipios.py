import pandas as pd
import obtenerDatos as oD
import conexionSGBD as cS
import util as ut
import os
#os.chdir('D:\\VS Proyectos\\Control carpocapsa')
## Tengo que dividir en dos la captura de datos de AEMET porque no me deja capturar más de 25 municipios
dfMunicipios=cS.getMunicipios()
for municipio in dfMunicipios['idMunicipio']:
    if (int(municipio)<100):
            oD.actualizarPrediccion(municipio)