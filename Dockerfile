FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install --no-cache-dir -e .
ENV PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
CMD ["bash", "scripts/run_biogpu_v47_powerpc_smoke.sh"]
