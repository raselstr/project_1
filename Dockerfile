# Menggunakan image Python sebagai base
FROM python:3.12.5-bullseye
# FROM python:3.12.5

ENV PYTHONBUFFERED=1

# Menentukan direktori kerja di dalam container
WORKDIR /project_1

# Menyalin file requirements.txt dan menginstal dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode proyek ke dalam container
COPY . /project_1/

# Menjalankan perintah untuk migrate dan collectstatic (opsional)
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Menentukan perintah default untuk menjalankan aplikasi Django
CMD ["gunicorn", "--bind", "0.0.0.0:5454", "project.wsgi:application"]
