docker volume create mysql_data
docker volume create backup
docker network create miRed
docker compose up -d
## Para Windows
# Para que le de tiempo a arrancar al mySQL
Start-Sleep -Seconds 30
Get-Content .\dump.sql | docker exec -i mySqlDocker mysql -uroot -pcarpocapsa
