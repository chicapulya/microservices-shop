# Node 18 base image
FROM node:18-alpine

# Установка рабочей директории
WORKDIR /app

# Копирование package.json и package-lock.json
COPY package*.json ./

# Установка зависимостей
RUN npm install

# Копирование всего проекта
COPY . .

# Expose порт
EXPOSE 3000

# Команда запуска dev сервера
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
