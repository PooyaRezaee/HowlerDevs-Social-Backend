# Run manual
- config and setup postgresql, redis
- run web application
    - ```python manage.py migrate```
    - ```python manage.py runserver```


# Run just Webapplication by Dockerfile
build dockerfile and start container
```bash
docker build . -t "webapplication"
docker run --name web_application --rm -p 8000:8000 --env-file .env --network host -d webapplication
```



# Run Project by Docker
```bash
docker-compose up -d
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
