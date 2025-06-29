#!/bin/bash
set -e

echo "Starting entrypoint script at $(date)"
echo "Waiting for Postgres..."
python - <<'EOF'
import os
import time
import psycopg2
from psycopg2 import OperationalError

timeout = 30
start_time = time.time()
while True:
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host='db',
            port='5432'
        )
        conn.close()
        print("Postgres is ready!")
        break
    except OperationalError:
        if time.time() - start_time > timeout:
            print("Error: Postgres not ready after {} seconds".format(timeout))
            exit(1)
        time.sleep(2)
EOF

# Wait for Redis to be ready
echo "Waiting for Redis..."
python - <<'EOF'
import os
import time
import redis
from redis import ConnectionError

timeout = 30
start_time = time.time()
while True:
    try:
        r = redis.Redis(host='redis', port=6379, decode_responses=True)
        r.ping()
        print("Redis is ready!")
        break
    except ConnectionError:
        if time.time() - start_time > timeout:
            print("Error: Redis not ready after {} seconds".format(timeout))
            exit(1)
        time.sleep(2)
EOF

# echo "Applying database migrations..."
# if ! python manage.py migrate; then
#     echo "Error: Database migrations failed"
#     exit 1
# fi
if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "Applying database migrations..."
  if ! python manage.py migrate; then
      echo "Error: Database migrations failed"
      exit 1
  fi
else
  echo "Skipping migrations for this container"
fi
# Optional: Collect static files (if needed)
# python manage.py collectstatic --no-input

exec "$@"