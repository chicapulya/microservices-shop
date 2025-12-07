# Python 3.11 base image
FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Копирование requirements.txt
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего проекта
COPY . .

# Создание директории для базы данных
RUN mkdir -p /app/db

# Expose порт
EXPOSE 8004

# Команда запуска (будет переопределена в docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8004"]
