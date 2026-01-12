FROM python:3.11

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "bot:app", "--host", "0.0.0.0", "--port", "8000"]
