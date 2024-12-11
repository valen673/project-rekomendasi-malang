# Gunakan Python 3.10 atau versi terbaru yang kompatibel
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Salin file requirements.txt ke dalam container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Salin kode aplikasi Anda ke dalam container
COPY . /app/

# Expose port yang digunakan aplikasi Anda
EXPOSE 5000

# Jalankan aplikasi menggunakan Flask
CMD ["python", "appp.py"]
