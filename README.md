# Toros Manager on Apache Airflow

Early prototype for the TOROS Manager using [Apache Airflow](https://airflow.apache.org) pipeline framework.
This only shows the pipeline concept.

# Installation

**Prerequisites:**

 - git (you probably have it installed already)
 - [Docker](https://www.docker.com)

Clone it locally:

    git clone https://github.com/toros-astro/torosairflow
    cd torosairflow

The first time you set it up, you have to run the initdb container while running postgres container
in a different console.

In one terminal window type:

    docker-compose up postgres

and wait for it to finish set up.

In a second terminal (check you're still in the `torosairflow` directory) type:

    docker-compose up initdb

Once initdb exits cleanly, you can stop the postgres container of the previous step.

From now on, to run the pipeline simpy type:

    docker-compose up

The webserver shold be running in [http://localhost:8080](http://localhost:8080).

***

(c) TOROS Dev Team
