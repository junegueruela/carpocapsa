Predicción de la Cydia Pomonella en perales de la DOP Peras de Rincón de Soto.
Este respositorio contiene todo el software necesario para el despliegue en dockers del sistema de predicción de plagas desarrollado para el TFM homónimo.
Para desplegar el sistema es necesario ejecutar el comando create.sh en entornos Linux o create.ps1 para Windows, cuyos pasos son:
- Creación dos volúmenes persistentes: mysql_data para los datos de MySQL y backup para las copias de seguridad.
- Crea una red miRed para que los contenedores se comuniquen entre sí.
- Lanza todos los contenedores definidos en  docker-compose.yml.
- Importación de la base de datos plagas tal y como estaba el 23 de mayo de 2025.
El proyecto está formado por cinco contenedores:
1. MySQL (mysql).
Basado en la imagen oficial de mysql:latest este alberga el servidor mySQL donde se aloja la base de datos de plagas, en el volumen persistente mysql_data. Comparte el volumen backup para guardar o recuperar copias.
3. AutoMySQLBackup (automysqlbackup)
Basado en la imagen: selim13/automysqlbackup. realiza copias de seguridad automáticas de la base de datos y las almacena en el volumen persistente backup . Inicialmente programada una copia cada semana.
Depende del contenedor mysql.
3. ETL (cron_etl)
Contenedor con Python y cron. Ejecuta scripts diarios que descargan datos climáticos del SIAR y AEMET.
4. Predicción ML (cron_ml)
También con Python y cron. Ejecuta tareas de predicción diaria y reentrenamiento semanal del modelo.
6. Aplicación Flask (appdatoscarpo)
Permite introducir datos manuales y comprobar que los datos climáticos se cargaron bien.
Expone el puerto 5000.
