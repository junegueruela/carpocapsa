import os
# Forzar método seguro de multiprocessing en Docker
os.environ["JOBLIB_START_METHOD"] = "spawn"

import predicciones as pr
import conexionSGBD as cS
import util as ut

pr.entrenarModelo()