# Usar Alpine como base
FROM python:3.12.6-alpine3.20

# Instalar Python y cron
RUN apk update && apk add --no-cache python3 py3-pip bash curl openrc
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    mariadb-dev \
    libffi-dev \
    unixodbc \
    unixodbc-dev \
    build-base

# Crear el directorio para la app y copiar los archivos
WORKDIR /usr/src/app/
COPY *.py /usr/src/app/
COPY *.sh /usr/src/app/
COPY requirements.txt /usr/src/app/
COPY root /etc/crontabs/

RUN pip install --no-cache-dir -r requirements.txt

# Me aseguro de que los permisos son correctos
RUN chmod 0644 /etc/crontabs/root
RUN chmod 0755 /usr/src/app/*.sh
# Iniciar crond en primer plano
CMD ["crond", "-f"]
