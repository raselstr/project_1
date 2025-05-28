#!/bin/bash
set -e

echo "Menunggu database siap di $DATABASE_HOST:$DATABASE_PORT ..."

# Tunggu sampai database siap menggunakan pg_isready
until pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$POSTGRES_USER"; do
  echo "Database belum siap - menunggu 1 detik..."
  sleep 1
done

echo "Database sudah siap!"

python manage.py migrate --noinput

# Menjalankan perintah yang diteruskan dari CMD
exec "$@"
