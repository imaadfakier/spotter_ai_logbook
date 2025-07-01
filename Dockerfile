FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static files (optional if using whitenoise or similar)
RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD gunicorn spotter_ai_trucker_logbook.wsgi:application --bind 0.0.0.0:8080
