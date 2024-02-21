# Используем базовый образ Python
FROM python:3.12

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

# Запускаем приложение
CMD ["python", "./app.py"]
