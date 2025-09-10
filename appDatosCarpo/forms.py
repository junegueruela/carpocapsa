# coding: utf-8
from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SelectField, StringField,PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import datetime


#Formulario para login de  usuario
class loginForm(FlaskForm):
    username=StringField("Nombre de usuario: ", validators=[DataRequired(),Length(min=4, max=25)])
    password=PasswordField("contraseña: ", validators=[DataRequired(),Length(min=6, max=40)])
    submit=SubmitField("Aceptar")

#Formulario para login de  usuario
class cambiarClaveForm(FlaskForm):
    oldPassword=PasswordField("Contraseña actual: ", validators=[DataRequired(),Length(min=6, max=40)])
    newPassword=PasswordField("Contrasea nueva: ", validators=[DataRequired(),Length(min=6, max=40)])
    confirmPassword=PasswordField("Repita contraseña: ", validators=[DataRequired(),Length(min=6, max=40)])
    submit=SubmitField("Aceptar")


## Formularios para estaciones de datos #####

## Formulario para obtener los datos de una estaci�n desde una fecha.
class datosEstacionForm(FlaskForm):
    estacion=SelectField("Seleccione una estación: ", choices=[])
    nDias=IntegerField("Consultar los últimos días: ", default=30)
    submit=SubmitField("Consultar por días")

class borrarLecturasEstacionForm(FlaskForm):
    fechaDesde=DateField("Borrar desde: ", default=datetime.today())
    fechaHasta=DateField("Hasta: ", default=datetime.today())
    borrar=SubmitField("Borrar datos")
    cargar=SubmitField("Refrescar datos")

## Formularios para términos municipales ##

## Formulario para añadir el campo termino en ambos
class terminoForm(FlaskForm):
    termino=SelectField("Seleccione una finca: ", choices=[], validators=[DataRequired()])
    nCapturas=IntegerField("Número de entradas a consultar: ", default=20)
    submit=SubmitField("Consultar")
    fechaMin=DateField("Desde: ", default=lambda:datetime.today())
    fechaMax=DateField("Hasta: ", default=lambda:datetime.today())
    submitF=SubmitField("Consultar por fechas")
## Formulario para añadir  los vuelos en un término
class addVueloTerminoForm(FlaskForm):
    fechaCaptura=DateField("Fecha de captura: ",default=lambda:datetime.today())
    numVuelos=IntegerField("Número de capturas: ", default=0)
    submit2=SubmitField("Añadir")

# Función para agregar un botón de borrado en cada fila
def agregar_boton_borrar(row):
    return f'''<form action="/vuelo" method="POST" style="display:inline;"> <input type="hidden" name="idVuelo" value="{row['idVuelo']}"/> <button type="submit" name="borrar" class="btn btn-danger">Borrar</button></form>'''

## Formularios para Municipios ##

### Formularios para visualizar municipios de la DOP
class municipioForm(FlaskForm):
    municipio=SelectField("Seleccione un munipio: ", choices=[], validators=[DataRequired()])
    submit=SubmitField("Consultar")
class actualizarMunicipioForm(FlaskForm):
    actualizar = SubmitField("Actualizar predicciones")