# ---- Builder Stage ----
FROM python:3.9-slim AS builder

# Set the Python path
ENV PYTHONPATH=/usr/local/lib/python3.9/site-packages
ENV PATH=$PATH:/usr/local/bin

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Production Stage ----
FROM python:3.9-slim

WORKDIR /app

# Create a non-root user and group
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --no-create-home --disabled-password appuser

# Copy installed packages and app code
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY ./app /app

# Change the owner of the app directory
RUN chown -R appuser:appgroup /app

USER appuser

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
