# Reto SysOps

Infraestructura AWS para procesar transacciones mediante una arquitectura de datos tipo **Medallion**, exponiendo los resultados mediante una API.

## Arquitectura

```text
Ingesta
   ↓
S3 Bronze
   ↓
AWS Glue
   ↓
S3 Silver (Parquet)
   ↓
Glue Data Catalog
   ↓
Athena
   ↓
FastAPI
   ↓
Docker → ECR → ECS Fargate → ALB
```

## Componentes

* **Terraform:** infraestructura como código.
* **S3:** almacenamiento Bronze/Silver/Gold.
* **AWS Glue:** transformación Bronze → Silver.
* **Glue Data Catalog:** catálogo de datos y particiones.
* **Athena:** consultas SQL sobre Parquet.
* **FastAPI:** API para consultar las transacciones.
* **Docker:** empaquetado de la API.
* **ECR:** almacenamiento de imágenes Docker.
* **ECS Fargate:** ejecución de la API.
* **ALB:** acceso HTTP a la API.
* **CloudWatch:** logs de la aplicación.
* **GitHub Actions:** CI/CD.

## Estructura

```text
reto_sysops/
├── api/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── etl/
│   └── glue/
│       └── bronze_to_silver.py
├── ingestion/
├── infra/
│   └── *.tf
├── .github/
│   └── workflows/
│       └── ci-cd.yml
└── .gitignore
```

## Despliegue de infraestructura

```bash
cd infra

terraform init
terraform validate
terraform plan
terraform apply
```

## ETL

El Job de Glue transforma los datos de:

```text
s3://<bucket>/bronze/
```

a:

```text
s3://<bucket>/silver/transactions/
```

Los datos Silver se almacenan en formato **Parquet** y se particionan por `status`.

## API

Endpoints principales:

```text
GET /health
GET /transactions
GET /transactions/summary
```

Ejemplo:

```bash
curl http://<ALB>/health
curl http://<ALB>/transactions
curl http://<ALB>/transactions/summary
```

## Athena

Ejemplo de consulta:

```sql
SELECT status, COUNT(*) AS total
FROM reto_sysops_dev_catalog.transactions
GROUP BY status
ORDER BY status;
```

Resultado actual:

```text
approved   14
rejected    6
```

## CI/CD

El workflow de GitHub Actions realiza:

```text
Push a main
   ↓
Tests
   ↓
Docker build
   ↓
Push a ECR
   ↓
Nueva Task Definition
   ↓
Deploy en ECS
```

La autenticación entre GitHub Actions y AWS se realiza mediante **OIDC**, evitando almacenar credenciales permanentes de AWS en GitHub.

## Estado

La solución está desplegada y funcionando en AWS:

* API accesible mediante ALB.
* ECS ejecutando la API.
* Glue ETL procesando los datos.
* Datos Silver disponibles en S3.
* Athena consultando las particiones.
* API consumiendo Athena correctamente.
* CI/CD preparado con GitHub Actions.

--
este proyceto fue realizado con la ayuda de un llm