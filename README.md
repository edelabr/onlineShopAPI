# onlineShopAPI

Interfaz diseñada para facilitar la integración y gestión de tiendas en línea.

---

## Tecnologías Usadas

- **[FastAPI](https://fastapi.tiangolo.com/)**: Framework para construir APIs rápidas y modernas con Python.
- **[SQLModel](https://sqlmodel.tiangolo.com/)**: Biblioteca para trabajar con bases de datos SQL y modelos Pydantic.
- **[PostgreSQL](https://www.postgresql.org/)**: Base de datos relacional robusta y escalable.
- **[Uvicorn](https://www.uvicorn.org/)**: Servidor ASGI para ejecutar la aplicación FastAPI.
- **[DummyJSON](https://dummyjson.com/)**: API gratuita sin autenticación para obtener datos de productos.
- **[Pandas](https://pandas.pydata.org/)**: Herramienta poderosa para análisis, transformación y exportación de datos.
- **[XlsxWriter](https://xlsxwriter.readthedocs.io/)**: Librería para crear archivos Excel (.xlsx) con múltiples opciones de formato.
- **[Jinja2](https://jinja.palletsprojects.com/)**: Motor de plantillas para generar HTML dinámico usado en la generación de PDFs.
- **[xhtml2pdf](https://xhtml2pdf.readthedocs.io/)**: Herramienta que convierte HTML y CSS básicos a archivos PDF.
- **[Python-JOSE](https://python-jose.readthedocs.io/)**: Biblioteca para manejar JWT.
- **[Bcrypt](https://pypi.org/project/bcrypt/)**: Biblioteca para hashear y verificar contraseñas.
- **[Redis](https://redis.io/docs/latest/develop/clients/redis-py/)**: Almacén de datos en memoria para gestionar tokens JWT revocados.
- **[python-dotenv](https://pypi.org/project/python-dotenv/)**: Carga variables de entorno desde archivos `.env` para mantener claves y configuraciones fuera del código fuente.

## Estructura de Carpetas

```
app/
├── auth/
│   ├── dependencies.py           # Dependencias para autenticación y roles
│   ├── hashing.py                # Funciones para hashear y verificar contraseñas
│   └── jwt.py                    # Funciones para manejo de JWT
├── clients/
│   └── dummy_json_client.py      # Operaciones CRUD para TaskStatus
├── db/
│   ├── database.py               # Configuración de la base de datos postgres
│   └── redis_client.py           # Configuración de la base de datos redis
├── models/
│   ├── order.py                  # Modelo Order con SQLModel
│   └── user.py                   # Modelo User con SQLModel
├── routes/
│   ├── auth.py                   # Endpoints relacionados con autenticación
│   ├── order.py                  # Endpoints relacionados con Orders
│   ├── product.py                # Endpoints relacionados con Products
│   └── user.py                   # Endpoints relacionados con User
├── services/
│   ├── order.py                  # Lógica de negocio relacionada con Orders
│   └── user.py                   # Lógica de negocio relacionada con Users
├── templates/
│   └── pdf_template_orders.html  # Plantilla de Orders en HTML para exportarlo a PDF
├── utils/
│   └── report_generator.py       # Funciones para exportar los Orders en diferentes formatos como Excel, PDF y CSV
├── .env                          # Variables de entorno para configuración local y Docker
├── .gitignore                    # Lista de archivos y carpetas que Git debe ignorar
├── docker-compose.yml            # Archivo Docker Compose para orquestar los servicios
├── Dockerfile                    # Archivo Docker para construir la imagen de la aplicación
├── logging.conf                  # Configuración del sistema de logging de la aplicación
├── main.py                       # Punto de entrada principal de la aplicación
├── seeder.py                     # Script para poblar la base de datos con datos iniciales
├── requirements.txt              # Lista de dependencias necesarias para la aplicación
└── README.md                     # Documentación del proyecto
```

## Configuración del Proyecto

### Variables de Entorno

El proyecto utiliza un único archivo `.env` para configuraciones tanto locales como en Docker.

Ejemplo de `.env`:

```properties
# Detectar si estamos dentro de Docker
IN_DOCKER=false

# ========================
# DATABASE CONFIGURATION
# ========================
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432
DB_NAME=mydatabase

# ========================
# REDIS CONFIGURATION
# ========================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# ========================
# JWT CONFIGURATION
# ========================
SECRET_KEY=your_secret_key_here
REFRESH_SECRET_KEY=your_refresh_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
REVOKED_TOKENS_FILE=/revoked_tokens.json
```

### Cómo Ejecutar el Proyecto

#### 1. **Ejecutar Localmente**

1. **Crear un entorno virtual**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. **Instalar dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar la base de datos**:

   - Asegúrate de que PostgreSQL esté instalado y ejecutándose. Crea la base de datos especificada en el archivo `.env` y asegurate que la variable IN_DOCKER está a false.
   - **Nota:** si lo necesitas puedes correr el servicio de db incluido en el fichero docker-compose.yml

4. **Ejecutar el seeder**:
   Si deseas poblar la base de datos con datos iniciales, ejecuta:

   ```bash
   python seeder.py
   ```

5. **Ejecutar la aplicación**:

   ```bash
   python main.py
   ```

6. **Abrir la documentación interactiva**:
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

#### 2. **Ejecución con Docker**

### Requisitos

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- Variable IN_DOCKER del archivo `.env` en true

### Pasos para Ejecutar

1. **Construir y levantar los servicios**:

   ```bash
   docker-compose up --build -d
   ```

2. **Acceder a la aplicación**:

   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

3. **Parar los servicios**:
   ```bash
   docker-compose down
   ```

### Cómo Ejecutar el Seeder

Si deseas poblar la base de datos con datos iniciales, puedes ejecutar el script `seeder.py` de las siguientes maneras:

#### Localmente

1. Asegúrate de que la base de datos esté configurada y en ejecución.
2. Ejecuta el siguiente comando:
   ```bash
   python seeder.py
   ```

#### Con Docker

1. Asegúrate de que los servicios estén levantados con Docker Compose:

   ```bash
   docker-compose up -d
   ```

2. Ejecuta el seeder dentro del contenedor de la aplicación:
   ```bash
   docker-compose run --rm api python seeder.py
   ```

Esto poblará la base de datos con los datos iniciales definidos en el script `seeder.py`.

### Notas

- Los datos de la base de datos se almacenan en un volumen llamado `postgres_data`, por lo que no se perderán al reiniciar los contenedores.
- Puedes modificar las variables de entorno en el archivo `.env` según sea necesario.

## Funcionalidades

### Sistema de Roles y Autenticación con JWT

Este proyecto incluye un sistema de autenticación basado en JWT (JSON Web Tokens) y roles (`admin` y `customer`). A continuación, se explica cómo usarlo:

#### Roles

1. **Admin**

   - Permisos: Acceso completo a todos los endpoints (`GET`, `POST`, `PUT`, `DELETE`).

2. **Customer**

   - Permisos: Acceso restringido a endpoints que devuelvan datos del mismo usuario (`GET`, `POST`, `PUT`, `DELETE`) en `/users`, `/orders` y `/products`.

#### Protección de Rutas

- Todas las rutas `GET`, `POST`, `PUT` y `DELETE` de los módulos `order` y `user` están protegidas con JWT. Solo los usuarios con rol de `admin` o `customer` pueden acceder a estas rutas.

#### Registro de Usuarios

Para registrar un nuevo usuario, utiliza el endpoint `/api/auth/register`. Este endpoint espera un objeto JSON con los campos `username`, `email`, `password` y opcionalmente `role` (por defecto es `customer`).

#### Inicio de Sesión

Para iniciar sesión y obtener un token JWT, utiliza el endpoint `/api/auth/login`. Este endpoint espera los campos `username` y `password`.

- Tiempo de expiración del token: 15 minutos.

#### Renovación de Tokens

El endpoint `/api/auth/refresh` permite obtener un nuevo `access_token` utilizando un `refresh_token` válido.

#### Cierre de Sesión

El endpoint `/api/auth/logout` permite cerrar sesión y revocar el token de acceso. Los tokens revocados se almacenan en Redis y adicionalmente en un archivo llamado `revoked_tokens.txt` para evitar su reutilización. Este archivo se encuentra en la raíz del proyecto y se carga al iniciar la aplicación.

---

### Recuperación de Contraseña

El proyecto incluye un flujo para la recuperación de contraseñas:

1. **Solicitar recuperación**:

   - Endpoint: `/api/auth/forgot-password`
   - Método: `POST`
   - Envía un token de recuperación al cliente.
   - Tiempo de expiración del token: 15 minutos.

2. **Restablecer contraseña**:
   - Endpoint: `/api/auth/reset-password`
   - Método: `POST`
   - Permite al usuario establecer una nueva contraseña utilizando el token de recuperación.

---

### Notas Adicionales

- **Excepciones**:
  - Manejo global de excepciones para errores inesperados.

---
