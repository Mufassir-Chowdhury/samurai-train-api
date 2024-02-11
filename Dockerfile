FROM python:3.11.5-slim-bookworm

WORKDIR /code

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_NAME=database.db

RUN python reset_db.py

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]