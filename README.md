# DevPoker Services

> Collection of backend services used by the DevPoker web platform

## Running

```bash
docker-compose -f docker/docker-compose.yml up --build -d
```

or run individually

```bash
docker-compose -f docker/docker-compose.yml up -d rabbitmq
docker-compose -f docker/docker-compose.yml up --build estimate
```

## Database

To setup you must create the databases. Start by acessing the postgres shell:

```bash
docker-compose -f docker/docker-compose.yml up -d db
docker exec -it devpoker-db psql -U postgres
```

Then run:

```sql
CREATE DATABASE estimate;
CREATE DATABASE keycloak WITH ENCODING 'UTF8';
```
