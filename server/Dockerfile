FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=frontend /frontend/static/app.js /app/frontend/static/app.js
RUN python manage.py collectstatic --noinput && mkdir -p /data && chmod 777 /data
USER 1001
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_catalogue && gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 90 djangoproj.wsgi:application"]
