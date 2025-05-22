FROM python:3.12-slim

ARG APP_CONTENT_DIR=.

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
COPY ${APP_CONTENT_DIR}/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir uvicorn

# Копируем весь проект
COPY ${APP_CONTENT_DIR} .

# Запускаем uvicorn, указывая путь к приложению
# main:app = файл main.py, переменная app = FastAPI()
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]