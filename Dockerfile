FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Запускаем uvicorn, указывая путь к приложению
# main:app = файл main.py, переменная app = FastAPI()
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]