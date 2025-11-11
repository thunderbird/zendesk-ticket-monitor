FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["spike-monitor", "run-once", "--config", "config.yaml"]
