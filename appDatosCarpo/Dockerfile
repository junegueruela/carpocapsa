FROM python:3.12.6-alpine3.20
WORKDIR /usr/src/app
# Copiar solo los archivos .py y los directorios templates y static
COPY *.py /usr/src/app/
COPY requirements.txt /usr/src/app/
COPY templates/ /usr/src/app/templates/
COPY static/ /usr/src/app/static/
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    mariadb-dev \
    libffi-dev \
    unixodbc \
    unixodbc-dev \
    build-base
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT python hello.py ## ENTRYPOINT es para gunicorn
# Expone el puerto 5000 para Flask, según chatgpt pongo lo de abajo en lugar de ENTRYPOINT
#EXPOSE 5000

# Comando para ejecutar la aplicación Flask
#CMD ["python", "hello.py"]