# Project url
https://github.com/lazgut/Auth_sprint_2

# Api Documentation

After starting the project, you will have access to the project documentation: [localhost:8080/apidocs]( http://localhost:8080/apidocs)

# Installation

The project permanent address: https://github.com/dondublon/Auth_sprint_1

(Optional) Use `flask -A cli.app create-superuser admin` shell command to create admin user.

# Development

## Run auth app in dev mode

Copy `.env.sample` to `.env`. Set `DOCKER_USER_ID` and `DOCKER_GROUP_ID` variables in `.env` files to your local uid and gid to have correct file permissions and create migrations from the container. Execute `docker-compose up` to run in dev mode or `docker-compose up -f docker-compose.yml` to use production ready setup. The application will be available at [http://127.0.0.1:8080/](http://127.0.0.1:8080/)

## DB migrations

Use **flask-migrate** extension to handle db migrations. Run `flask db upgrade` to apply the latest migrations to your db.

## Code style enforcement

Install [pre-commit](https://pypi.org/project/pre-commit/) python package to your environment (it is intentionally absent in requirements.txt) and run `pre-commit install` to install pre commit git hooks and check your code automatically before it's commited. It's handy to run `pre-commit` manually while working on code style issues or even use separate linting tools from `.pre-commit-config.yaml` eg. like *black* -  `black --skip-string-normalization` - to fix codestyle issues automatically.

## Running functional tests

Change your current directory to **tests/functional** then copy **.env.sample** to **.env** and execute `docker-compose up tests --no-log-prefix` to run tests.

## Naming conventions
Use **Data** postfix (eg. `UserData`) for marshmallow schema classes to use a feature of automatic sqlachemy objects serialization. It allows return sqlalchemy objects from flask view functions and also use them in **make_response** function.

## Request tracing
Jaeger tracing solution is available at [http://127.0.0.1:16686](http://127.0.0.1:16686)

## Rate limiting
Use [Flask-limiter configuration values](https://flask-limiter.readthedocs.io/en/stable/configuration.html#RATELIMIT_DEFAULT) to fine tune rate limiting.

## Test OAuth
- Get your dev access token following [this instruction](https://yandex.ru/dev/id/doc/dg/oauth/tasks/get-oauth-token.html)
- Send POST request to `http://localhost:8080/v1/oauth/login` with your access token as payload `{"access_token": "y0_AgAAAABasdfsdm4AAjj_wAAAADXUXR96IV2NrNGTua7hE7wkvvf2iewewe"}`
- Your will be registered as auth api user and get auth api credentials as result!
