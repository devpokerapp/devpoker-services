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
