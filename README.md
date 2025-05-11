# Project Setup Guide

This guide will walk you through setting up the project by cloning it from GitHub, setting up the environment, and running the necessary services.

## Prerequisites

- Docker
- Docker Desktop (for running Redis)
- Python (3.12.10)
- `uv` (Python package manager)

## Step 1: Clone the Repository

First, clone the repository from GitHub:

```sh
git clone <repository-url>
cd <repository-directory>
```

## Step 2: Set Up the Virtual Environment

Use `uv` to create a virtual environment and install the dependencies:

```sh
uv venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

## Step 3: Install Dependencies

Install the required Python packages using `uv`:

```sh
uv pip install -r requirements.txt
```

## Step 4: Set Up the Environment File

Create a `.env` file in the root directory of the project and add the necessary environment variables. Here is an example `.env` file:

```env
SECRET_KEY=""

DB_ENGINE=""
DB_NAME=""
DB_USER=""
DB_PASSWORD=""
DB_HOST=""
DB_PORT=""
DB_OPTIONS={}


LOG_LEVEL=""
LOG_FILE=""
LOG_FORMAT =""
LOG_DATE_FORMAT =""
MAX_LOG_FILE_SIZE=""
LOG_BACKUP_COUNT=""
```

## Step 5: Set Up PostgreSQL

Ensure you have PostgreSQL installed and running. You can install it using your package manager or download it from the [official PostgreSQL website](https://www.postgresql.org/download/).

Create a database and user for your Django project:

```sh
sudo -u postgres psql
CREATE DATABASE your-db-name;
CREATE USER your-db-user WITH PASSWORD 'your-db-password';
ALTER ROLE your-db-user SET client_encoding TO 'utf8';
ALTER ROLE your-db-user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your-db-user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE your-db-name TO your-db-user;
```

## Step 6: Set Up Redis with Docker

Run Redis using Docker:

```sh
docker run --name my-redis -p 6379:6379 -d redis
```

## Step 7: Run Migrations

Apply the database migrations:

```sh
python manage.py migrate
```

## Step 8: Run the Development Server

Start the Django development server:

```sh
python manage.py runserver
```

## Step 9: Verify the Setup

Open your web browser and navigate to `http://127.0.0.1:8000/healthcheck/` to verify that the Django project is running correctly.

## Troubleshooting

- **Docker Issues**: Ensure Docker Desktop is running and the Redis container is started.
- **Database Connection Issues**: Verify the database credentials in the `.env` file and ensure PostgreSQL is running.
- **Dependency Issues**: Ensure all dependencies are installed correctly using `uv`.

## Conclusion

You should now have the project set up and running with Redis, PostgreSQL, and all necessary dependencies.
```