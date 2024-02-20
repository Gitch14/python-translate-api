# Используем базовый образ Python
FROM python:3.7

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости в контейнер
COPY requirements.txt .

RUN apt-get update && apt-get -y install gcc

# Создаем и активируем виртуальное окружение
RUN python -m venv venv
RUN /bin/bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# Копируем исходный код приложения в контейнер
COPY . .

# Запускаем приложение
CMD ["python", "app.py"]
