## Gitjob Internal Api
![ci-workflow](https://github.com/GitjobTeam/gitjob-api/actions/workflows/main.yml/badge.svg)
![ci-dev-workflow](https://github.com/GitjobTeam/gitjob-api/actions/workflows/dev.yml/badge.svg)
![pytest-workflow](https://github.com/GitjobTeam/gitjob-api/actions/workflows/pytest.yml/badge.svg)
![availability](https://img.shields.io/website?url=http%3A%2F%2F172.86.66.189%3A8069%2Fdocs&label=dev-api)

### Usage
* use poetry for dependency management
* use uvicorn to run `uvicorn app.main:app --host 0.0.0.0`
* use `/docs` route for fastapi docs
#### Docker
* `docker build --tag registry.gitjob.com/gitjob-api:latest --target production-image .`
* easy way, using .env file
`docker compose up`
* manual docker run with specifying environment variables by hand
`docker run -e "API_TOKEN=..." -e "DB_HOST=..." ... registry.gitjob.com/gitjob-api:latest`

#### Environment
Can be setted through .env file, or directly through environment
* `API_TOKEN` - any string which will be used as bearer token for auth
* `DB_HOST` - db host without schema
* `DB_PORT` - port
* `DB_NAME` - db name
* `DB_USERNAME` - db username
* `DB_PASS` - db user password


### Project structure

`app/schemas/` contains Pydantic models. These can be used both to validate the data incoming within API requests, and to define structure
for data returned from API endpoints.

pydantic will try to coalesce the incoming data into the type
defined on the model. E.g., if an integer field is defined on the model like so: `age: int`, pydantic will try to convert strings in payload into

`app/models` defines the ORM models used to interface, mapping data in the database into python classes

`app/repository` encapsulates low-level helper methods for working with ORM objects in database

`app/services` defines higher-level CRUD methods, which can contain business logic specific to particular ORM models

`app/routers` contains FastAPI router definitions. These are responsible for mapping HTTP requests to the appropriate service methods

`app/db.py` and `app/dependencies.py` define database connector and API-level utils correspondingly

`app/main.py` is the entry point to the API, that loads the routers and starts the application service.

API-level exception handlers can also be defined here to return custom error messages to the clients

**FastAPI** is used to host API. It automatically generates OpenAPI specification for the endpoints from
pyantic models, which can be viewed at e.g. 0.0.0.0:8080/docs

![Layer diagram for the API service](/docs/layers.png)
