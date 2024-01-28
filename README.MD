# Air quality monitor project API. 
## Project description:
Description goes here


### Local setup:
Following command pulls and runs postgres

`docker compose up airq_app_db -d`

After postgres is running, for migrations run:

`alembic upgrade heads`

To run application:

`cd app; uvicorn main:app`


Or

`docker compose build`

`docker compose up -d`

to run application inside docker. 