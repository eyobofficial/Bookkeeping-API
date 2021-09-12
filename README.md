# Dukka Inc. REST API

## Prerequisites
* [Python 3.8](https://www.python.org/downloads/)
* [virtualenv](https://virtualenv.pypa.io/en/latest/index.html)
* [PostgreSQL 12.0](https://www.postgresql.org/download/)

## Optionals
* [Redis](https://redis.io/download)


## Project Setup
You can setup your local developement environment the following steps. Before you start, make sure to install the [virtualenv](https://virtualenv.pypa.io/en/latest/index.html) package to complete the steps.

Steps:
1. Clone this repository to your local machine.
2. From the root directory of the repository, create a virtualenv container and activate it. For more information on how to create & activate a virtualenv container, click [here](https://virtualenv.pypa.io/en/stable/user_guide.html).
3. Install the dependencies of the project by entering the following command:
```
$ pip install -r requirements.txt
```
4. Make sure your postgresql service up and running.
```
$ sudo service postgresql status
```
5. Login to your Postgres shell and create a database for the project.
6. In the root directory, you will find a file called `.env.example`. Copy it and rename to `.env`. These file will hold all your environmental varaiable that are needed by the project. Make sure to update it accordingly.
Note: For your local development environment, you could leave the `AWS S3` section as it is.
* `
7. Run the following commands to setup the database tables and initial data:
```
$ python manage.py migrate --no-input
$ python manage.py loaddata business_types
$ python manage.py defaultsuperuser
```

## Usage
1. Make sure, your virtualenv container is still activated.
2. Run the following command to start the development server.
```
$ python manage.py runserver 0.0.0.0:8000
```
3. Open a web browser and go to: http://localhost:8000/admin/
4. Using the credentials you created on the `.env` file, login to the admin dashboard.
