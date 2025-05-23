    docker volume create mysql_data
    docker volume create backup
    docker network create miRed
    docker compose up -d
    ## Para Linux
    # Para que le de tiempo a arrancar al mySQL
    sleep 30
    docker exec -i mySqlDocker mysql -uroot -pcarpocapsa < dump.sql