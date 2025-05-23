docker volume create mysql_data
docker volume create backup
docker network create miRed
docker compose up -d
## Para Windows
Get-Content .\dump.sql | docker exec -i mySqlDocker mysql -uroot -pcarpocapsa
