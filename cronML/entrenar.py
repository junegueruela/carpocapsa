import predicciones as pr
import conexionSGBD as cS
import util as ut
import os

from joblib import Parallel, delayed
os.environ["JOBLIB_NJOBS"] = "1"

#os.chdir('D:\\VS Proyectos\\Control carpocapsa')
pr.entrenarModelo()