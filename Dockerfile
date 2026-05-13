# BioSDK v4.3 — Production Docker Image
# BioReservoir + BioCompute OS + Dashboard
#
# Build:
#   docker build -t biosdk:v4.3 .
#
# Run (dashboard on :8420):
#   docker run -p 8420:8420 biosdk:v4.3
#
# Run (CLI mode):
#   docker run --rm biosdk:v4.3 biosdk version
#
# Run (with data volume):
#   docker run -p 8420:8420 -v ./data:/app/data -v ./outputs:/app/outputs biosdk:v4.3

FROM python:3.13-slim

LABEL org.opencontainers.image.title="BioSDK"
LABEL org.opencontainers.image.description="Vendor-Neutral Neural Data Library with BioReservoir (Izhikevich + STDP)"
LABEL org.opencontainers.image.version="v4.3"
LABEL org.opencontainers.image.source="https://github.com/Vladrus39/BioSDK"

# ── System dependencies ──────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ──────────────────────────────────────────────
WORKDIR /app

# Install core dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Install Numba for GPU/Izhikevich acceleration
RUN pip install --no-cache-dir numba>=0.65.0

# Optional: install dashboard dependencies
RUN pip install --no-cache-dir fastapi>=0.100 uvicorn[standard]>=0.23

# ── Application ──────────────────────────────────────────────────────
COPY . .
RUN pip install --no-cache-dir .

# ── Runtime ──────────────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1
ENV BIOSDK_SIGNING_KEY="biosdk-docker-v4.3"
ENV PYTHONPATH="/app:${PYTHONPATH}"

EXPOSE 8420

# Health check: verify imports work
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import biosdk; print(f'v{biosdk.__version__}')" || exit 1

# Default: start dashboard + OS
CMD ["python", "-m", "biogpu.dashboard.server_v40"]
