FROM python:3.12.5-bullseye

WORKDIR /project_1

# Menyalin file requirements.txt dan menginstal dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode proyek ke dalam container
COPY . /project_1/

RUN python manage.py collectstatic --noinput
# RUN python manage.py migrate
# Menentukan perintah default untuk menjalankan aplikasi Django
CMD ["gunicorn", "--bind", "0.0.0.0:4500", "project.wsgi:application"]
