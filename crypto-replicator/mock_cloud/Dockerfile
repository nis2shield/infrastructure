# Mock Cloud Receiver
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask gunicorn

COPY app.py .

RUN mkdir -p /data/envelopes

# Non-root user
RUN useradd -r mockuser && chown -R mockuser:mockuser /app /data
USER mockuser

ENV PORT=8080

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
