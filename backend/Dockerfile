FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY backend ./backend
COPY src ./src
COPY data ./data
COPY integration ./integration

RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
