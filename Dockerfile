# Gunakan base image Python dengan versi terbaru dan stabil
FROM python:3.12.5-bullseye

# Set workdir
WORKDIR /project_1

# Menyalin file requirements.txt dan menginstal dependencies sistem
COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    netcat-openbsd \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Salin skrip wait_for_db.sh dan berikan izin eksekusi
# COPY wait_for_db.sh /wait_for_db.sh

# Menyalin seluruh kode proyek ke dalam container
COPY . /project_1/
RUN chmod +x /project_1/wait_for_db.sh

# Jalankan collectstatic setelah semua file tersedia
RUN python manage.py collectstatic --noinput


# Menentukan entrypoint untuk menunggu database siap
ENTRYPOINT ["/project_1/wait_for_db.sh"]

# Menentukan perintah default untuk menjalankan aplikasi Django
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "project.wsgi:application"]
