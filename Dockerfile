FROM python:3.11-slim

# Instalar LibreOffice y dependencias
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    fonts-liberation \
    fontconfig \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Instalar fuentes personalizadas si existen
RUN if [ -d "fonts" ] && [ "$(ls -A fonts)" ]; then \
    mkdir -p /usr/share/fonts/custom && \
    cp fonts/* /usr/share/fonts/custom/ && \
    fc-cache -f -v; \
    fi

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "2", "app:app"]
