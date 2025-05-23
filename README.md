# Run Project by Docker
```bash
# just docker file
docker build . -t "webapplication"
docker run --name web_application --env-file .env --network host -d webapplication
# all services in development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
# all services in production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

# Useful commands
#### See std-out web application
```bash
docker logs web_application
``` 
#### Enter to shell WebApplication
```bash
docker exec -it web_application bash
```
#### Exec migration on docker container
```bash
docker exec web_application python manage.py migrate
```
#### Add new superuser
```bash
docker exec -it web_application python manage.py createsuperuser
```
#### Database shell
```bash
docker exec -it django-social-db-1 psql -U user -d social
```

# Need postgres command: CREATE EXTENSION pg_trgm;