# coding: UTF-8
# Para ejecutar en modo debug, desde la consola: flask --app hello --debug run
from ast import Str
import email
from email.message import EmailMessage
from logging.config import dictConfigClass
from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import user_agents
from werkzeug.security import generate_password_hash, check_password_hash
import forms as f
import pandas as pd
import obtenerDatos as oD
import conexionSGBD as cS
from datetime import datetime,timedelta
import util as ut

app = Flask(__name__)
## Configuramos la clave secreta, obligatoria para trabajar con wtf forms.
app.config['SECRET_KEY']='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqdW5lZ3VlcnVlbGFAZ21haWwuY29tIiwianRpIjoiYjMzZmVkYTYtODEzOS00ZDdjLWEyOTktN2Q0M2NiYzMwZDA5IiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3MTM1NDYzODEsInVzZXJJZCI6ImIzM2ZlZGE2LTgxMzktNGQ3Yy1hMjk5LTdkNDNjYmMzMGQwOSIsInJvbGUiOiIifQ.hZT8YCEAuhb8tZmrTdBf7KFi6k3U5cV_ln-AdXiBFxk'

# Configuración de Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Modelo de usuario
# Clase Usuario adaptada para trabajar con los datos de la función obtenerUsuario
class Usuario(UserMixin):
    def __init__(self, id, usuario, clave,nombre,email,tecnico):
        self.id= id
        self.usuario = usuario
        self.clave = clave 
        self.nombre=nombre
        self.email=email
        self.tecnico=tecnico

    def get_id(self):
        return self.id

# Cargar usuario por id
@login_manager.user_loader
def load_user(user_id):
        # Usa la funciónn getUsuarioPorID para obtener los datos del usuario por ID
    df=cS.getUsuarioPorID(user_id)
    
    if not df.empty:
        # Si el DataFrame no está vacío, creamos un objeto Usuario
        user_data = df.iloc[0]  # Tomamos la primera fila
        user = Usuario(int(user_data['id']), user_data['usuario'], user_data['clave'],user_data['nombre'],user_data['email'],user_data['tecnico'])
        return user
    return none

#Filtros personalizados para flash y jinja
@app.add_template_filter
def today(date):
    return date.strftime('%Y-%m-%d')
@app.add_template_global ## Me añade la función para todas mis plantillas del proyecto

@app.route("/login", methods=['GET','POST'])
def login():
    user_agent = request.headers.get('User-Agent')
    ua = user_agents.parse(user_agent)
    form=f.loginForm()
    if form.validate_on_submit():
        usuario=form.username.data
        clave=form.password.data
        try:
            bdClave = cS.getClave(usuario)
        except Exception as e:
                error='Ocurrió un error general. Inténtelo más tarde'
                return render_template("/auth/login.html",form=form,error=error)
        ## Chequeo que la clave encriptada sea igual que en bd
        if check_password_hash(bdClave, clave):
            # Si la clave coindice.
            df=cS.getUsuarioPorLogin(usuario)
            user_data = df.iloc[0]  # Tomamos la primera fila
            user = Usuario(int(user_data['id']), user_data['usuario'], user_data['clave'],user_data['nombre'],user_data['email'],user_data['tecnico'])
            ## Si no es técnico de la DOP no puede acceder
            if user.tecnico == 'N':
                error='Usuario no autorizado'
                return render_template("/auth/login.html",form=form,error=error)
            else:
                login_user(user)
            return redirect(url_for('index'))
        else:
            error='Usuario o clave incorrectos'
            return render_template("/auth/login.html",form=form,error=error)
    return render_template("/auth/login.html",form=form)

# Me cambia la clave del usuario
@app.route("/cambiarClave", methods=['GET','POST'])
@login_required
def cambiarClave():
    form=f.cambiarClaveForm()
    mensaje=" "
    if form.validate_on_submit():
        clave=form.oldPassword.data
        nuevaClave=form.newPassword.data
        confirmaClave=form.confirmPassword.data
        bdClave = cS.getClave(current_user.usuario)
        if check_password_hash(bdClave, clave):
            if nuevaClave==confirmaClave:
                claveEncriptada=generate_password_hash(nuevaClave)
                cS.actualizaClave(current_user.id, claveEncriptada)
                mensaje="Clave actualizada correctamente"
            else:
                mensaje="La nueva clave y la confirmaci�n no coinciden"
        else:
            mensaje='Clave incorrecta int�ntelo de nuevo'
    return render_template("/auth/cambiarClave.html",form=form, mensaje=mensaje)

@app.route("/", methods=['GET','POST'])
@login_required
def index():
    date=datetime.now()
    estaciones=cS.getUltimosDatosEstaciones()
    estaciones=estaciones.rename(columns={"fecha":"Fecha","altitud":"Altitud (m)"})
    municipios=cS.getMunicipiosEstacion()
    municipios=municipios.drop("idMunicipio",axis=1)
    municipios=municipios.rename(columns={"altitudMunicipio":"Altitud (m)","difAltitud":"Diferencia de altitud (m)","distancia":"Distancia (km)","Estacion":"Estación de referencia"})
    leyenda=ut.leyendaTiempoCorta()
    return render_template('index.html',estaciones=estaciones.to_html(index=False, classes='tablas'),municipios=municipios.to_html(index=False, classes='tablas'), \
                           leyenda=leyenda.to_html(index=False, classes='tablas'))
   #en lugar de crear una función y pasarla como plantilla, la paso como parámetro

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/estacion", methods=['GET','POST'])
@login_required
def estacion():
    eForm=f.datosEstacionForm()
    bForm=f.borrarLecturasEstacionForm()
    estaciones=cS.getEstaciones()
    listaEstaciones= [(row['estacion'], row['municipio']) for index, row in estaciones.iterrows()]
    eForm.estacion.choices=listaEstaciones
    ## Si hemos seleccionado el botón submit vemos las últimas n temperaturas
    if eForm.validate_on_submit() and 'submit' in request.form:
        estacion = eForm.estacion.data
        nDias = eForm.nDias.data
        df=cS.getDatosTiempoDias(estacion, nDias)
        df=df.drop("Estacion",axis=1)
        df=df.rename(columns={"fecha":"Fecha"})
        leyenda=ut.leyendaTiempo()
        return render_template("/estaciones/estacion.html",form=eForm,formB=bForm, datos=df.to_html(index=False, classes='tablas'), leyenda=leyenda.to_html(index=False, classes='tablas'))
   ## Si hemos seleccionado el botón borrar, borramos.
    if bForm.validate_on_submit() and 'borrar' in request.form:
        estacion = request.form.get('estacion')
        fechaDesde=bForm.fechaDesde.data
        fechaHasta=bForm.fechaHasta.data
        cS.borraDatosTemperatura(int(estacion), fechaDesde, fechaHasta)
        nDias = eForm.nDias.data
        df=cS.getDatosTiempoDias(estacion, nDias)
        df=df.drop("Estacion",axis=1)
        df=df.rename(columns={"fecha":"Fecha"})
        leyenda=ut.leyendaTiempo()
        return render_template("/estaciones/estacion.html",form=eForm,formB=bForm, datos=df.to_html(index=False, classes='tablas'), leyenda=leyenda.to_html(index=False, classes='tablas'))
   ## Si hemos seleccionado el botón cargar, actualizamos.
    if bForm.validate_on_submit() and 'cargar' in request.form:
        estacion = request.form.get('estacion')
        fechaDesde=bForm.fechaDesde.data
        fechaHasta=bForm.fechaHasta.data
        dfTemperaturas=oD.getDatosClimaticosCAR(fechaDesde.strftime("%Y-%m-%d"), fechaHasta.strftime("%Y-%m-%d"), estacion)
        ## Si la consulta de la CAR devuelve datos, borro los que hay en ese periodo para que no los duplique.
        if len(dfTemperaturas)>0:
                    cS.borraDatosTemperatura(int(estacion), fechaDesde, fechaHasta)
        cS.insertarDatosTiempo(dfTemperaturas)
        nDias = eForm.nDias.data
        df=cS.getDatosTiempoDias(estacion, nDias)
        df=df.drop("Estacion",axis=1)
        df=df.rename(columns={"fecha":"Fecha"})
        leyenda=ut.leyendaTiempo()
        return render_template("/estaciones/estacion.html",form=eForm,formB=bForm, datos=df.to_html(index=False, classes='tablas'), leyenda=leyenda.to_html(index=False, classes='tablas'))
    return render_template("/estaciones/estacion.html",form=eForm)

@app.route("/vuelo", methods=['GET','POST'])
@login_required
def vuelo():
    tForm=f.terminoForm()
    aForm=f.addVueloTerminoForm()
    terminos=cS.getTerminos()
    listaTerminos= [(row['idTermino'], row['Termino']) for index, row in terminos.iterrows()]
    tForm.termino.choices=listaTerminos
    if 'borrar' in request.form:
           termino = tForm.termino.data
           idvuelo=request.form.get("idVuelo")
           # Asegñurate de mantener el valor del SelectField
           tForm.termino.data = termino
           print(f"Restaurando el valor seleccionado después de borrar: {tForm.termino.data}")  # Prueba de valor
           nTermino=str(cS.getTermino(idvuelo))
           tForm.termino.data = nTermino
           cS.borraVuelo(idvuelo)
           df=cS.getUltimosVuelos(nTermino)
           df=df.rename(columns={"fecha":"Fecha"})
           df=df.rename(columns={"vuelos":"Capturas"})
           df['Accion']=df.apply(f.agregar_boton_borrar,axis=1)
           return render_template("/vuelos/vuelo.html",formT=tForm, formA=aForm, datos=df.to_html(index=False, escape=False, classes="tablas"))
    ## Si validamos el formulario de tForm mostramos las últimas n capturas o por días.
    if tForm.validate_on_submit() and ('submit' in request.form or 'submitF' in request.form):
           termino = tForm.termino.data
           nCapturas = tForm.nCapturas.data
           fechaMin = tForm.fechaMin.data
           fechaMax = tForm.fechaMax.data
           if ('submit' in request.form):
               df=cS.getUltimosVuelos(termino, nCapturas)
           else:
               df=cS.getDatosVuelos(termino,fechaMin.strftime("%Y-%m-%d"),fechaMax.strftime("%Y-%m-%d"))
           df=df.rename(columns={"fecha":"Fecha"})
           df=df.rename(columns={"vuelos":"Capturas"})
           df['Accion']=df.apply(f.agregar_boton_borrar,axis=1)
           return render_template("/vuelos/vuelo.html",formT=tForm, formA=aForm, datos=df.to_html(index=False, escape=False, classes="tablas"))
    ## Si damos al de aForm añadimos la captura y mostramos las últimas 20 
    if aForm.validate_on_submit() and 'submit2' in request.form:
           termino = request.form.get('termino')  # Obtener el valor de termino
           fechaCaptura=aForm.fechaCaptura.data
           numVuelos=aForm.numVuelos.data
           strFechaCaptura=fechaCaptura.strftime("%Y-%m-%d")
           datos={'fecha':[strFechaCaptura], 'idTermino':[int(termino)],'valor':[numVuelos]}
           df=pd.DataFrame(datos)
           cS.insertarVuelo(df)
           df=cS.getUltimosVuelos(termino)
           df=df.rename(columns={"fecha":"Fecha"}) 
           df=df.rename(columns={"vuelos":"Capturas"}) 
           df['Accion']=df.apply(f.agregar_boton_borrar,axis=1)
           return render_template("/vuelos/vuelo.html",formT=tForm, formA=aForm, datos=df.to_html(index=False, escape=False, classes="tablas"))
           #return render_template("resultado2.html",mensaje=df.to_html(index=False, classes="tablas"))
    return render_template("/vuelos/vuelo.html",formT=tForm)

@app.route("/municipio", methods=['GET','POST'])
@login_required
def municipio():
    mForm = f.municipioForm()
    acForm = f.actualizarMunicipioForm()
    municipios = cS.getMunicipios()
    listaMunicipios = [(row['idMunicipio'], row['Municipio']) for index, row in municipios.iterrows()]
    mForm.municipio.choices = listaMunicipios

    if mForm.validate_on_submit() and 'submit' in request.form:
        idMunicipio = mForm.municipio.data
        dfM = cS.getMunicipiosEstacion()
        dfM = dfM[dfM["idMunicipio"] == int(idMunicipio)]
        strIdEstacion = dfM["idEstacion"].astype("string").iloc[0]
        dfM = dfM[["Estacion", "distancia", "difAltitud"]]
        dic = dfM.iloc[0].to_dict()

        dp = cS.getPrediccion(idMunicipio)
        dp = dp.sort_values(by=["fecha"])
        dp = dp.rename(columns={"fecha": "Fecha"})
        leyenda = ut.leyendaTiempo()
        return render_template("/municipios/municipio.html", form=mForm, formB=acForm,
                               leyenda=leyenda.to_html(index=False, classes='tablas'),
                               prediccion=dp.to_html(index=False, escape=False, classes="tablas"), dic=dic)

    elif acForm.validate_on_submit() and 'actualizar' in request.form:
        idMunicipio = request.form.get('municipio')

        dp = oD.actualizarPrediccion(idMunicipio)

        dfM = cS.getMunicipiosEstacion()
        dfM = dfM[dfM["idMunicipio"] == int(idMunicipio)]
        strIdEstacion = dfM["idEstacion"].astype("string").iloc[0]
        dfM = dfM[["Estacion", "distancia", "difAltitud"]]
        dic = dfM.iloc[0].to_dict()

        dp = cS.getPrediccion(idMunicipio)
        dp = dp.sort_values(by=["fecha"])
        dp = dp.rename(columns={"fecha": "Fecha"})
        leyenda = ut.leyendaTiempo()

        return render_template("/municipios/municipio.html", form=mForm, formB=acForm,
                               leyenda=leyenda.to_html(index=False, classes='tablas'),
                               prediccion=dp.to_html(index=False, escape=False, classes="tablas"), dic=dic)

    return render_template("/municipios/municipio.html", form=mForm, formB=acForm)

# Ruta para cerrar sesión
@app.route('/panel')
@login_required
def panel():
    return render_template('/panel/panel.html')

if __name__ == "__main__":
    # Para ejecutar en docker
    app.run(host="0.0.0.0",port=5000)
    ##app_run()
