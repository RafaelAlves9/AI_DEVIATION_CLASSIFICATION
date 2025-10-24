# Dockerfile otimizado para Deviation Classifier API
# Multi-stage build para imagem menor

# Stage 1: Base com dependências do sistema
FROM python:3.11-slim as base

# Instala dependências do sistema (ffmpeg necessário para Whisper)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Stage 2: Builder - instala dependências Python
FROM base as builder

# Copia requirements e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 3: Runtime - imagem final
FROM base as runtime

# Copia dependências Python instaladas do builder
COPY --from=builder /root/.local /root/.local

# Adiciona .local/bin ao PATH
ENV PATH=/root/.local/bin:$PATH

# Copia código da aplicação
COPY . .

# Cria diretório para logs
RUN mkdir -p logs

# Baixa modelo Whisper (para evitar download em runtime)
# Descomente se quiser embedar o modelo na imagem
# RUN python -c "import whisper; whisper.load_model('medium')"

# Expõe porta
EXPOSE 8000

# Variáveis de ambiente default
ENV PYTHONUNBUFFERED=1
ENV DEBUG=false

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Comando para executar a aplicação
CMD ["python", "app.py"]
