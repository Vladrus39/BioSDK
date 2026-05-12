FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install --no-cache-dir -e .
ENV PYTHONUNBUFFERED=1
# Default: install from test.pypi.org and verify
CMD ["python", "-c", "import biosdk; print(f'BioSDK v{biosdk.__version__} ready. Adapters:', biosdk.list_adapters())"]
