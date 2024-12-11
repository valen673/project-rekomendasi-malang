# Gunakan image base Rust
FROM rust:1.68-slim AS builder

# Gunakan Python 3.10
FROM python:3.10-slim

# Install dependencies lainnya
RUN apt-get update && apt-get install -y build-essential curl && apt-get clean

# Set working directory
WORKDIR /app

# Salin file requirements.txt ke dalam container
COPY requirements.txt /app/

# Install dependencies Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Salin kode aplikasi Anda ke dalam container
COPY . /app/

# Expose port yang digunakan aplikasi Anda
EXPOSE 5000

# Jalankan aplikasi menggunakan Flask
CMD ["python", "appp.py"]  # Ganti dengan nama file aplikasi yang benar
