# Gunakan image dasar Python
FROM python:3.10-slim

# Install Rust dan Cargo (manajer paket Rust)
RUN apt-get update && apt-get install -y curl build-essential \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- -y \
    && export PATH="$HOME/.cargo/bin:$PATH"

# Set up lingkungan kerja aplikasi
WORKDIR /app

# Salin file requirements.txt dan install dependensi Python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Salin seluruh kode aplikasi ke dalam kontainer
COPY . /app

# Tentukan port yang digunakan oleh aplikasi
EXPOSE 5000

# Jalankan aplikasi (contoh dengan Flask)
CMD ["python", "appp.py"]
