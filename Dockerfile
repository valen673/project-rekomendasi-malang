# Gunakan Python 3.10 atau versi yang kompatibel
FROM python:3.10-slim

# Install dependencies yang diperlukan, termasuk curl dan build-essential
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    && apt-get clean

# Install Rust secara eksplisit
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    export PATH="$HOME/.cargo/bin:$PATH" && \
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> /etc/profile.d/rust.sh

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
