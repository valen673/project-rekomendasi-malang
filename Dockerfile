# Gunakan Python 3.10 atau versi yang kompatibel
FROM python:3.10-slim

# Install Rust dan dependencies lainnya
RUN apt-get update && \
    apt-get install -y curl build-essential && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    # Pastikan Rust ditambahkan ke PATH
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc && \
    apt-get clean

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
