# Cactus Backend

Prueba tecnica basada en un gestor de tareas simple

## Requisitos

- Python 3.8+, en este caso se ha usado la 3.12
- Django 4.2.8
- Django REST Framework
- Django OAuth Toolkit (OAuth2)
- PostgreSQL
- Docker & Docker Compose
- Pytest

## Instalación y despliegue

1. **Clonar el repositorio:**
   ```sh
   git clone https://github.com/tuusuario/cactus_backend.git
   cd cactus_backend/taskmanager
   ```

2. **Configurar las variables de entorno:**
   Edita el archivo `settings.env` con tus credenciales y configuración de base de datos.
   En este caso aunque los archivos .env estan incluidos en el gitignore se ha subido el archivo de `settings.env` para que pueda ser usado para las pruebas y tenerlo como ejemplo.

3. **Construir y levantar los servicios:**
   ```sh
   docker-compose build
   docker-compose up -d
   ```

4. **Opcional: Aplicar migraciones y crear el superusuario:**
	En caso de empezar con una base de datos limpia deberiamos ejecutar las migraciones, crear el superuser y recolectar los estaticos, ademas de por supuesto acceder al /admin y crear la aplicacion Oauth2 para poder loguearse.
    Esto es opcional puesto que se ha subido la base de datos de pruba con todo ya configurado ademas de un backup de esta pero se pone para poder configurarla de cero si se quiere.
   ```sh
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   docker-compose exec web python manage.py collectstatic
   ```
   Para crear la aplicacion de Oauth2 accedemos a /admin como superuser que hayamos creado, en la base de datos de prueba es admin/admin, y creamos la aplicacion con los siguientes datos:
   ```
	Client type: Confidential
	Authorization grant type: Resource owner password-based
	Name: CactusApp
	```
	Debemos guardarnos el client_id y client_secret de la aplicacion para poder usarlos mas adelante.
5. **Opcional: Restaurar backup de la base de datos **
	En caso de que queramos restaurar los datos de prueba del proyeto en una base de datos nueva se puede hacer desde el archivo backup con los siguientes comando de docker segun estemos en linux o windows. 
	- **Linux:**
      ```sh
      docker exec -i taskmanager-db-1 psql -U cactus_user -d cactus_db < backup.sql
      ```
    - **Windows (PowerShell):**
      ```sh
      type backup.sql | docker exec -i taskmanager-db-1 psql -U cactus_user -d cactus_db
      ```

## Estructura del proyecto

```
taskmanager/
├── core/		  	# App principal del proyecto (registro, configuración)
├── tasks/			# App para el CRUD de tareas
├── pgdata/               	# Volumen de datos para el docker de PostgreSQL
├── backup.sql            	# Backup de la base de datos
├── docker-compose.yml
├── settings.env		# Archivo con las variables de entorno, solo añadido como ejemplo
├── manage.py
├── pytest.ini			# Archivo de configuracion de pytest
├── requirements.txt	  	# Archivo de librerias requeridas para el proyecto
├── Dockerfile
├── CactusBackend.postman_collection.json	  # Coleccion de endpoints de la api para postman
└── ...
```

## Principales endpoints
Estos son los principales endpoints con la especificacion de los parametros necesarios para poder lanzarlos. Todas las tareas solo se puede acceder a tareas que sean del propio usuario por lo que el token es requerido para todas las peticiones de tasks.

- POST `/api/register/` - Registro de usuario
	```
	POST /api/register/
	Body: { "username": "antonio", "password": "tu_password" }
	```
- POST `/o/token/` - Obtención de token OAuth2
	```
    POST /o/token/
    Body:
      grant_type=password
      username=antonio
      password=tu_password
      client_id=tu_client_id
      client_secret=tu_client_secret

	```
- POST `/o/token/` - Refrescar de token OAuth2
    ```
    POST /o/token/
    Body:
      grant_type=refresh_token
      refresh_token=tu_refresh_token
      client_id=tu_client_id
      client_secret=tu_client_secret

	```
- POST	`/api/tasks/`	Crear tarea
	```
	POST /api/tasks/
    Authorization: Bearer <access_token>
    Content-Type: application/json

    {
      "title": "Comprar café",
      "description": "Asegúrate que sea descafeinado"
    }

	```
- GET	`/api/tasks/`	Listar tareas propias
	```
	GET /api/tasks/
	Authorization: Bearer <access_token>

	```
- GET	`/api/tasks/<id>/`	Ver detalle de tarea propia
	```
    GET /api/tasks/1/
    Authorization: Bearer <access_token>

	```
- PUT	`/api/tasks/<id>/`	Actualizar tarea propia
	```
	PUT /api/tasks/1/
    Authorization: Bearer <access_token>
    Content-Type: application/json

    {
      "title": "Comprar café y pan",
      "description": "Que el café sea tostado natural"
    }

	```
- DELETE	`/api/tasks/<id>/`	Eliminar tarea propia
	```
	DELETE /api/tasks/1/
    Authorization: Bearer <access_token>

	```

## Ejecutar tests
Para ejecutar los tests hay que tener el docker del proyecto levantado y ejecutar el siguiente comando para lanzarlos con pytest

  ```sh
  docker-compose exec web pytest
  ```

##Documentacion
La documentacion aparte de este Readme, consiste en una documentacion interactiva generada por la propia api con swagger y una coleccion de endpoits exportada de postman para su uso. Se puede probar los endpoints facilmente desde la propia api usando los endpoints de swagger: 
- /api/docs/ → Interfaz Swagger

- /api/schema/ → Archivo JSON OpenAPI

El primero nos permitr ver todos los endpoints, sus parámetros, autenticación OAuth2, y probarlos directamente con el token. El segundo nos devuelve el archivo del esquema de la api en formato estandar de OpenAPI.

Asi mismo en el proyecto esta el archivo `CactusBackend.postman_collection.json` que contiene la colecion completa de endpoints de la api para su uso simplemente importandola desde postman. 

