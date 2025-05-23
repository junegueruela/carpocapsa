    docker volume create mysql_data
    docker volume create backup
    docker network create miRed
    docker compose up -d
    ## Para Linux
    docker exec -i mySqlDocker mysql -uroot -pcarpocapsa < dump.sql