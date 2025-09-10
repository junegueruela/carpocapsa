import os

# Forzar método seguro en Python 3.12 / Docker
os.environ["JOBLIB_START_METHOD"] = "spawn"

import predicciones as pr
import conexionSGBD as cS
import util as ut
#os.chdir('D:\\VS Proyectos\\Control carpocapsa')
pr.realizarPredicciones()