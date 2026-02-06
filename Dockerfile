# Dockerfile
FROM python:3.12-bullseye

WORKDIR /project_1

COPY requirements.txt .
# Install dependencies sistem
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    netcat-openbsd \
    postgresql-client \
    python3-distutils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dan install
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua kode
COPY . /project_1/

# Pastikan skrip siap dijalankan
RUN chmod +x /project_1/wait_for_db.sh

# Jalankan collectstatic (opsional, tapi direkomendasikan)
RUN python manage.py collectstatic --noinput

# Entry point untuk menunggu DB
ENTRYPOINT ["/project_1/wait_for_db.sh"]

# Default CMD (web)
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "project.wsgi:application"]
